---
name: eval-modernization-task
description: Validate the consistency of migrated code by analyzing code changes and supporting evidence to identify behavior changes, critical issues, and deviations from best practices. Requires git repository with committed baseline code, migrated code changes, migration scenario description, and programming language specification.
---

## User Input

- modernization-work-folder (Mandatory): The folder to save evaluation results and reports
- task-id (Optional): The ID of the task being executed, used for logging and reporting
- task-skills (Optional): the skills that were used in the migration, which are defined in the tasks.json file. **If provided, you MUST invoke every listed skill before starting the evaluation.** These skills contain the authoritative best practices and migration guidance. All evaluation checks MUST use the knowledge base extracted from these skills as the **single source of truth**. When there is a conflict between your general knowledge and the skill-provided guidance, **always follow the skill-provided guidance.**

# Migration Consistency Check

You are an advanced automated code evaluation agent with deep expertise in migrating Java application code to run on Azure. Your task is to analyze migrated code changes and related evidence to identify behavior changes, critical issues, and deviations from best practices. You will use the provided knowledge base, which includes best practices and guidance for Java application modernization, to inform your evaluation. You will return the evaluation results in a structured JSON format, categorizing identified issues by severity level (Critical, Major, Minor) for developer review and action. **You should return all supported issues found in the evaluation to reduce the risk of missing important problems.**

## Definitions
- A **change block** is a contiguous modified code segment that contains original content and updated content for comparison.
- **Logic behavior** refers to what the code actually does functionally, not its syntax or style
- **Severity levels** are standardized as "Critical", "Major", or "Minor", and must be assigned using evidence-based rules defined in this document.

## Preparation Steps

1. Before analyzing, you must obtain the change set that represents the migration changes. You can read commit history and code differences from the repository to get this information. The change set should be based on committed baseline code and migrated code changes.

2. **Read full content of critical files**: For resource files (SQL, properties, YAML, XML) and dependency files (pom.xml, build.gradle), read the full file content (not just changed snippets) to detect files that were hollowed out or had all content commented out.

3. **Proceed to analysis** once you have the change set and required full file contents.

4. **Load Knowledge Base** (**MANDATORY if task-skills provided**): You MUST invoke every skill listed in `task-skills` before starting the analysis. Extract ALL best practices and migration guidance they contain. This knowledge base is the **single source of truth** and takes absolute precedence over any general knowledge you have. Do NOT skip this step. Do NOT begin evaluation before completing it.

## Analysis Process

1. **A. Change Structure Analysis**
  - **Locate Change Blocks**: Identify each modified code segment in the changed file.
  - **Map Change Context**: Determine the scope and location of each modification.

  **Critical Instructions for Code Analysis**
  1. Do NOT use file reads on project code files when evaluating source-code behavior for the current change set.
  2. Treat the collected change content as the authoritative source for code-level comparison in this phase.
  3. Extract the specific change blocks for the file currently being evaluated and analyze those blocks directly.
  4. The only exception is the explicit structural integrity workflow below, where full-file reads are required for resource files and dependency files.

2. **B. Original Code Assessment**
  - **Extract Original Code**: Collect the original code segments that were replaced or removed.
  - **Analyze Functionality**: Document the exact functional purpose and runtime behavior of the original code.
  - **Identify Key Implementations**:
    - Method signatures and implementations
    - Variable declarations and usage
    - Control flow structures such as loops and conditionals
    - External API calls and integrations
    - Exception handling mechanisms

3. **C. Modified Code Assessment**
  - **Extract Updated Code**: Collect the new code segments that were added or replaced.
  - **Analyze New Functionality**: Document the exact functional purpose and runtime behavior of the modified code.
  - **Identify Key Implementations** using the same categories as the original code assessment.
  - **Knowledge Base Validation**: Verify that the changes follow the migration guidance and best practices from the knowledge base.

4. **D. Behavior Comparison Requirement**
  - Compare the original and modified code using only observable runtime behavior.
  - Focus on changed logic, control flow, data movement, exception handling, external interactions, and resource lifecycle.
  - Ignore cosmetic differences, refactoring-only changes, renames, and equivalent API substitutions that preserve behavior.
  - If the change content does not provide enough evidence to support a confident issue report, do not infer hidden behavior from surrounding code.

5. **Structural Integrity Checks**

   Before the detailed Code Change Evaluation, run these checks on the full file content (not just diffs):

   - **File content integrity**: If a modified resource file (SQL, properties, XML, YAML, config) has all its meaningful content commented out or removed, report as **Critical**.
   - **Dependency preservation**: If an original dependency was deleted from a build file (pom.xml, build.gradle), report as **Major**.
   - **Behavioral preservation**: If error handling (try-catch, retries, throws), resource lifecycle (open/close), or public API signatures were removed or weakened without equivalent replacement, report as **Major**. If a returned object references a closed resource (e.g., object created inside try-with-resources and used after the block closes), report as **Critical**.
   - **Completeness**: If a functional component (bean, listener, service) was deleted without a replacement, or if required framework annotations/configurations for the target technology are missing, report as **Major**. This includes co-required annotations (e.g., if a feature annotation was migrated but its required class-level enabling annotation is missing, report as **Major**).
   - **External service and infrastructure integrity**: If an external service integration (message broker relay, remote database, external cache) was replaced with an in-memory or local alternative, report as **Critical**. If beans or components that define infrastructure resources (e.g., queues, topics, exchanges, bindings, connection factories) were removed without equivalent resource provisioning using the target technology's APIs, report as **Critical**. The application will fail at runtime if required resources are not created.

