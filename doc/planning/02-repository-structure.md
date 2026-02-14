# Step 02 — Repository Structure & Schemas

> Define and implement the BigBang repository's canonical directory structure, naming conventions, template format, project manifest schema, and composition rules.

<!-- Model: Opus | Extended Thinking: Yes -->

## Objective

Establish the foundational structure that all BigBang operations (seed, harvest, push) depend on. This includes the directory layout, the project manifest schema, template conventions, and the composition strategy for copilot-instructions.

## Implementation Details

### 2.1 Target Directory Structure

```
BigBang/
├── .github/
│   ├── copilot-instructions.md              # BigBang's own coding rules
│   └── prompts/
│       ├── bigbang_implement.prompt.md      # BigBang's own prompts
│       ├── bigbang_commit.prompt.md
│       ├── bigbang_system.prompt.md
│       ├── bigbang_maintenance.prompt.md
│       ├── bigbang_update.prompt.md
│       ├── bigbang_coverage.prompt.md
│       ├── bigbang_seed.prompt.md           # NEW: Seeding workflow
│       ├── bigbang_harvest.prompt.md        # NEW: Harvesting workflow
│       └── bigbang_push.prompt.md           # NEW: Forward-propagation
├── templates/
│   ├── copilot-instructions/
│   │   ├── base.md                          # Domain-agnostic rules
│   │   ├── python.md                        # Python-specific overlay
│   │   ├── typescript.md                    # TypeScript/Electron overlay
│   │   ├── cpp.md                           # C++/Qt overlay
│   │   └── devops.md                        # CI/DevOps overlay
│   ├── prompts/
│   │   ├── _implement.prompt.md             # Parameterized templates
│   │   ├── _commit.prompt.md                # (prefix replaced at seed time)
│   │   ├── _system.prompt.md
│   │   ├── _maintenance.prompt.md
│   │   ├── _update.prompt.md
│   │   └── _coverage.prompt.md
│   └── LEARNINGS.md                         # Empty starter for seeded projects
├── learnings/
│   ├── LEARNINGS.md                         # Cross-cutting learnings
│   ├── LEARNINGS.python.md                  # Python domain
│   ├── LEARNINGS.typescript.md              # TypeScript domain
│   ├── LEARNINGS.cpp.md                     # C++/Qt domain
│   └── LEARNINGS.devops.md                  # CI/DevOps domain
├── schemas/
│   └── manifest.schema.json                 # JSON Schema for .bigbang.json
├── scripts/
│   ├── seed.py                              # Seeding CLI
│   ├── harvest.py                           # Harvesting CLI
│   ├── push.py                              # Forward-propagation CLI
│   └── audit.sh                             # Repo audit utility
├── tests/
│   ├── test_seed.py                         # Seed script tests
│   ├── test_harvest.py                      # Harvest script tests
│   └── test_push.py                         # Push script tests
├── doc/
│   └── planning/                            # Planning documents (this folder)
├── LEARNINGS.md                             # BigBang's own learnings
├── README.md
├── pyproject.toml
└── LICENSE
```

**Design rationale**:
- `templates/` is clearly separated from BigBang's own `.github/` artifacts. BigBang uses its own prompts (with `bigbang_` prefix); templates are what gets distributed.
- `learnings/` is split by domain for easier maintenance and selective seeding.
- `schemas/` holds validation definitions used by the CLI scripts.
- `scripts/` holds the three core CLI tools plus utilities.

### 2.2 Project Manifest Schema

