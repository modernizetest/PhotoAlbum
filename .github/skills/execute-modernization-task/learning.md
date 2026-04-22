# Learning Template

Use this file to capture reusable learnings discovered while executing modernization tasks.

## Build

### Entry Template
- **Task:** <task id or name>
- **Scope:** <module or path>
- **Command:** `<exact build command>`
- **Working directory:** <relative path or repository root>
- **Prerequisites:** <sdk/env/service requirements>
- **Outcome:** <passed/failed + short note>

## Test

### Entry Template
- **Task:** <task id or name>
- **Scope:** <module or path>
- **Command:** `<exact test command>`
- **Working directory:** <relative path or repository root>
- **Prerequisites:** <service/dev server/test data requirements>
- **Outcome:** <passed/failed + short note>

## Commands

### Entry Template
- **Task:** <task id or name>
- **Purpose:** <what the command achieves>
- **Command:** `<exact command and arguments>`
- **Working directory:** <relative path or repository root>
- **When to use:** <trigger condition>
- **Outcome:** <success + caveat>

## Observations

### Entry Template
- **Task:** <task id or name>
- **Scope:** <module path or repository-wide>
- **Observation:** <co-change rule, module convention, prerequisite, or coupling>
- **Implication:** <how future changes should adapt>

## Technical Concepts

### Entry Template
- **Task:** <task id or name>
- **Type:** <architecture|framework-pattern|integration-model|domain-invariant>
- **Scope:** <module, boundary, or repository-wide>
- **Concept:** <identified technical concept>
- **Migration implication:** <how this affects migration decisions>

## Migration Patterns

### Entry Template
- **Task:** <task id or name>
- **Scenario:** <source -> target>
- **Preconditions:** <must-hold conditions>
- **Steps:**
  1. <step>
  2. <step>
- **Files touched:** <key files or file types>
- **Variations:** <edge cases and handling>

## Skill Issues

### Entry Template
- **Task:** <task id or name>
- **Skill:** <skill name>
- **Severity:** <broken|partial|context-mismatch>
- **Expected:** <what should have happened>
- **Observed issue:** <what went wrong>
- **Workaround:** <none or alternative approach>

## Mistakes

### Entry Template
- **Task:** <task id or name>
- **What happened:** <mistake>
- **Why it was wrong:** <error/outcome>
- **Correct approach:** <fix>

## Loop Failures

### Entry Template
- **Task:** <task id or name>
- **Step that failed:** <description>
- **Attempts:** <count>
- **Attempt summary:** <what was tried>
- **Root cause analysis:** <likely cause>
- **Recommendation:** <next action for future agent/human>

## Rules

- Keep entries concise and actionable.
- Do not store secrets, tokens, passwords, or full connection strings.
- Prefer parameterized placeholders (for example `$TOKEN`) over expanded secret values.
- Update existing entries when refining the same task outcome; append new entries for distinct tasks.