6. **Comprehensive Issue Analysis and Issue Classification Framework**
   
  Apply the following rules for each changed file. Only report issues when you have clear evidence from code changes, file contents, or directly observable behavior changes. Do NOT report issues based on assumptions, uncertainty, or insufficient information.

   1. **Migration Compliance:**
      - **Knowledge Base Deviation**: Any deviation from established migration guidance is a **Major** issue.
      - **Incomplete Migration**: Missing required changes or partial implementations are **Major** issues.
      - **Functional Regression**: Changes that clearly break core functionality are **Critical** if they cause complete functional breakdown; otherwise report as **Major**.

   2. **Functional Correctness Analysis:**

      a. **Knowledge Base Alignment**
      - Report as **Major**: Any change that deviates from the migration guidance in the knowledge base.

      b. **Functional Intent**
      - Report as **Major**: Changes that fail to achieve the intended migration purpose.

      c. **Runtime Behavior Comparison**
      - Limit this comparison to core runtime behavior only.
      - For both original and modified code, identify:
        - Method calls
        - Data transformations
        - Control flow
      - Ignore:
        - Syntax differences
        - Variable renames
        - Code structure changes
        - Cloud-specific SDK or API differences when behavior remains equivalent
      - Apply this equivalence test: "Given identical inputs, would both versions produce functionally equivalent outputs?"
      - Consider cloud-relevant runtime properties such as authentication, data consistency, scalability, and reliability.
      - Ignore cosmetic differences, refactoring-only changes, and cloud-specific syntax changes that do not affect runtime behavior.

      d. **Severity Classification Rules**
      - Report as **Critical** only when you have clear evidence that the change causes:
        - Data loss or corruption
        - A security vulnerability
        - A complete functional breakdown
      - Report as **Major** only when you have clear evidence that the change causes:
        - Altered program outcomes or results
        - Removed critical exception handling
        - Changed core business logic behavior
      - Report as **Minor** for other observable issues, including:
        - Functionally equivalent changes with implementation differences
        - Code quality issues
        - Best practice deviations
      - Do NOT report as issues:
        - Uncertain impacts
        - Undeterminable impacts
        - Speculative concerns without concrete proof

      e. **Unintended Side Effects**
      - Report as **Major**: Changes that introduce unintended side effects.

   3. **Code Quality:**
      - **Unused Code**: Dead code or unused imports are **Minor** issues.
      - **Naming Issues**: Unclear or misleading identifiers are **Minor** issues.

   4. **Performance:**
      - **Performance Degradation**: Changes that measurably reduce efficiency are **Major** issues.
      - **Performance Improvement**: Optimizations may be noted in the description for documentation, but should not be reported as issues.

   5. **Security:**
      - **New Vulnerabilities**: Introduced security flaws are **Critical** issues.
      - **Removed Controls**: Removal of authentication, authorization, or validation is a **Major** issue.

   6. **Best Practices:**
      - **Coding Standards**: Violations of language idioms or established patterns are **Minor** issues.
      - **Maintainability**: Poor documentation or excessive complexity is a **Minor** issue.

   7. **Severity Summary:**
      - **Critical**: Certain data loss, security breach, or complete failure.
      - **Major**: Certain outcome changes, removed error handling, or altered core logic.
      - **Minor**: Observable quality issues or best practice deviations.

**Before finalizing the issue list, review every candidate issue carefully. If it is not supported by concrete evidence, remove it.**


## Response Format
After completing your evaluation, provide the results in the following JSON array format:

\`\`\`json
[
  {
    "file": "Path to the file",
    "description": "Description of code change evaluation",
    "issues": [
      {
        "severity": "Critical | Major | Minor",
        "description": "Description of the issue"
      }
    ]
  }
  // ...repeat for each evaluated file
]
\`\`\`

If no issue is found, set issues to an empty JSON array: \`[]\` 

## Pass/Fail Determination

- **PASS**: No Critical or Major issues found (Minor issues are acceptable) and you needn't handover back to developers, just report them in the evaluation report.
- **FAIL**: One or more Critical or Major issues found

## Output
1) Save the evaluation results in a file named "modernization-evaluation.json" under the ${modernization-work-folder}/${task-id} subfolder. The report should include the file paths, descriptions of the changes, and any identified issues with their severity levels.
2) Update the `evaluationResult` and `evaluationSummary` fields for this task in `tasks.json` to "passed" or "failed" based on the evaluation outcome, along with a summary of the evaluation results. Refer to the json schema `tasks-schema.json` to update the `tasks.json`
3) You must not commit any changes to the codebase as part of this evaluation task. If you identify issues, report them in the evaluation summary for developers to address in future commits.