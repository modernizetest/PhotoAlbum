#!/usr/bin/env python3
"""endpoint-model-sa.py - forced static-analysis driver for Step 3a (composite scenarios).

Single self-contained file (no package imports) so it ships cleanly through the skill
bundle. It runs IBM CLDK `codeanalyzer` over the module and builds a framework-neutral
endpoint model (the SA skeleton: 8-tuple endpoints + DTO schemas + deterministic resource
dependency edges + auth model). This is the MANDATORY static-analysis foundation the
cross-endpoint scenarios are grounded in - it is never simulated by reading the source by
hand.

Vendored from the weakened-SAINT pipeline (arXiv:2511.13305v2, Phase-1 model construction):
the LLM client, request/scenario generation, and Stage 2b semantic enrichment are dropped.
Stage 2b (Object Dependency Graph semantic edges, inter-parameter dependencies, value
constraints) is performed by the migration agent and then re-checked deterministically by
this same tool in `--validate` mode.

Usage:
  python endpoint-model-sa.py build <module-path> <out.json>
      Run codeanalyzer + build the SA skeleton, write <out.json>. Exit codes:
        0  model written (>=1 endpoint)
        2  no supported web framework detected (skip Step 3a for this module)
        3  codeanalyzer could not run (missing jar / JDK / WSL) - forced SA failed
        4  codeanalyzer ran but produced no usable symbol table

  python endpoint-model-sa.py validate <out.json>
      Re-validate an agent-enriched endpoint-model.json against the schema + invariants
      (producer-consumer / database edges must be agent-added, IPD categories must be
      from the fixed catalog, ODG nodes must equal endpoint ids, ...). Exit codes:
        0  valid
        1  schema or invariant violation (message on stderr)

Environment:
  SAINT_CODEANALYZER_JAR   explicit path to the codeanalyzer jar (overrides cldk discovery)
  SAINT_WSL_DISTRO         WSL distro to use on Windows (codeanalyzer runs under WSL there)
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # Gate-1 is best-effort: invariants (Gate-2) always run with stdlib only.
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None  # type: ignore


# =========================================================================== #
# Config: codeanalyzer discovery + WSL helpers
# =========================================================================== #

def _log(msg: str) -> None:
    print(f"[endpoint-model-sa] {msg}", file=sys.stderr)


def discover_codeanalyzer_jar() -> Path | None:
    """Best-effort discovery of the IBM CLDK codeanalyzer jar shipped with cldk."""
    env = os.environ.get("SAINT_CODEANALYZER_JAR")
    if env:
        p = Path(env)
        return p if p.exists() else None
    candidates: list[Path] = []
    try:
        import cldk  # type: ignore

        base = Path(cldk.__file__).parent / "analysis" / "java" / "codeanalyzer" / "jar"
        if base.is_dir():
            candidates.extend(sorted(base.glob("codeanalyzer-*.jar")))
    except Exception:
        pass
    return candidates[-1] if candidates else None


def to_wsl_path(p: str | os.PathLike) -> str:
    """Convert a Windows path (C:\\x\\y) to a WSL mount path (/mnt/c/x/y)."""
    s = str(p).replace("\\", "/")
    if len(s) >= 2 and s[1] == ":":
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def _has_wsl() -> bool:
    return platform.system() == "Windows" and shutil.which("wsl") is not None


# =========================================================================== #
# Stage 1: run codeanalyzer (symbol-table level)
# =========================================================================== #

class SaError(RuntimeError):
    pass


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def _wsl_script(jar_wsl: str, in_wsl: str, out_wsl: str) -> str:
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'JAR="{jar_wsl}"\n'
        f'IN="{in_wsl}"\n'
        f'OUT="{out_wsl}"\n'
        'mkdir -p "$OUT"\n'
        'java -jar "$JAR" -i "$IN" --analysis-level=1 -o "$OUT" 2>&1 | tail -n 40\n'
    )


def run_codeanalyzer(module_path: Path, work_dir: Path) -> dict[str, Any]:
    """Run codeanalyzer and return the parsed analysis.json document.

    On Windows the codeanalyzer jar crashes compiling its default exclude regex on
    Windows-style paths, so it is run under WSL where paths use '/'.
    """
    jar = discover_codeanalyzer_jar()
    if jar is None:
        raise SaError(
            "codeanalyzer jar not found. Install it with `pip install cldk` or set "
            "SAINT_CODEANALYZER_JAR to the jar path."
        )
    work_dir.mkdir(parents=True, exist_ok=True)
    is_windows = platform.system() == "Windows"

    if is_windows:
        if not _has_wsl():
            raise SaError(
                "On Windows, codeanalyzer must run under WSL (its default exclude regex is "
                "invalid on Windows paths), but `wsl` was not found on PATH."
            )
        script = _wsl_script(to_wsl_path(jar), to_wsl_path(module_path), to_wsl_path(work_dir))
        sh_path = work_dir / "_run_codeanalyzer.sh"
        sh_path.write_text(script, encoding="utf-8", newline="\n")
        cmd = ["wsl"]
        distro = os.environ.get("SAINT_WSL_DISTRO")
        if distro:
            cmd += ["-d", distro]
        cmd += ["bash", to_wsl_path(sh_path)]
        proc = _run(cmd)
    else:
        java = shutil.which("java")
        if java is None:
            raise SaError("java not found on PATH (a JDK is required to run codeanalyzer).")
        cmd = [
            java, "-jar", str(jar),
            "-i", str(module_path),
            "--analysis-level=1",
            "-o", str(work_dir),
        ]
        proc = _run(cmd)

    out_json = work_dir / "analysis.json"
    if not out_json.exists():
        raise SaError(
            "codeanalyzer did not produce analysis.json.\n"
            f"exit={proc.returncode}\nstdout/stderr:\n{proc.stdout}\n{proc.stderr}"
        )
    doc = json.loads(out_json.read_text(encoding="utf-8"))
    _check_analysis_invariants(doc)
    return doc


# =========================================================================== #
# Symbol-table view objects + annotation helpers
# =========================================================================== #

class ClassInfo:
    def __init__(self, qualified_name: str, decl: dict[str, Any], package: str | None, file: str):
        self.qualified_name = qualified_name
        self.decl = decl
        self.package = package
        self.file = file

    @property
    def annotations(self) -> list[str]:
        return self.decl.get("annotations", []) or []

    @property
    def annotation_names(self) -> list[str]:
        return [ann_name(a) for a in self.annotations]

    def methods(self) -> dict[str, dict[str, Any]]:
        return self.decl.get("callable_declarations", {}) or {}

    def fields(self) -> list[dict[str, Any]]:
        return self.decl.get("field_declarations", []) or []

    @property
    def simple_name(self) -> str:
        return self.qualified_name.split(".")[-1]


class ModelContext:
    def __init__(self) -> None:
        self.classes: dict[str, ClassInfo] = {}


def ann_name(a: str) -> str:
    m = re.match(r"@([A-Za-z0-9_.]+)", a.strip())
    return m.group(1).split(".")[-1] if m else a


def ann_args(a: str) -> str:
    m = re.search(r"\((.*)\)\s*$", a.strip(), re.S)
    return m.group(1).strip() if m else ""


def find_annotation(annotations: list[str], *names: str) -> str | None:
    wanted = set(names)
    for a in annotations:
        if ann_name(a) in wanted:
            return a
    return None


def extract_paths(args: str) -> list[str]:
    """Pull URL path string(s) out of a mapping annotation's argument text."""
    if not args:
        return [""]
    val = re.search(r'(?:value|path)\s*=\s*(\{[^}]*\}|"[^"]*")', args)
    if val:
        return re.findall(r'"([^"]*)"', val.group(1)) or [""]
    first = re.match(r'\s*(\{[^}]*\}|"[^"]*")', args)
    if first:
        return re.findall(r'"([^"]*)"', first.group(1)) or [""]
    return [""]