The `.bigbang.json` manifest lives in each seeded project and enables version tracking, drift detection, and selective operations.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BigBang Project Manifest",
  "type": "object",
  "required": ["project_name", "stack", "bigbang_version", "seeded_at"],
  "properties": {
    "project_name": {
      "type": "string",
      "description": "The project name used for prompt prefixes and template rendering",
      "pattern": "^[a-z][a-z0-9_-]*$"
    },
    "project_description": {
      "type": "string",
      "description": "One-line project description"
    },
    "stack": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["python", "typescript", "cpp", "devops"]
      },
      "minItems": 1,
      "description": "Domain stacks included in this project"
    },
    "bigbang_version": {
      "type": "string",
      "description": "BigBang version used for seeding or last push",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "seeded_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of initial seeding"
    },
    "last_harvest": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO 8601 timestamp of last harvest, null if never harvested"
    },
    "last_push": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO 8601 timestamp of last forward-propagation, null if never pushed"
    },
    "artifact_hashes": {
      "type": "object",
      "description": "SHA-256 hashes of seeded/pushed artifacts for drift detection",
      "additionalProperties": {
        "type": "string",
        "pattern": "^sha256:[a-f0-9]{64}$"
      }
    }
  }
}
```

**Example `.bigbang.json`**:

```json
{
  "project_name": "pulsar",
  "project_description": "Cryptocurrency trading heuristics generator",
  "stack": ["python"],
  "bigbang_version": "0.1.0",
  "seeded_at": "2026-02-14T12:00:00Z",
  "last_harvest": null,
  "last_push": null,
  "artifact_hashes": {
    ".github/copilot-instructions.md": "sha256:a1b2c3...",
    ".github/prompts/pulsar_implement.prompt.md": "sha256:d4e5f6...",
    ".github/prompts/pulsar_commit.prompt.md": "sha256:789abc...",
    "LEARNINGS.md": "sha256:empty..."
  }
}
```

**Key capabilities enabled**:
- **Version tracking**: Compare `bigbang_version` in manifest with current BigBang version to determine if updates are available.
- **Drift detection**: Recompute hashes of current files and compare with `artifact_hashes`. Changed files have been locally modified.
- **Selective harvesting**: Only harvest artifacts whose hashes differ from the manifest.

### 2.3 Template Naming Conventions

| Template File | Seeded File (project: "pulsar") | Rule |
|---------------|-------------------------------|------|
| `_implement.prompt.md` | `pulsar_implement.prompt.md` | `_` prefix replaced with `{project_name}_` |
| `_commit.prompt.md` | `pulsar_commit.prompt.md` | Same rule |
| `base.md` + `python.md` | `copilot-instructions.md` | Composed via concatenation |
| `LEARNINGS.md` (template) | `LEARNINGS.md` | Copied with relevant domain entries |

**Inside templates**, the following placeholders are used:

| Placeholder | Description | Example Value |
|-------------|-------------|---------------|
| `{{project_name}}` | Lowercase project identifier | `pulsar` |
| `{{project_description}}` | One-line description | `Cryptocurrency trading heuristics generator` |

**Implementation note**: Use `str.replace()` rather than a full Jinja2 templating engine. There are only 2 placeholders, and `str.replace()` avoids issues with templates that contain literal `{{` for other purposes (e.g., GitHub Actions syntax, Jinja2 examples in documentation).

### 2.4 Copilot Instructions Composition

When seeding a project, the `copilot-instructions.md` is composed by concatenating:

1. `templates/copilot-instructions/base.md` — always included
2. Selected domain overlays based on `--stack` — appended in order

**Composition format**:

```markdown
<!-- Generated by BigBang v0.1.0 — Do not edit this header -->
<!-- Stack: python -->

# Rules

## General

[contents of base.md]

## Python

[contents of python.md]
```

The header comment enables the push tool to identify BigBang-managed files and parse the stack configuration.

**Overlay design principle**: Each overlay is self-contained and additive. It should never contradict the base rules, only extend them with domain-specific guidance. If a domain needs to override a base rule, the override should be explicit (e.g., "For Python projects, prefer `pathlib` over `os.path` — this overrides the general filesystem guidance").

### 2.5 Learnings File Convention

**In BigBang** (`learnings/` directory):
- One file per domain: `LEARNINGS.python.md`, `LEARNINGS.typescript.md`, etc.
- One cross-cutting file: `LEARNINGS.md` for domain-agnostic learnings.
- Format: Markdown list items, one learning per item.

```markdown
# Learnings — Python

- Always use `pathlib` instead of `os.path` for file path manipulation. It provides a cleaner, object-oriented API.
- When using `pydantic`, prefer `model_validator` over `__init__` for complex initialization logic.
- Use `structlog` for logging in production code. It provides structured, machine-parseable log output.
```

**In seeded projects** (`LEARNINGS.md`):
- Single file containing all relevant learnings for the project's stack.
- Entries may have optional domain tags: `- [python] Always use pathlib...`
- The tag helps harvesting classify entries back into the correct domain file.

**During seeding**: Relevant domain files are concatenated into a single `LEARNINGS.md`:
```markdown
# Learnings

## General

[contents of learnings/LEARNINGS.md]

## Python

[contents of learnings/LEARNINGS.python.md]
```

### 2.6 Python Project Setup

BigBang needs a minimal Python project setup for its CLI scripts:

```toml
[project]
name = "bigbang"
version = "0.1.0"
description = "Centralized knowledge & template repository for AI coding agent artifacts"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "jsonschema>=4.20",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
]

[project.scripts]
bigbang-seed = "scripts.seed:main"
bigbang-harvest = "scripts.harvest:main"
bigbang-push = "scripts.push:main"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### 2.7 VSCode Tasks

Define VSCode tasks for the BigBang project itself:

| VSCode Task | Command | Description |
|-------------|---------|-------------|
| Check | `ruff check . && mypy scripts/` | Run linter and type checker |
| Test | `pytest tests/ -v` | Run all tests |
| Coverage | `pytest tests/ --cov=scripts --cov-report=html:build/coverage` | Generate coverage report |

## Tests Required

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Schema validity | `manifest.schema.json` is valid JSON Schema | Validates against meta-schema |
| Template rendering | `{{project_name}}` substitution produces valid files | No remaining placeholders |
| Composition | Base + overlay concatenation produces valid markdown | Well-formed document |
| Overlay isolation | Each overlay file parses as valid markdown independently | No broken references |

## Acceptance Criteria

- [ ] Full directory structure created and committed
- [ ] `schemas/manifest.schema.json` defined and valid against JSON Schema meta-schema
- [ ] Template prompt files created from existing BigBang prompts (parameterized with `{{project_name}}`)
- [ ] Copilot-instructions split into `base.md` + domain overlays
- [ ] `pyproject.toml` created; `pip install -e ".[dev]"` succeeds in a virtual environment
- [ ] VSCode tasks defined in `.vscode/tasks.json`
- [ ] Naming conventions documented in `README.md`

## Dependencies

- [Phase 01](01-initial-consolidation.md) — Consolidated artifacts needed as input for templates and learnings.

## Hints

- Keep the manifest schema minimal. Start with the fields shown above; extend only when a concrete need arises.
- `str.replace()` is sufficient for template rendering. Switch to Jinja2 only if template complexity grows beyond 3-4 placeholders.
- The `artifact_hashes` in the manifest use relative paths from the project root as keys. This keeps the manifest portable across machines.

## Risk & Complexity Assessment

**Overall: Medium**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Over-engineering the manifest schema | Medium | Medium | Start minimal, extend when needed |
| Template parameterization too limited | Low | Low | Only 2 placeholders needed now; easy to add more later |
| Copilot-instructions composition conflicts | Low | Medium | Overlays are additive only; no overrides without explicit documentation |
| `str.replace()` collisions with literal `{{` | Low | Low | Unlikely in markdown agent prompts; switch to Jinja2 if it occurs |
