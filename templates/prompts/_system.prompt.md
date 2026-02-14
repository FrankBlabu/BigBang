---
name: {{project_name}}_system
description: Commit changes in the general project utilities and prompts
agent: agent
---

# Objective

> Your goal is to commit changes in the agent based coding related project files

# Workflow

- Check for changes in the prompting and instruction files. This includes 
  - everything in the `.github` directory,
  - `AGENTS.md` (if existing),
  - `CLAUDE.md` (if existing) and similar files.
- Only if there were changes:
  - Create a branch named `xx-utilities-YYYYMMDD-hhmmss` (replace `YYYYMMDD` with the current date and `hhmmss` with the current time and keep the `xx-` prefix).
  - Commit the changes with a message that clearly describes what was changed. Split into multiple commits if there are multiple distinct issues.
  - Push the committed changes to the remote repository.
  - Create a pull request from the new branch to `main` with the same name as the branch.
  - Label the pull request with the `utilities` label.