def join_path(base: str, sub: str) -> str:
    if not base and not sub:
        return "/"
    b = (base or "").strip("/")
    s = (sub or "").strip("/")
    parts = [p for p in (b, s) if p]
    return "/" + "/".join(parts)


_JDK_PREFIXES = ("java.", "javax.", "jakarta.", "org.springframework.", "io.micronaut.")


def is_project_type(type_name: str | None, ctx: ModelContext) -> bool:
    """A non-JDK, non-framework type that the project itself declares."""
    if not type_name:
        return False
    base = re.sub(r"<.*?>", "", type_name).strip()
    if base in ctx.classes:
        return True
    return not base.startswith(_JDK_PREFIXES) and "." in base


def make_param(
    *,
    name: str | None,
    ptype: str | None,
    kind: str,
    annotations: list[str] | None = None,
    enclosing_method: str | None = None,
    enclosing_class: str | None = None,
    provenance: str = "SA",
    value_constraints: list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "type": ptype,
        "kind": kind,
        "valueConstraints": value_constraints or [],
        "enclosingMethod": enclosing_method,
        "enclosingClass": enclosing_class,
        "annotations": annotations or [],
        "provenance": provenance,
    }


def make_endpoint(
    *,
    ep_id: str,
    controller_class: str,
    handler_signature: str,
    path: str,
    http_method: str,
    parameters: list[dict[str, Any]],
    framework: str,
    response_schema: Any = None,
    crud_operations: list[Any] | None = None,
    evidence: dict[str, Any] | None = None,
    path_provenance: str = "SA",
) -> dict[str, Any]:
    return {
        "id": ep_id,
        "controllerClass": controller_class,
        "handlerSignature": handler_signature,
        "path": path,
        "httpMethod": http_method,
        "parameters": parameters,
        "interParamDependencies": [],          # filled by the agent (Stage 2b)
        "databaseOperations": crud_operations or [],
        "responseSchema": response_schema,
        "framework": framework,
        "provenance": "SA",
        "pathProvenance": path_provenance,
        "evidence": evidence or {},
    }


# =========================================================================== #
# Framework adapters (framework knowledge lives only here)
# =========================================================================== #

