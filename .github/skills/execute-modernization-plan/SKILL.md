---
name: execute-modernization-plan
description: Execute the modernization plan by running the tasks listed in the plan
---

# Execute modernization plan

This skill is used to execute a modernization plan to migrate the a given project to Azure

## User Input

- modernization-description: The user intent to run the modernization plan
- modernization-work-folder (Mandatory): The folder to save the modernization plan
- programming-language: Input by user or autodetect by context

You **MUST** consider the user input before proceeding.

## Workflow

Given that modernization description, do this:
1. Read ${modernization-work-folder}/plan.md and ${modernization-work-folder}/clarifications.json, you can have an overview with the modernization plan

2. Load all tasks from ${modernization-work-folder}/tasks.json and execute them one by one in the order they appear in the `tasks` array in tasks.json (do not reorder tasks):
    - Refer to the json schema tasks-schema.json to update the tasks.json
    - Before starting a task, update the tasks.json status to "started"
    - After completing a task, **YOU MUST** update the tasks.json status to exactly one of: "success", "failed", or "skipped" (do NOT use "completed" or any other value) with a task summary and task successCriteriaStatus
    - Do not stop task execution until all tasks are completed or any task fails. If one task is started, wait for final result with success, skipped or failed.
    - Choose the right custom agent to execute the task based on the `type` field of the task in tasks.json, and call the custom agent with the prompt according to the task type and information in tasks.json. The custom agent will return the execution result including whether the task is successful, skipped or failed, and a summary of the execution.
        1) Custom agent usage to complete the infrastructure task:
        For tasks with `"type": "infrastructure"` in tasks.json, call custom agent `modernize-azure-platform-engineer` with prompt:

            ```md
            Generate IaC files to ./infra/ and provision Azure infrastructure.
            iacType: {iacType}
            provision: {provision}
            ```

        2) Custom agent usage to complete the coding task:
            1) You must call custom agent general-purpose for upgrade task of java with below prompt according to information from tasks.json, the upgrade task include java-version-upgrade, spring-boot-upgrade, spring-framework-upgrade and jakarta-ee-upgrade
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
                {{v1}} and {{v2}} is the version and {{v2}} can be 'latest version' of it is not specified

            2) For .NET upgrade tasks (tasks with `"type": "upgrade"` that target .NET version upgrades), you must call custom agent `modernize-dotnet-upgrade-engineer` with below prompt:
                ```md
                Upgrade this .NET project using your MCP-based workflow. Run in Automatic flow mode — do NOT pause for user input at any point. After all tasks complete, clean up any .github/upgrades/ and .github/agents/ artifacts created by the MCP server

                Upgrade task details:
                  - TaskId: {task id from `id` field}
                  - Description: {task description from `description` field}
                  - Requirements: {from `requirements` field}
                  - Environment Configuration: {from `environmentConfiguration` field, may be null}
                  - Success Criteria: {from `successCriteria` field}

                CRITICAL: This is a fully autonomous execution. Never ask the user for confirmation, never pause for review, never present options. Accept all defaults and complete the entire upgrade end-to-end.
                ```

            3) You must call custom agent general-purpose for transform task with below prompt according to information from tasks.json
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

            4) Only use the skill execute-modernization-task in custom agent to do the code change for each task

        5. Custom agent usage to complete the security task:
            You must call custom agent general-purpose for security task with below prompt according to information from tasks.json
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
        {{security-skill-for-the-task}} is resolved from the `skills` array in the security task in tasks.json. Each entry in `skills` is an object with `name` and `location` fields. If the task has multiple skills, combine all skill names into a single comma-separated list (e.g., `validate-cves-and-fix, additional-security-scan`). If there is only one skill, use its `name` value directly (e.g., `validate-cves-and-fix`).

        6. Custom agent usage to complete the integration test task:
        For tasks with `"type": "integrationTest"` in tasks.json, extract the layers array from the task (e.g., [1, 2]).

        **IMPORTANT**: Use the Agent tool to spawn agents in FOREGROUND mode (do NOT use run_in_background parameter).
        Loop through each layer and spawn one agent per layer. Wait for ALL agents to complete before marking the task as successful.

        For EACH layer N in the layers array, spawn an Agent tool with this prompt:

                ```md
                **CONTEXT:**
                This is a Java project that was migrated to Azure.
                - Migration completed: Azure services are now in use
                - Build tool: {maven or gradle from project analysis}
                - Work folder: {modernization-work-folder from input}
                {if this is Layer 2 and Layer 1 was in the layers array}
                - Layer 1 status: COMPLETED (TestContainers tests exist)
                {end if}

                **YOUR TASK:**
                Generate Layer {N} integration tests by calling the /integration-tests skill.

                **SKILL INVOCATION:**
                Call /integration-tests with:
                - layer={N}
                - modernization-work-folder={modernization-work-folder from input}
                - test-root={current working directory}
                {if Layer 3}
                - azure-config={azure-config from task if available}
                {end if}

                {if N == 1}
                **LAYER 1 REQUIREMENTS:**
                - Generate TestContainers-based integration tests
                - Layer 1 uses Java test classes (*L1Test.java)
                - NO @MockBean or @Mock on migrated Azure SDK clients
                - Tests must use real TestContainers (Azurite, Service Bus emulator, etc.)

                **VERIFICATION REQUIREMENTS:**
                Before marking complete, verify:
                1. Test classes exist (*L1Test.java in src/test/java)
                2. Classes have @Tag("Layer1") or @Category(Layer1.class)
                3. TestContainers used (no mocking of Azure SDK clients)
                4. Tests compile and run
                5. Files COMMITTED to git (not just created)

                **VERIFICATION COMMANDS:**
                Run these commands and check output BEFORE claiming success:
                ```bash
                # Verify test files exist
                find src/test/java -name "*L1Test.java" -type f

                # Verify git commit
                git log --oneline --all --grep="Layer 1" -n 1
                git show --stat HEAD
                ```

                **SUCCESS CRITERIA:**
                Only mark COMPLETE when verification commands show expected output.
                {end if}

                {if N == 2}
                **LAYER 2 REQUIREMENTS:**
                - Generate shell-based smoke tests (NOT Java test classes)
                - Layer 2 uses docker-compose.smoke.yml + run-layer2-tests.sh/.ps1
                - Requires EXACTLY 3 commits in specific order

                **VERIFICATION REQUIREMENTS:**
                Before marking complete, verify:
                1. Artifacts: docker-compose.smoke.yml, run-layer2-tests.sh, run-layer2-tests.ps1 exist
                2. NO *L2Test.java files (Layer 2 uses shell, not Java test classes)
                3. 3-Commit Structure:
                   - Commit 1: [layer-2] artifacts
                   - Commit 2: [smoke-test] auth changes
                   - Commit 3: [smoke-test] restore (reverts commit 2, references its SHA)
                4. Smoke test executes successfully (exit code 0)

                **VERIFICATION COMMANDS:**
                Run these commands and check output BEFORE claiming success:
                ```bash
                # Verify artifacts exist
                ls -la src/test/resources/docker-compose.smoke.yml
                ls -la {modernization-work-folder}/integration-tests/run-layer2-tests.sh

                # Verify NO test classes for Layer 2
                find src/test/java -name "*L2Test.java" -type f  # should return NOTHING

                # Verify 3-commit structure
                git log --oneline --all | grep -E "\[layer-2\]|\[smoke-test\]"
                # Should show 3 commits
                ```

                **SUCCESS CRITERIA:**
                Only mark COMPLETE when:
                - All 3 commits exist in correct order
                - Verification commands show expected output
                - Smoke test exit code 0
                {end if}

                {if N == 3}
                **LAYER 3 REQUIREMENTS:**
                - Generate Azure integration tests (connects to real Azure services)
                - Tests use *L3Test.java naming
                - Tests have @Tag("Layer3") or @Category(Layer3.class)
                {end if}

                {if N == 4}
                **LAYER 4 REQUIREMENTS:**
                - Generate behavioral comparison tests
                - Tests use *L4Test.java naming
                - Tests have @Tag("Layer4") or @Category(Layer4.class)
                {end if}

                Task details for reference:
                - TaskId: {id from task}
                - Description: {description from task}
                - Requirements: {requirements from task}
                - Test Layer: {N}
                ```

        **After ALL layer agents complete:**
        1. Wait for ALL agents to return results
        2. Review verification command outputs from each agent
        3. Check git log to confirm commits exist
        4. Do NOT exit until verification confirmed for all layers

        **Safety check before marking integration test task complete:**
        ```bash
        git log --oneline -10 | grep -E "\[layer-.*\]|\[smoke-test\]"
        # Should show commits for all requested layers
        ```
        7. Custom agent usage to complete containerization or deploy task:
        Custom agent modernize-azure-deploy-developer for containerization or deploy, call the agent with prompt with below format
                ```md
                Deploy the application to Azure
                ```
            or deploy to existing azure resources with below format if the plan.md contains the section of Azure Environment with Subscription ID and Resource Group:
                ```md
                Deploy the application to existing Azure resources. Subscription ID: {subscriptionId}, Resource Group: {resourceGroup}
    - You needn't generate any other documents except the "modernization-summary.md" for each task
    - **YOU MUST** update the tasks.json with the final status of each task (success, failed, or skipped)
    - Make a commit when all tasks are completed with the changes made in the modernization plan.            ```

7. Final verification before completing the plan:
   After all tasks have been executed, perform an overall verification:
   - **Consistency**: All expected modernization goals across all tasks are correctly and completely implemented
   - **Completeness**: All old technology references are fully removed or replaced — no partial remnants remain in source files, configuration files, build files, or test files
   - If any gap is found, re-execute the relevant task to address it before finalizing
