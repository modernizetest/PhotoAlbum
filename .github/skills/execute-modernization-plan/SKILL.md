---
name: execute-modernization-plan
description: Execute the modernization plan by running the tasks listed in the plan
---

# Execute Modernization Plan

This skill is used to execute a modernization plan to migrate a given project to Azure.

## User Input

- `modernization-description`: The user intent to run the modernization plan.
- `modernization-work-folder` (Mandatory): The folder to save the modernization plan.
- `programming-language`: Input by user or autodetect by context.

You **MUST** consider the user input before proceeding.

## Workflow

Given that modernization description, do this:
1. Read `${modernization-work-folder}/plan.md` to get an overview of the modernization plan.

2. Load all tasks from `${modernization-work-folder}/tasks.json` and execute them one by one in the order they appear in the `tasks` array (do not reorder tasks):
     - Refer to JSON schema `tasks-schema.json` when updating `tasks.json`.
     - Before starting a task, update status to `started`.
     - After completing a task, **YOU MUST** update status to `success`, `failed`, or `skipped` with task summary and task `successCriteriaStatus`.
     - Do not stop task execution until all tasks are completed or any task fails.
     - Choose the right custom agent based on task `type`. The custom agent returns execution result (`success`, `skipped`, or `failed`) and summary.

        - Infrastructure task:
            - For tasks with `"type": "infrastructure"`, call custom agent `modernize-azure-platform-engineer` with prompt:
                ```md
                Generate IaC files to ./infra/ and provision Azure infrastructure.
                iacType: {iacType}
                provision: {provision}
                ```

        - Coding tasks:
            - Java upgrade task:
                - Use custom agent `general-purpose` for Java upgrade tasks (java-version-upgrade, spring-boot-upgrade, spring-framework-upgrade, jakarta-ee-upgrade) with prompt:
                    ```md
                    Call skill execute-modernization-task to upgrade the X from {{v1}} to {{v2}} using java upgrade tools
                    Here is the upgrade task details:
                    - TaskId (from `id` field)
                    - Description (from `description` field)
                    - Requirements (from `requirements` field)
                    - Environment Configuration (from `environmentConfiguration` field, may be null)
                    - Success Criteria (from `successCriteria` field, includes: passBuild, generateNewUnitTests, passUnitTests)
                    - Exit Criteria: Ensure all code logic, configurations, support files and tests are properly migrated. Ensure both build and tests pass. Ensure the modernization is consistent (all expected goals are correctly implemented) and complete (all old technology references are fully removed or replaced).
                    - modernization-work-folder: The folder to save the modernization summary
                    ```
                - `{{v1}}` and `{{v2}}` are versions. `{{v2}}` can be `latest version` if not specified.

            - .NET upgrade task:
                - For tasks with `"type": "upgrade"` where `skills` contains `"name": "create-dotnet-upgrade-plan"` (optionally with `"location": "builtin"`), call custom agent `modernize-dotnet-upgrade-developer` with prompt:
                    ```md
                    Complete the .NET upgrade in two phases:

                    Phase 1: Call skill create-dotnet-upgrade-plan with:
                        - upgrade-prompt: {task description from `description` field}
                        - modernization-work-folder: ${modernization-work-folder}/{taskId}

                    IMPORTANT: Use ${modernization-work-folder}/{taskId} as the work folder so the upgrade plan is saved in a subdirectory, NOT in the root plan folder.

                    Phase 2: Execute each sub-task from ${modernization-work-folder}/{taskId}/tasks.json sequentially using skill execute-modernization-task.

                    Here is the parent upgrade task details:
                        - TaskId (from `id` field)
                        - Description (from `description` field)
                        - Requirements (from `requirements` field)
                        - Environment Configuration (from `environmentConfiguration` field, may be null)
                        - Success Criteria (from `successCriteria` field, includes: passBuild, generateNewUnitTests, generateNewIntegrationTests, passUnitTests, passIntegrationTests)
                    ```

            - Transform task:
                - Use `You must call custom agent general-purpose` with prompt:
                    ```md
                    Call skill modernize-azure-developer to do the code change
                    Here is the transform task details:
                    - TaskId (from `id` field)
                    - Description (from `description` field)
                    - Requirements (from `requirements` field)
                    - Migration Skills (The skill list from `skills` field used for migration if available, otherwise show `hint: <description of this task>`)
                    - Environment Configuration (from `environmentConfiguration` field, may be null)
                    - Success Criteria (from `successCriteria` field, includes: passBuild, generateNewUnitTests, passUnitTests)
                    - Exit Criteria: Ensure all code logic, configurations, support files and tests are properly migrated. Ensure both build and tests pass. Ensure the modernization is consistent (all expected goals are correctly implemented) and complete (all old technology references are fully removed or replaced).
                    - modernization-work-folder: The folder to save the modernization plan from input
                    ```

            - Only use skill `execute-modernization-task` in custom agents for code changes per task.

        - Security task:
            - Use custom agent `general-purpose` with prompt:
                ```md
                Call skill {{security-skill-for-the-task}} to do the security check and fix
                Here is the security task details:
                        - TaskId (from `id` field)
                        - Description (from `description` field)
                        - Requirements (from `requirements` field)
                        - Environment Configuration (from `environmentConfiguration` field, may be null)
                        - Success Criteria (from `successCriteria` field, includes: passBuild, generateNewUnitTests, passUnitTests)
                        - modernization-work-folder: The folder to save the cve check report and fix summary
                ```
            - `{{security-skill-for-the-task}}` is resolved from the `skills` array in the security task in `tasks.json`.
                - If multiple skills exist, combine names as a comma-separated list.
                - If one skill exists, use its `name` directly.

        - Integration test task:
            - For tasks with `"type": "integrationTest"`, call custom agent `general-purpose` with prompt:
                ```md
                Call skill integration-tests to generate and run integration tests for the migrated project
                Here is the integration test task details:
                        - TaskId (from `id` field)
                        - Description (from `description` field)
                        - Requirements (from `requirements` field)
                        - Test Layers (from `layers` field, e.g., [1, 2] for Layer 1 and Layer 2)
                        - modernization-work-folder: The folder to save the modernization plan from input

                The integration-tests skill should:
                - For each layer in the layers array, run the integration-tests skill with that layer parameter
                - Layer 1: Generate Local Integration Tests with TestContainers for all Azure services
                - Layer 2: Generate Smoke Tests for basic application health checks
                - Ensure all tests pass before marking the task as successful
                ```

        - Containerization or deploy task:
            - Use custom agent `modernize-azure-deploy-developer` with prompt:
                ```md
                Deploy the application to Azure
                ```
            - If `plan.md` contains Azure Environment with Subscription ID and Resource Group, use:
                ```md
                Deploy the application to existing Azure resources. Subscription ID: {subscriptionId}, Resource Group: {resourceGroup}
                ```

     - Do not generate documents other than `modernization-summary.md` for each task.
     - **YOU MUST** update `tasks.json` with the final status of each task (`success`, `failed`, or `skipped`).
     - Make a commit when all tasks are completed with changes from the modernization plan.

3. Final verification before completing the plan:
     - **Consistency**: All expected modernization goals across all tasks are correctly and completely implemented.
     - **Completeness**: All old technology references are fully removed or replaced; no partial remnants remain in source, configuration, build, or test files.
     - If any gap is found, re-execute the relevant task before finalizing.