class FrameworkAdapter:
    name = "abstract"

    def matches(self, ci: ClassInfo) -> bool:
        raise NotImplementedError

    def extract_endpoints(self, ci: ClassInfo, ctx: ModelContext) -> list[dict[str, Any]]:
        raise NotImplementedError

    def extract_auth(self, ci: ClassInfo, ctx: ModelContext) -> dict[str, Any] | None:
        return None


_SPRING_MAPPING_VERB = {
    "GetMapping": ["GET"],
    "PostMapping": ["POST"],
    "PutMapping": ["PUT"],
    "DeleteMapping": ["DELETE"],
    "PatchMapping": ["PATCH"],
    "RequestMapping": None,  # verb from method=RequestMethod.X
}
_SPRING_CONTROLLER_ANN = ("RestController", "Controller")
_SPRING_BINDING_KIND = {
    "PathVariable": "path",
    "RequestParam": "query",
    "RequestHeader": "header",
    "RequestBody": "body",
    "ModelAttribute": "form",
    "CookieValue": "cookie",
}


def _spring_request_methods(args: str) -> list[str]:
    return re.findall(r"RequestMethod\.([A-Z]+)", args)


class SpringMvcAdapter(FrameworkAdapter):
    name = "spring-mvc"

    def matches(self, ci: ClassInfo) -> bool:
        return any(c in ci.annotation_names for c in _SPRING_CONTROLLER_ANN)

    def _base_paths(self, ci: ClassInfo) -> list[str]:
        rm = find_annotation(ci.annotations, "RequestMapping")
        return extract_paths(ann_args(rm)) if rm else [""]

    def extract_endpoints(self, ci: ClassInfo, ctx: ModelContext) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        base_paths = self._base_paths(ci)
        for sig, m in ci.methods().items():
            mann = m.get("annotations", []) or []
            mapping = next(
                ((ann_name(a), ann_args(a)) for a in mann if ann_name(a) in _SPRING_MAPPING_VERB),
                None,
            )
            if mapping is None:
                continue
            nm, margs = mapping
            sub_paths = extract_paths(margs)
            verbs = _SPRING_MAPPING_VERB[nm] or _spring_request_methods(margs) or ["GET"]
            params = self._params(ci, sig, m, ctx)
            for bp in base_paths:
                for sp in sub_paths:
                    full = join_path(bp, sp)
                    for v in verbs:
                        out.append(
                            make_endpoint(
                                ep_id="",
                                controller_class=ci.qualified_name,
                                handler_signature=sig,
                                path=full,
                                http_method=v,
                                parameters=params,
                                framework=self.name,
                                response_schema=m.get("return_type"),
                                crud_operations=m.get("crud_operations") or [],
                                evidence={
                                    "sourceAnnotations": mann,
                                    "startLine": m.get("start_line"),
                                    "endLine": m.get("end_line"),
                                },
                            )
                        )
        return out

    def _params(self, ci: ClassInfo, sig: str, m: dict[str, Any], ctx: ModelContext):
        params = []
        for p in m.get("parameters", []) or []:
            pann = p.get("annotations", []) or []
            pann_names = [ann_name(x) for x in pann]
            kind = "unknown"
            for b, k in _SPRING_BINDING_KIND.items():
                if b in pann_names:
                    kind = k
                    break
            ptype = p.get("type", "")
            if kind == "unknown" and is_project_type(ptype, ctx):
                kind = "body"
            params.append(
                make_param(
                    name=p.get("name"),
                    ptype=ptype,
                    kind=kind,
                    annotations=pann,
                    enclosing_method=sig,
                    enclosing_class=ci.qualified_name,
                )
            )
        return params

    def extract_auth(self, ci: ClassInfo, ctx: ModelContext) -> dict[str, Any] | None:
        is_sec = any(
            "EnableWebSecurity" in a or "EnableGlobalMethodSecurity" in a or "EnableMethodSecurity" in a
            for a in ci.annotations
        ) or "SecurityConfig" in ci.simple_name
        if not is_sec:
            return None
        rules = []
        for sig, m in ci.methods().items():
            code = m.get("code") or ""
            ret = m.get("return_type") or ""
            if (
                "SecurityFilterChain" in ret
                or "authorizeHttpRequests" in code
                or "authorizeRequests" in code
                or "antMatchers" in code
                or "requestMatchers" in code
            ):
                rules.append(
                    {
                        "class": ci.qualified_name,
                        "method": sig,
                        "evidence": {"sourceText": code},
                        "provenance": "SA",
                    }
                )
        if not rules:
            return None
        return {"framework": "spring-security", "rules": rules}


_JAXRS_VERB_ANN = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
_JAXRS_PARAM_KIND = {
    "PathParam": "path",
    "QueryParam": "query",
    "HeaderParam": "header",
    "FormParam": "form",
    "CookieParam": "cookie",
    "MatrixParam": "query",
    "BeanParam": "query",
}


