---
name: {{project_name}}_update
description: Update the project dependencies and perform necessary code changes to keep the project up to date with the latest versions of libraries and tools.
agent: agent
---

# Objective

> Your goal is to update the project dependencies to their latest versions and make any necessary code changes to ensure compatibility with the new versions. 

- Stick to stable or LTS versions of dependencies, unless there is a compelling reason to use a newer version (e.g., critical bug fixes, security patches, or significant performance improvements).

# Workflow

## Pre checks

- Check if you are working on the `main` branch. If not, warn and offer to switch to `main` before proceeding.

## Dependency Update

- Update the dependencies in the relevant files, like `pyproject.toml`, `requirements.txt`, `package.json` or any other dependency management files, to their latest stable or LTS versions. This includes both direct dependencies and any relevant development dependencies. 
- Make sure to check the release notes and changelogs of the updated dependencies for any breaking changes, deprecations, or important updates that may require code changes in the project.

## Checks and tests

- Run all checks and tests. Fix **all** warnings and **all** errors before proceeding to the next step. This includes 
  - linting, 
  - type checking, 
  - unit tests, 
  - integration tests, 
  - any other checks configured in the project.
- Repeat until all warnings and errors in both checks and tests are resolved.

## Commit and push

- Only if you had to make changes:
  - Create a branch named `xx-update-YYYYMMDD-hhmmss` (replace `YYYYMMDD` with the current date and `hhmmss` with the current time and keep the `xx-` prefix).
  - Commit the changes with a message that clearly describes what was fixed, e.g., "Fix linting and type errors". Split into multiple commits if there are multiple distinct issues.
  - Push the committed changes to the remote repository.
  - Create a pull request from the new branch to `main` with the same name as the branch.
  - Label the pull request with the `update` label.

  # Hints

  - Use update tools like `pip-tools`, `npm-check-updates`, or similar tools for other languages to help with updating dependencies and managing compatibility issues.
  - Add these tools to the project if they are not already present, to facilitate future updates and maintenance.
