---
name: bigbang_implement
description: Perform an implementation task
agent: agent
---

# Objective

> Your goal is to implement a new feature or fix a bug.

# Workflow

Perform the necessary steps in the following order:

## Access issue details

- If an issue is given to be implemented, access the issue tracker using the MCP interface and read the issue description as well as all comments to get the full context about the issue.
- If you are asked to implement an issue step only, look for hints left by a prior agent instance in the issue comments. Implement that step only.
- Check if we are working on the `main` branch. Warn if not so and offer to switch to `main` branch. If the user wants to switch, switch to the `main` branch.

## Access learnings

- Read the `LEARNINGS.md` file in the project root to get important learnings from prior implementations rounds.

## Implementation

- Perform your implementation tasks, following the best practices.
- For new features or solved bugs, add tests or test cases matching the structure of the existings tests. Be thorough, but do not cover every detail with a test. Make a reasonable decision what is necessary for being tested.

## Checks and tests

- Run the task 'Check' in vscode to perform linter checks.
- Fix all errors and warnings reported by the linter. Repeat until all checks pass.
- Run the task 'Test' in vscode to execute all tests.
- Fix any failing tests including all warnings. Repeat until all tests pass.

## Adapt documentation

- Scan the documentation for inconsistencies and necessary adaptions triggered by this issues changed.
- Adapt the documentation accordingly to reflect the changes made.