class JaxRsAdapter(FrameworkAdapter):
    name = "jax-rs"

    def matches(self, ci: ClassInfo) -> bool:
        if "Path" in ci.annotation_names:
            return True
        for m in ci.methods().values():
            if any(ann_name(a) in _JAXRS_VERB_ANN for a in (m.get("annotations") or [])):
                return "Path" in ci.annotation_names
        return False

    def _base_path(self, ci: ClassInfo) -> str:
        a = find_annotation(ci.annotations, "Path")
        return extract_paths(ann_args(a))[0] if a else ""

    def _content_types(self, annotations: list[str]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        cons = find_annotation(annotations, "Consumes")
        prod = find_annotation(annotations, "Produces")
        if cons:
            out["consumes"] = extract_paths(ann_args(cons))
        if prod:
            out["produces"] = extract_paths(ann_args(prod))
        return out

    def extract_endpoints(self, ci: ClassInfo, ctx: ModelContext) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        base = self._base_path(ci)
        for sig, m in ci.methods().items():
            mann = m.get("annotations", []) or []
            verbs = [ann_name(a) for a in mann if ann_name(a) in _JAXRS_VERB_ANN]
            if not verbs:
                continue
            sub = find_annotation(mann, "Path")
            sub_path = extract_paths(ann_args(sub))[0] if sub else ""
            full = join_path(base, sub_path)
            ct = self._content_types(mann) or self._content_types(ci.annotations)
            params = self._params(ci, sig, m, ctx)
            for v in verbs:
                out.append(
                    make_endpoint(
                        ep_id="",
                        controller_class=ci.qualified_name,
                        handler_signature=sig,
                        path=full,
                        http_method=v,
                        parameters=params,
                        framework=self.name,
                        response_schema=m.get("return_type"),
                        crud_operations=m.get("crud_operations") or [],
                        evidence={
                            "sourceAnnotations": mann,
                            "contentTypes": ct,
                            "startLine": m.get("start_line"),
                            "endLine": m.get("end_line"),
                        },
                    )
                )
        return out

    def _params(self, ci: ClassInfo, sig: str, m: dict[str, Any], ctx: ModelContext):
        params = []
        for p in m.get("parameters", []) or []:
            pann = p.get("annotations", []) or []
            pann_names = [ann_name(x) for x in pann]
            default = None
            dv = find_annotation(pann, "DefaultValue")
            if dv:
                vals = extract_paths(ann_args(dv))
                default = vals[0] if vals else None
            kind = "unknown"
            for a, k in _JAXRS_PARAM_KIND.items():
                if a in pann_names:
                    kind = k
                    break
            ptype = p.get("type", "")
            if kind == "unknown" and is_project_type(ptype, ctx):
                kind = "body"
            vc = [{"defaultValue": default}] if default is not None else []
            params.append(
                make_param(
                    name=p.get("name"),
                    ptype=ptype,
                    kind=kind,
                    annotations=pann,
                    enclosing_method=sig,
                    enclosing_class=ci.qualified_name,
                    value_constraints=vc,
                )
            )
        return params

    def extract_auth(self, ci: ClassInfo, ctx: ModelContext) -> dict[str, Any] | None:
        rules = []
        for sig, m in ci.methods().items():
            for a in m.get("annotations", []) or []:
                if ann_name(a) in ("RolesAllowed", "PermitAll", "DenyAll"):
                    rules.append({"method": sig, "annotation": a, "provenance": "SA"})
        for a in ci.annotations:
            if ann_name(a) in ("RolesAllowed", "PermitAll", "DenyAll"):
                rules.append({"class": ci.qualified_name, "annotation": a, "provenance": "SA"})
        if not rules:
            return None
        return {"framework": "jax-rs-security", "rules": rules}


_MICRONAUT_MAPPING_VERB = {
    "Get": "GET",
    "Post": "POST",
    "Put": "PUT",
    "Delete": "DELETE",
    "Patch": "PATCH",
    "Head": "HEAD",
    "Options": "OPTIONS",
}
_MICRONAUT_PARAM_KIND = {
    "PathVariable": "path",
    "QueryValue": "query",
    "Header": "header",
    "Body": "body",
    "CookieValue": "cookie",
    "Part": "form",
}


class MicronautAdapter(FrameworkAdapter):
    name = "micronaut"

    def matches(self, ci: ClassInfo) -> bool:
        return "Controller" in ci.annotation_names

    def _base_path(self, ci: ClassInfo) -> str:
        a = find_annotation(ci.annotations, "Controller")
        paths = extract_paths(ann_args(a)) if a else [""]
        return paths[0]

    def extract_endpoints(self, ci: ClassInfo, ctx: ModelContext) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        base = self._base_path(ci)
        for sig, m in ci.methods().items():
            mann = m.get("annotations", []) or []
            mapping = next(
                ((ann_name(a), ann_args(a)) for a in mann if ann_name(a) in _MICRONAUT_MAPPING_VERB),
                None,
            )
            if mapping is None:
                continue
            nm, margs = mapping
            sub_paths = extract_paths(margs)
            verb = _MICRONAUT_MAPPING_VERB[nm]
            params = self._params(ci, sig, m, ctx)
            for sp in sub_paths:
                full = join_path(base, sp)
                out.append(
                    make_endpoint(
                        ep_id="",
                        controller_class=ci.qualified_name,
                        handler_signature=sig,
                        path=full,
                        http_method=verb,
                        parameters=params,
                        framework=self.name,
                        response_schema=m.get("return_type"),
                        crud_operations=m.get("crud_operations") or [],
                        evidence={
                            "sourceAnnotations": mann,
                            "startLine": m.get("start_line"),
                            "endLine": m.get("end_line"),
                        },
                    )
                )
        return out

    def _params(self, ci: ClassInfo, sig: str, m: dict[str, Any], ctx: ModelContext):
        params = []
        for p in m.get("parameters", []) or []:
            pann = p.get("annotations", []) or []
            pann_names = [ann_name(x) for x in pann]
            kind = "unknown"
            for a, k in _MICRONAUT_PARAM_KIND.items():
                if a in pann_names:
                    kind = k
                    break
            ptype = p.get("type", "")
            if kind == "unknown" and is_project_type(ptype, ctx):
                kind = "body"
            params.append(
                make_param(
                    name=p.get("name"),
                    ptype=ptype,
                    kind=kind,
                    annotations=pann,
                    enclosing_method=sig,
                    enclosing_class=ci.qualified_name,
                )
            )
        return params

    def extract_auth(self, ci: ClassInfo, ctx: ModelContext) -> dict[str, Any] | None:
        rules = []
        for a in ci.annotations:
            if ann_name(a) == "Secured":
                rules.append({"class": ci.qualified_name, "annotation": a, "provenance": "SA"})
        for sig, m in ci.methods().items():
            for a in m.get("annotations", []) or []:
                if ann_name(a) == "Secured":
                    rules.append({"method": sig, "annotation": a, "provenance": "SA"})
        if not rules:
            return None
        return {"framework": "micronaut-security", "rules": rules}


_SERVLET_DO_VERB = {
    "doGet": "GET",
    "doPost": "POST",
    "doPut": "PUT",
    "doDelete": "DELETE",
    "doHead": "HEAD",
    "doOptions": "OPTIONS",
    "doTrace": "TRACE",
}
_SERVLET_SUPERCLASS_KEYS = ("extends_list", "super_classes", "parent_classes", "super_class", "extends")


def _extends_http_servlet(ci: ClassInfo) -> bool:
    for key in _SERVLET_SUPERCLASS_KEYS:
        val = ci.decl.get(key)
        if not val:
            continue
        items = val if isinstance(val, (list, tuple)) else [val]
        for it in items:
            if "HttpServlet" in str(it):
                return True
    return False


def _method_short(sig: str) -> str:
    return sig.split("(", 1)[0].strip()


class ServletAdapter(FrameworkAdapter):
    name = "servlet"

    def matches(self, ci: ClassInfo) -> bool:
        if "WebServlet" in ci.annotation_names:
            return True
        if _extends_http_servlet(ci):
            return any(_method_short(s) in _SERVLET_DO_VERB for s in ci.methods())
        return False

    def _url_patterns(self, ci: ClassInfo) -> list[str]:
        a = find_annotation(ci.annotations, "WebServlet")
        if not a:
            return []
        args = ann_args(a)
        up = re.search(r'urlPatterns\s*=\s*(\{[^}]*\}|"[^"]*")', args)
        if up:
            return re.findall(r'"([^"]*)"', up.group(1))
        return [p for p in extract_paths(args) if p]

    def extract_endpoints(self, ci: ClassInfo, ctx: ModelContext) -> list[dict[str, Any]]:
        patterns = self._url_patterns(ci)
        if not patterns:
            # extends HttpServlet but no @WebServlet pattern: mapping likely in web.xml
            # (XML, unreachable at symbol level) -> sentinel path so the limitation is visible.
            patterns = ["/__servlet-mapping-unknown__"]
        out: list[dict[str, Any]] = []
        for sig, m in ci.methods().items():
            verb = _SERVLET_DO_VERB.get(_method_short(sig))
            if verb is None:
                continue
            for pat in patterns:
                full = join_path("", pat)
                ep = make_endpoint(
                    ep_id="",
                    controller_class=ci.qualified_name,
                    handler_signature=sig,
                    path=full,
                    http_method=verb,
                    parameters=[],  # request.getParameter(...) is unresolved at symbol level
                    framework=self.name,
                    response_schema="stream/unknown",
                    crud_operations=m.get("crud_operations") or [],
                    evidence={
                        "paramExtraction": "unsupported-at-symbol-level",
                        "handlerSource": m.get("code"),
                        "startLine": m.get("start_line"),
                        "endLine": m.get("end_line"),
                    },
                )
                ep["paramExtraction"] = "unsupported-at-symbol-level"
                out.append(ep)
        return out

    def extract_auth(self, ci: ClassInfo, ctx: ModelContext) -> dict[str, Any] | None:
        rules = []
        for a in ci.annotations:
            if ann_name(a) in ("ServletSecurity", "HttpConstraint"):
                rules.append({"class": ci.qualified_name, "annotation": a, "provenance": "SA"})
        if not rules:
            return None
        return {"framework": "servlet-security", "rules": rules}


ADAPTERS: list[FrameworkAdapter] = [
    SpringMvcAdapter(),
    JaxRsAdapter(),
    MicronautAdapter(),
    ServletAdapter(),
]
_SPRING = SpringMvcAdapter()  # reused for security-config auth extraction


# =========================================================================== #
# Stage 2a: build the SA skeleton
# =========================================================================== #

_VALIDATION_ANN_STD = {
    "NotNull", "NotEmpty", "NotBlank", "Size", "Min", "Max", "Email", "Pattern",
    "Positive", "PositiveOrZero", "Negative", "NegativeOrZero", "Digits", "Past",
    "Future", "DecimalMin", "DecimalMax", "AssertTrue", "AssertFalse",
}


def _index_classes(symbol_table: dict[str, Any]) -> ModelContext:
    ctx = ModelContext()
    for fp, fd in symbol_table.items():
        if not isinstance(fd, dict):
            continue
        for cn, cd in (fd.get("type_declarations", {}) or {}).items():
            ctx.classes[cn] = ClassInfo(
                qualified_name=cn, decl=cd, package=fd.get("package_name"), file=fp
            )
    return ctx


def _is_custom_constraint(ann: str, ctx: ModelContext) -> bool:
    nm = ann_name(ann)
    if nm in _VALIDATION_ANN_STD:
        return True
    for cn, ci in ctx.classes.items():
        if ci.simple_name == nm:
            if any(ann_name(a) == "Constraint" for a in ci.annotations):
                return True
    return False


def _dto_schema(type_name: str, ctx: ModelContext) -> dict[str, Any] | None:
    base = re.sub(r"<.*?>", "", type_name).strip()
    ci = ctx.classes.get(base)
    if ci is None:
        return None
    fields = []
    for fd in ci.fields():
        fann = fd.get("annotations", []) or []
        vrules = [a for a in fann if _is_custom_constraint(a, ctx)]
        names = fd.get("variables") or ([fd.get("name")] if fd.get("name") else [None])
        for name in names:
            fields.append(
                {
                    "name": name,
                    "type": fd.get("type"),
                    "validationAnnotations": vrules,
                    "provenance": "SA",
                }
            )
    return {
        "class": base,
        "classAnnotations": ci.annotations,
        "fields": fields,
        "provenance": "SA",
    }


def _norm_path(path: str) -> str:
    return "/" + "/".join(
        "{}" if seg.startswith("{") else seg
        for seg in path.strip("/").split("/")
        if seg != ""
    )


def _resource_edges(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """RAFT-like SA resource edges: writers on a resource -> readers/mutators of its item."""
    edges: list[dict[str, Any]] = []
    by_resource: dict[str, list[dict[str, Any]]] = {}
    for ep in endpoints:
        norm = _norm_path(ep["path"])
        key = re.sub(r"/\{\}$", "", norm) or "/"
        by_resource.setdefault(key, []).append(ep)
    for key, group in by_resource.items():
        writers = [e for e in group if e["httpMethod"] in ("POST", "PUT", "PATCH")]
        readers = [e for e in group if e["httpMethod"] in ("GET", "DELETE")]
        for w in writers:
            for r in readers:
                if w["id"] == r["id"]:
                    continue
                edges.append(
                    {
                        "from": w["id"],
                        "to": r["id"],
                        "type": "resource",
                        "rationale": f"shared resource {key}: {r['httpMethod']} consumes what "
                        f"{w['httpMethod']} produces",
                        "provenance": "SA",
                    }
                )
    return edges


def build_sa_skeleton(analysis: dict[str, Any]) -> dict[str, Any]:
    symbol_table = analysis["symbol_table"]
    ctx = _index_classes(symbol_table)

    raw_endpoints: list[dict[str, Any]] = []
    frameworks: set[str] = set()
    auth_fragments: list[dict[str, Any]] = []
    dto_types: set[str] = set()

    for cn, ci in ctx.classes.items():
        chosen = None
        for adapter in ADAPTERS:
            if not adapter.matches(ci):
                continue
            eps = adapter.extract_endpoints(ci, ctx)
            if not eps:
                continue  # matched by annotation but produced nothing; try next adapter
            chosen = adapter
            frameworks.add(adapter.name)
            raw_endpoints.extend(eps)
            for ep in eps:
                for p in ep["parameters"]:
                    if p["kind"] == "body" and p["type"]:
                        dto_types.add(re.sub(r"<.*?>", "", p["type"]).strip())
            frag = adapter.extract_auth(ci, ctx)
            if frag:
                auth_fragments.append(frag)
            break  # one endpoint-producing adapter per class
        if chosen is None:
            # security configuration classes carry no endpoints but do carry auth rules
            frag = _SPRING.extract_auth(ci, ctx)
            if frag:
                auth_fragments.append(frag)

    raw_endpoints.sort(key=lambda e: (e["path"], e["httpMethod"]))
    for i, ep in enumerate(raw_endpoints, start=1):
        ep["id"] = f"EP{i:02d}"

    dtos = {}
    for t in sorted(dto_types):
        sch = _dto_schema(t, ctx)
        if sch:
            dtos[t] = sch

    resource_edges = _resource_edges(raw_endpoints)
    odg = {
        "nodes": [
            {"id": ep["id"], "functionalSummary": None, "provenance": "SA"}
            for ep in raw_endpoints
        ],
        "edges": resource_edges,
    }
    auth_model = {"fragments": auth_fragments} if auth_fragments else {"mode": "unknown"}

    return {
        "schema": "saint-endpoint-model/1",
        "frameworksDetected": sorted(frameworks),
        "endpointCount": len(raw_endpoints),
        "endpoints": raw_endpoints,
        "dtoSchemas": dtos,
        "odg": odg,
        "authModel": auth_model,
        "enrichment": {"applied": False, "provenance": "SA-only"},
    }


# =========================================================================== #
# Schemas (Gate-1) + invariants (Gate-2)
# =========================================================================== #

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"}
PARAM_KINDS = {"path", "query", "header", "body", "form", "cookie", "unknown"}
IPD_TYPES = {"AllOrNone", "Requires", "OnlyOne", "Or", "ZeroOrOne", "Arithmetic", "Complex"}
ODG_EDGE_TYPES = {"resource", "producer-consumer", "database"}


class SchemaValidationError(Exception):
    pass


class InvariantError(Exception):
    pass


ANALYSIS_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["symbol_table"],
    "properties": {
        "symbol_table": {"type": "object"},
        "version": {"type": ["string", "number", "null"]},
    },
}

_PARAM_SCHEMA = {
    "type": "object",
    "required": ["name", "type", "kind", "provenance"],
    "properties": {
        "name": {"type": ["string", "null"]},
        "type": {"type": ["string", "null"]},
        "kind": {"type": "string", "enum": sorted(PARAM_KINDS)},
        "valueConstraints": {"type": ["array", "null"]},
        "enclosingMethod": {"type": ["string", "null"]},
        "enclosingClass": {"type": ["string", "null"]},
        "annotations": {"type": "array"},
        "provenance": {"type": "string", "enum": ["SA", "LLM"]},
    },
}

_ENDPOINT_SCHEMA = {
    "type": "object",
    "required": [
        "id", "controllerClass", "handlerSignature", "path", "httpMethod",
        "parameters", "framework", "provenance",
    ],
    "properties": {
        "id": {"type": "string"},
        "controllerClass": {"type": "string"},
        "handlerSignature": {"type": "string"},
        "path": {"type": "string"},
        "httpMethod": {"type": "string", "enum": sorted(HTTP_METHODS)},
        "parameters": {"type": "array", "items": _PARAM_SCHEMA},
        "interParamDependencies": {"type": "array"},
        "databaseOperations": {"type": "array"},
        "responseSchema": {},
        "framework": {"type": "string"},
        "provenance": {"type": "string", "enum": ["SA", "LLM"]},
        "evidence": {"type": "object"},
    },
}

_ODG_NODE_SCHEMA = {
    "type": "object",
    "required": ["id", "functionalSummary"],
    "properties": {
        "id": {"type": "string"},
        "functionalSummary": {"type": ["string", "null"]},
        "provenance": {"type": "string", "enum": ["SA", "LLM"]},
    },
}

_ODG_EDGE_SCHEMA = {
    "type": "object",
    "required": ["from", "to", "type", "provenance"],
    "properties": {
        "from": {"type": "string"},
        "to": {"type": "string"},
        "type": {"type": "string", "enum": sorted(ODG_EDGE_TYPES)},
        "rationale": {"type": ["string", "null"]},
        "provenance": {"type": "string", "enum": ["SA", "LLM"]},
    },
}

ENDPOINT_MODEL_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["schema", "frameworksDetected", "endpointCount", "endpoints", "odg"],
    "properties": {
        "schema": {"type": "string"},
        "frameworksDetected": {"type": "array", "items": {"type": "string"}},
        "endpointCount": {"type": "integer", "minimum": 0},
        "endpoints": {"type": "array", "items": _ENDPOINT_SCHEMA},
        "dtoSchemas": {"type": "object"},
        "odg": {
            "type": "object",
            "required": ["nodes", "edges"],
            "properties": {
                "nodes": {"type": "array", "items": _ODG_NODE_SCHEMA},
                "edges": {"type": "array", "items": _ODG_EDGE_SCHEMA},
            },
        },
        "authModel": {"type": "object"},
    },
}


