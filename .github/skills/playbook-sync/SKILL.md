---
name: playbook-sync
description: Generate or update modernization playbook from document sources. Use this skill when the user wants to create a playbook, sync playbook from a document or GitHub issue, extract migration policies from architecture docs, or update existing playbook files with new decisions.
---

# Playbook Sync

Analyze source documents and generate a modernization playbook — three markdown files that capture an organization's approved migration targets, standards, and guardrails.

## User Input

- **output-path** (Required when push-git-url is NOT set): The folder to save the playbook files.
- **source-file-path** (Optional): Path to the source file containing the document content
- **push-git-url** (Optional): GitHub repository URL to push the generated playbook to. When set, output-path is NOT provided — you MUST only write playbook files to the cloned repo's `playbook/` directory determined in Step 0. Do NOT write files to any other location (no `.github/modernize/playbook/`, no local paths).

## Output Structure

```
${output-path}/
├── targets.md       # Approved technologies and migration decisions
├── standards.md     # Naming, security, and compliance rules
└── guardrails.md    # Prohibited/required technologies and patterns
```

## Principles

- **Source Fidelity**: The playbook is loaded and enforced by automated agents at runtime — a fabricated policy causes wrong migration decisions. Only include content explicitly present in the source document or user prompt. If a category isn't mentioned, omit that section entirely rather than adding placeholders.
- **Incremental Merge**: When output files already exist, merge at the **section level** — update sections with new or changed content, preserve unchanged sections verbatim. If the source explicitly removes or contradicts an existing entry, update that entry. Never drop existing content simply because the source is silent on it.
- **Direct Policy Output**: State policies as-is. Do not include rationale, explanations, or implementation guidance — those belong elsewhere.

## Classification Guide

When source content could fit multiple files, use these rules:

| Content | Goes in | Not in |
|---------|---------|--------|
| "Use Java 21" (approved target) | targets.md | guardrails.md |
| "Java 8 is prohibited" (prohibition) | guardrails.md | targets.md |
| "Secrets must be in Key Vault" (standard) | standards.md | guardrails.md |
| "No hardcoded secrets" (anti-pattern) | guardrails.md | standards.md |
| "Oracle DB → PostgreSQL" (migration) | targets.md | — |
| "SOC 2 Type II applies" (compliance) | standards.md | — |

**Rule of thumb**: targets.md says *what to use*, standards.md says *how to do it right*, guardrails.md says *what to avoid and what's mandatory*.

## Workflow

### Step 0: Prepare Remote Repository (only if push-git-url is provided)

If ${push-git-url} is set:

1. Determine a local working directory in the OS temp folder: `<temp>/modernize-playbook-sync/<repo-name>/`
2. If the directory already exists and is a valid git repo, run `git pull` to get the latest
3. If the directory does not exist, run `gh repo clone ${push-git-url} <temp>/modernize-playbook-sync/<repo-name>/`
4. Set ${output-path} to `<temp>/modernize-playbook-sync/<repo-name>/playbook/` (create the `playbook/` subdirectory if it doesn't exist)

**IMPORTANT**: When push-git-url is set, this is the ONLY location where playbook files should be written. Do NOT create or write files to `.github/modernize/playbook/` or any other local path.

If clone or pull fails, stop and report the error:
- Clone failure: "Failed to clone repository. Verify the URL is correct and accessible."
- Authentication failure: "Authentication failed. Run 'gh auth login' and verify you have push access to this repository."

### Step 1: Read and Analyze Source

1. If ${source-file-path} is provided, read the content (may be a GitHub issue export or markdown file)
2. Check if output files already exist in ${output-path} — read them for merge comparison
3. Classify each decision from the source (and/or the user prompt) into one of the three output files using the Classification Guide above

If no source file is provided, work with the user prompt and any existing playbook files only.

### Step 2: Generate Playbook Files

For each file, use the corresponding template as the structural reference, then fill in content extracted from the source.

#### targets.md

Use the template [targets-template](targets-template.md) for the required structure (5 sections):
- Target Frameworks, Target Compute Services, Target Data Services, Target Integration Services, Migration Decisions

#### standards.md

Use the template [standards-template](standards-template.md) for the required structure (7 sections):
- Resource Naming Conventions, Tagging Requirements, Authentication & Authorization, Secrets Management, Network Security, Encryption, Compliance Frameworks

#### guardrails.md

Use the template [guardrails-template](guardrails-template.md) for the required structure (3 sections):
- Prohibited Technologies, Prohibited Patterns, Required Elements

For each file: if it already exists, merge new content; if not, create it fresh.

### Step 3: Validate

Verify the output before finishing:
- [ ] All three files exist in ${output-path}
- [ ] targets.md has all 5 required sections
- [ ] standards.md has all 7 required sections
- [ ] guardrails.md has all 3 required sections
- [ ] Every decision in the source document is reflected in exactly one output file
- [ ] No content was invented beyond what the source provides

### Step 4: Present Summary

Report to the user:
- Number of target technologies defined
- Number of migration decisions captured
- Number of prohibited technologies/patterns
- Number of required elements
- Sections left empty (no corresponding source content) — flag these as gaps for architect review

### Step 5: Push to Remote Repository (only if push-git-url is provided)

If ${push-git-url} is set:

1. Check for actual changes with `git diff` in the cloned repo
2. If no changes: report "No changes detected, nothing to push." and stop
3. If there are changes:
   a. Stage only the playbook files: `git add playbook/` — do NOT stage any other files in the repo
   b. Generate a meaningful commit message based on the actual changes (English, conventional commit style, single-line summary). Example: `feat: add Java 21 migration target and Spring Boot 3.x standard`
   c. Run `git commit` with the generated message
   d. Run `git push`
4. If push fails:
   - Remote has new commits: run `git pull --rebase` then retry the push (do NOT regenerate the playbook)
   - Branch protection rules: "Push rejected by branch protection rules. The default branch requires a pull request to update. Please push manually or adjust the branch protection settings."
   - Authentication failure: "Authentication failed. Run 'gh auth login' and verify you have push access to this repository."
