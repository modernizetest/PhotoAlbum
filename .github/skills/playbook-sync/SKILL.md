---
name: playbook-sync
description: Generate or update modernization playbook from document sources
---

# Playbook Sync

This skill analyzes document content to generate a comprehensive modernization playbook with migration policies, code instructions, resource configurations, and migration patterns.

## User Input

- output-path (Mandatory): The folder to save the playbook files
- source-file-path (Mandatory): Path to the source file containing the document content

## Principles

- **No Hallucination**: Only include policies and content explicitly present in the source document. Do not invent, assume, or add information not found in the source.
- **No Policy Inheritance**: Do not copy, inherit, or infer content from policy files, templates, or prior knowledge. Only use content explicitly present in ${source-file-path}.
- **Concise Output**: Keep generated content concise and focused. Omit sections that have no corresponding content in the source rather than adding placeholder text.
- **Source Fidelity**: If a policy category (e.g., Compliance Requirements, Rollback Strategy) is not mentioned in the source, do not include that section in the output.
- **Incremental Updates**: If output files already exist, only update sections with new or changed content from the source file. Preserve all existing content that is not affected by the source changes.
- **Direct Policy Output**: Output should contain only the truth and target record. Do not include reasons, rationale, or explanations behind policies—just state the policy itself.

## Workflow

Given the user input, follow these steps:

1. **Read Source Content**
   - Read the content from ${source-file-path}
   - This file contains the playbook documentation from GitHub issues or markdown files
   - Check if output files already exist in ${output-path}
   - If existing files are found, read their current content for comparison

2. **Analyze Content Structure**
   - Identify sections related to:
     - Migration policies and standards
     - Code styles and best practices
     - Azure landing zone
     - Migration patterns with sample code
     - Assessment criteria

3. **Generate modernization-policy.md**
   - Extract migration policy information as defined in the playbook spec
   - Look for content about:
     - Approved Azure Services
     - Service replacement patterns
     - Prohibited Technologies (legacy app servers, outdated versions, vulnerable frameworks)
     - Required Technologies (Java versions, Spring Boot, container images, standards)
     - Security Requirements (authentication, encryption, Key Vault, network security)
     - Compliance Requirements (SOC 2, PCI DSS, HIPAA, GDPR, SOX, Azure Policy)
     - Deployment Standards (CI/CD pipelines, gates, strategies, environments)
     - Rollback Strategy (triggers, procedures, communication, runbooks, testing)
   - Use the template [modernization-policy](modernization-policy.md)
   - If file exists: merge new content into existing file, preserving unchanged sections
   - If file does not exist: create new file
   - Save to ${output-path}/modernization-policy.md
   - DO NOT include detailed code samples or configurations in this file - those belong in other files

4. **Generate modernization-code-instruction.md**
   - Extract code style, best practices, and security guidance
   - Look for:
     - Coding standards, conventions, samples
  - **Important**: ONLY add content explicitly present in ${source-file-path}. Do not import or inherit any content from policy files.
   - Use the template [code-instruction](modernization-code-instruction.md)
   - If file exists: merge new content into existing file, preserving unchanged sections
   - If file does not exist: create new file
   - Save to ${output-path}/modernization-code-instruction.md

5. **Generate azure-landing-zone.md**
   - Extract Azure service configurations and resource information
   - Look for:
     - Azure resource configurations
     - Landing zone information
     - Network architecture, RBAC, Identity
     - Resource naming conventions
   - Use the template [azure-landing-zone](azure-landing-zone.md)
   - If file exists: merge new content into existing file, preserving unchanged sections
   - If file does not exist: create new file
   - Save to ${output-path}/azure-landing-zone.md

6. **Generate assess-instruction.md**
   - Extract criteria for assessment
   - Look for:
     - Assessment scoring criteria
     - Classification rules
     - Technical debt identification
     - Complexity metrics
     - Migration readiness indicators
   - Use the template [assess-instruction](assess-instruction.md)
   - If file exists: merge new content into existing file, preserving unchanged sections
   - If file does not exist: create new file
   - Save to ${output-path}/assess-instruction.md

7. **Generate Migration Pattern Skills**
   - If migration patterns with sample code or detailed guidance are found:
     - Create a SKILL.md file in path: ${output-path}/skills/{migration-pattern-name}/SKILL.md
   - Use the template [modernization-skill](modernization-skill.md) to generate SKILL.md
   - If skill file exists: merge new content into existing file, preserving unchanged sections
   - If skill file does not exist: create new file
   - Example folder structure:
     ```
     skills/
       pattern-cache-migration/
         SKILL.md
       pattern-database-migration.md
     ```

## Completion Criteria

1. All applicable playbook files are generated in ${output-path}
2. Content is properly categorized into the correct files
3. Return success message listing all generated files