def validate_schema(instance: Any, schema: dict[str, Any], label: str) -> None:
    """Gate-1. Best-effort: skipped when jsonschema is unavailable."""
    if jsonschema is None:
        _log(f"jsonschema not installed; skipping Gate-1 schema check for {label}")
        return
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        path = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        raise SchemaValidationError(f"[{label}] schema violation at {path}: {exc.message}") from exc


def _check_analysis_invariants(doc: dict[str, Any]) -> None:
    st = doc.get("symbol_table")
    if not isinstance(st, dict):
        raise InvariantError("analysis.json: symbol_table must be an object")
    has_types = any(fd.get("type_declarations") for fd in st.values() if isinstance(fd, dict))
    if not has_types:
        raise InvariantError("analysis.json: symbol table has no type_declarations")


def check_endpoint_model_invariants(doc: dict[str, Any]) -> None:
    eps = doc.get("endpoints", [])
    if doc.get("endpointCount") != len(eps):
        raise InvariantError(
            f"endpoint-model: endpointCount={doc.get('endpointCount')} != len(endpoints)={len(eps)}"
        )
    if not doc.get("frameworksDetected"):
        raise InvariantError("endpoint-model: frameworksDetected is empty")
    ids: set[str] = set()
    for ep in eps:
        ids.add(ep["id"])
        if ep["httpMethod"] not in HTTP_METHODS:
            raise InvariantError(f"endpoint {ep['id']}: bad httpMethod {ep['httpMethod']}")
        if not ep["path"].startswith("/"):
            raise InvariantError(f"endpoint {ep['id']}: path must start with '/' ({ep['path']})")
        if ep.get("provenance") not in ("SA", "LLM"):
            raise InvariantError(f"endpoint {ep['id']}: bad provenance")
        for p in ep.get("parameters", []):
            if p.get("kind") not in PARAM_KINDS:
                raise InvariantError(f"endpoint {ep['id']}: param kind {p.get('kind')} invalid")
        for ipd in ep.get("interParamDependencies", []):
            if ipd.get("relationType") not in IPD_TYPES:
                raise InvariantError(
                    f"endpoint {ep['id']}: IPD relationType {ipd.get('relationType')} not in catalog"
                )
            if ipd.get("provenance") != "LLM":
                raise InvariantError(f"endpoint {ep['id']}: IPD provenance must be LLM")
    odg = doc.get("odg", {})
    node_ids = {n["id"] for n in odg.get("nodes", [])}
    if node_ids != ids:
        raise InvariantError("endpoint-model: ODG nodes must be exactly the endpoint ids")
    for n in odg.get("nodes", []):
        if "functionalSummary" not in n:
            raise InvariantError(f"ODG node {n['id']}: missing functionalSummary")
    for e in odg.get("edges", []):
        if e["from"] not in node_ids or e["to"] not in node_ids:
            raise InvariantError(f"ODG edge {e['from']}->{e['to']}: endpoint not in node set")
        if e["type"] == "resource" and e.get("provenance") != "SA":
            raise InvariantError(f"ODG resource edge {e['from']}->{e['to']} must be SA")
        if e["type"] in ("producer-consumer", "database") and e.get("provenance") != "LLM":
            raise InvariantError(f"ODG {e['type']} edge {e['from']}->{e['to']} must be agent-added (LLM)")


