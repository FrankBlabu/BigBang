# BigBang Learnings

This directory contains domain-classified learnings extracted from all repositories in the portfolio.

## Structure

```
learnings/
├── LEARNINGS.python.md      # Python-specific learnings
├── LEARNINGS.typescript.md  # TypeScript/Node.js learnings
├── LEARNINGS.devops.md      # DevOps and deployment learnings
└── LEARNINGS.general.md     # Cross-cutting, universal learnings
```

## Domain Classification

Learnings are classified by domain using keyword detection and manual review:

- **python:** pydantic, pytest, ruff, mypy, pandas, numpy, HDF5, asyncio
- **typescript:** React, Electron, Theia, GraphQL, npm, Vitest, TypeScript
- **devops:** Docker, CI/CD, electron-builder, packaging, deployment
- **general:** Architecture, testing patterns, documentation, accessibility

## Usage in Projects

During project initialization (Phase 03), the seeding CLI will:

1. Determine the project's primary stack
2. Merge relevant domain learnings into the project's `LEARNINGS.md`
3. Include general learnings that apply to all projects

Example for a Python project:
```
LEARNINGS.md = LEARNINGS.general.md + LEARNINGS.python.md
```

Example for a TypeScript project:
```
LEARNINGS.md = LEARNINGS.general.md + LEARNINGS.typescript.md
```

## Harvesting New Learnings (Phase 04)

When projects accumulate new learnings, the `bigbang-harvest` tool will:

1. Extract new entries from the project's `LEARNINGS.md`
2. Classify them by domain (with agent assistance)
3. Append them to the appropriate BigBang learning file
4. Remove duplicates

## Learning Entry Format

Each learning is a single bullet point with:
- Clear, actionable insight
- Context about when it applies
- Specific examples or code snippets when helpful

```markdown
- Ruff outdated rules: Rules `ANN101` and `ANN102` are no longer supported in recent ruff versions. Remove them from ignore list to avoid warnings.
```

## Statistics

Current learning count by domain:

| Domain | Entries | Source Projects |
|--------|---------|----------------|
| Python | 31 | Pulsar, ProjectZ, BigBang |
| TypeScript | 69 | ProjectZ, ParabelLab |
| DevOps | 15 | Pulsar, ProjectZ |
| General | 79 | All projects |
| **Total** | **194** | (after deduplication) |

## Maintaining Learnings

To keep learnings valuable:

1. **Add tags:** Prefix domain-specific entries with `[domain]` in project LEARNINGS.md
2. **Periodic harvesting:** Run `bigbang-harvest` quarterly to extract new learnings
3. **Remove outdated:** Mark deprecated learnings with ~~strikethrough~~ or remove them
4. **Merge duplicates:** During harvesting, consolidate similar entries

## See Also

- [doc/audit-report.md](../doc/audit-report.md) — Initial consolidation details
- [doc/planning/04-back-propagation.md](../doc/planning/04-back-propagation.md) — Harvesting workflow
