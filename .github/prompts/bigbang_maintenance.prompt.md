---
name: pulsar_maintenance
description: Perform maintenance tasks to keep the project in good shape
agent: agent
---

# Objective

> Your goal is to check and improve the quality of the project.

# Workflow

## Checks and tests

- Check if you are working on the `main` branch. If not, warn and offer to switch to `main` before proceeding.
- Run all checks and tests. Fix **all** warnings and **all** errors before proceeding to the next step. This includes 
  - linting, 
  - type checking, 
  - unit tests, 
  - integration tests, 
  - any other checks configured in the project.

## Commit and push

- Only if you had to make changes:
  - Create a branch named `xx-maintanance-YYYYMMDD-hhmmss` (replace `YYYYMMDD` with the current date and `hhmmss` with the current time and keep the `xx-` prefix).
  - Commit the changes with a message that clearly describes what was fixed, e.g., "Fix linting and type errors". Split into multiple commits if there are multiple distinct issues.
  - Push the committed changes to the remote repository.
  - Create a pull request from the new branch to `main` with the same name as the branch.
  - Label the pull request with the `maintenance` label.