# =========================================================================== #
# Commands
# =========================================================================== #

def cmd_build(module_path: str, out_path: str) -> int:
    module = Path(module_path).resolve()
    if not module.exists():
        _log(f"module path does not exist: {module}")
        return 3
    work_dir = Path(out_path).resolve().parent / "_sa-work"
    try:
        analysis = run_codeanalyzer(module, work_dir)
    except SaError as exc:
        _log(f"static analysis failed (forced SA cannot be skipped): {exc}")
        return 3
    except InvariantError as exc:
        _log(f"codeanalyzer output unusable: {exc}")
        return 4

    model = build_sa_skeleton(analysis)
    if not model["frameworksDetected"]:
        _log("no supported web framework detected (Spring MVC / JAX-RS / Micronaut / Servlet).")
        return 2

    validate_schema(model, ENDPOINT_MODEL_SCHEMA, "endpoint-model")
    check_endpoint_model_invariants(model)
    Path(out_path).write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    _log(
        f"OK -> {out_path} ({model['endpointCount']} endpoints, "
        f"frameworks={model['frameworksDetected']}, "
        f"resourceEdges={len(model['odg']['edges'])})"
    )
    return 0


def cmd_validate(model_path: str) -> int:
    p = Path(model_path)
    if not p.exists():
        _log(f"model file not found: {model_path}")
        return 1
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
        validate_schema(doc, ENDPOINT_MODEL_SCHEMA, "endpoint-model")
        check_endpoint_model_invariants(doc)
    except (SchemaValidationError, InvariantError, ValueError) as exc:
        _log(f"INVALID: {exc}")
        return 1
    _log(f"VALID: {model_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _log(__doc__ or "usage: endpoint-model-sa.py build <module> <out.json> | validate <model.json>")
        return 64
    cmd, rest = args[0], args[1:]
    if cmd == "build":
        if len(rest) != 2:
            _log("usage: endpoint-model-sa.py build <module-path> <out.json>")
            return 64
        return cmd_build(rest[0], rest[1])
    if cmd == "validate":
        if len(rest) != 1:
            _log("usage: endpoint-model-sa.py validate <model.json>")
            return 64
        return cmd_validate(rest[0])
    _log(f"unknown command: {cmd}")
    return 64


if __name__ == "__main__":
    raise SystemExit(main())
