# Step 06 — Ongoing Governance

> Define the governance model, contribution workflow, CI/CD checks, and maintenance cadence that keep BigBang healthy as the canonical source of truth.

<!-- Model: Sonnet | Extended Thinking: No -->

## Objective

Establish the processes, automation, and conventions that ensure BigBang remains reliable, consistent, and up-to-date as the number of seeded projects grows and artifacts evolve over time.

## Implementation Details

### 6.1 Contribution Workflow

All changes to BigBang follow this workflow:

```
Developer / Agent
       │
       ▼
  Feature Branch
       │
       ▼
  CI Checks (auto)  ──── FAIL ──── Fix & Retry
       │
      PASS
       │
       ▼
  Pull Request
       │
       ▼
  Review (human or agent-assisted)
       │
       ▼
  Merge to main
       │
       ▼
  Version Bump (if applicable)
```

**Branch naming**:
- Harvested content: `harvest/{project_name}-YYYYMMDD`
- Template improvements: `templates/{description}`
- Infrastructure changes: `infra/{description}`
- Documentation: `docs/{description}`

**For solo developer workflow**: Skip formal PR reviews. Rely on CI gates and agent-assisted review. Use PRs mainly for history and change tracking.

### 6.2 CI Checks

Automated checks that run on every commit/PR to BigBang:

| Check | Tool | What It Validates |
|-------|------|-------------------|
| Template rendering | Python script | All templates render without error for a test project |
| Placeholder completeness | grep | No `{{` remains in rendered output |
| Schema validation | jsonschema | `manifest.schema.json` is valid JSON Schema |
| Learnings format | Python script | Each entry follows `- [tag] description` or `- description` format |
| Prompt frontmatter | Python script | All `.prompt.md` files have valid YAML frontmatter |
| Python linting | ruff | Code quality for scripts |
| Python types | mypy | Type correctness for scripts |
| Tests | pytest | All unit tests pass |

**Implementation as GitHub Actions** (`.github/workflows/ci.yml`):

```yaml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy scripts/
      - run: pytest tests/ -v
      - run: python scripts/validate_templates.py
```

**`scripts/validate_templates.py`** — A validation script that:
1. Renders all templates with a test project name ("testproject", stack: all).
2. Checks for remaining `{{` placeholders.
3. Validates YAML frontmatter in prompt files.
4. Validates learnings file format.

### 6.3 Maintenance Cadence

| Cadence | Activity | How |
|---------|----------|-----|
| Per commit | CI checks | Automated via GitHub Actions |
| Monthly | Harvest from active projects | Run `bigbang_harvest.prompt.md` per project |
| Monthly | Review and consolidate learnings | Manual review of `learnings/` files |
| Monthly | Check for stale or contradictory learnings | Agent-assisted review |
| Quarterly | Review copilot-instructions for currency | Are rules still best practice? |
| Quarterly | Review prompt templates for improvements | Any workflow steps outdated? |
| Per release | Version bump and push preview | `bigbang-push-all --dry-run` to preview impact |

**Automation**: Create a GitHub Action or scheduled script that opens a reminder issue monthly:

```yaml
# .github/workflows/maintenance-reminder.yml
name: Monthly Maintenance Reminder
on:
  schedule:
    - cron: "0 9 1 * *"  # First of each month at 9am
jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          gh issue create \
            --title "Monthly maintenance — $(date +%B\ %Y)" \
            --body "Time for the monthly BigBang maintenance cycle. See doc/planning/06-governance.md for the checklist." \
            --label maintenance
```

### 6.4 Conflict Resolution Policy

When BigBang and a seeded project disagree, the following hierarchy applies:

| Scenario | Authority | Rationale |
|----------|-----------|-----------|
| Cross-cutting coding rules | BigBang | These are universal best practices |
| Domain-specific rules | BigBang (default), project can override | BigBang represents "best practice" |
| Project-specific customizations | Project | Projects have unique needs |
| Learnings | Both contribute | Both can add; BigBang deduplicates |
| Prompt workflow steps | BigBang (general), project (specific) | General workflow from BigBang, project adds specifics |

**Override mechanism**: A project can mark sections in `copilot-instructions.md` with override comments:

```markdown
<!-- bigbang:override-start -->
# Custom Rules
These rules override BigBang defaults for this project.
- Use unittest instead of pytest (legacy codebase requirement)
<!-- bigbang:override-end -->
```

The push tool respects these markers and does not overwrite content between them.

### 6.5 Versioning and Changelog

**Version format**: Semantic versioning (MAJOR.MINOR.PATCH) in `pyproject.toml`.

| Bump | When | Example |
|------|------|---------|
| MAJOR | Breaking changes to manifest schema or template contract | Changing placeholder syntax |
| MINOR | New features or templates that seeded projects should adopt | Adding `_review.prompt.md` |
| PATCH | Fixes, clarifications, new learnings | Typo fixes, new domain learnings |

**Changelog** (`CHANGELOG.md`):

```markdown
# Changelog

## [0.2.0] — 2026-03-15

### Added
- New `_review.prompt.md` template for code review workflow
- DevOps domain overlay for copilot-instructions

### Changed
- Improved commit workflow in `_commit.prompt.md` — added PR creation step

### Fixed
- Typo in Python overlay: "pydandic" → "pydantic"

## [0.1.0] — 2026-02-14

### Added
- Initial repository structure
- Core templates: implement, commit, system, maintenance, update, coverage
- Seeding CLI and agent prompt
```

### 6.6 `bigbang_audit.prompt.md` — Self-Audit Prompt

A new agent prompt for periodic self-auditing:

```markdown
---
name: bigbang_audit
description: Audit BigBang repository health and consistency
agent: agent
---

# Objective

> Your goal is to verify the health and consistency of the BigBang repository.

# Workflow

## Template validation

- Render all templates with test parameters and verify no placeholders remain.
- Verify all prompt templates have valid YAML frontmatter.
- Verify copilot-instruction overlays are self-contained and do not contradict each other.

## Learnings review

- Check for duplicate or near-duplicate entries across domain files.
- Check for outdated entries (reference deprecated tools, old versions, etc.).
- Check for contradictory entries within the same domain.

## Schema validation

- Validate `manifest.schema.json` against the JSON Schema meta-schema.
- Verify example manifests are valid against the schema.

## Drift detection (if registry exists)

- For each registered project, check if `.bigbang.json` exists.
- Report which projects are behind the current BigBang version.
- Report which projects have local modifications to BigBang-managed files.

## Report

- Generate a health report summarizing findings.
- Propose fixes for any issues found.
```

### 6.7 Documentation Standards

All BigBang artifacts must follow these documentation standards:

| Artifact | Documentation Requirement |
|----------|--------------------------|
| Template files | Header comment explaining purpose and available placeholders |
| Domain overlays | Introduction paragraph explaining when this overlay applies |
| Learnings entries | Clear, actionable single-sentence descriptions |
| Scripts | Module docstring, function docstrings, CLI help text |
| Schemas | `description` field on every property |
| Planning docs | Follow the numbered convention with standard sections |

**README.md structure**:

```markdown
# BigBang

One-paragraph description.

## Quick Start

### Seed a new project
bigbang-seed --name myproject --stack python /path/to/project

### Harvest from a project
bigbang-harvest /path/to/project

### Push updates to a project
bigbang-push /path/to/project

## Documentation

- [Planning Documents](doc/planning/00-overview.md)
- [Template Reference](templates/README.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
```

## Tests Required

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Template validation script | Run `validate_templates.py` | All templates valid |
| CI workflow syntax | Validate GitHub Actions YAML | Valid workflow |
| Learnings format | Run learnings linter on all files | All entries correctly formatted |
| Schema meta-validation | Validate schema against meta-schema | Valid JSON Schema |

## Acceptance Criteria

- [ ] CI workflow defined in `.github/workflows/ci.yml`
- [ ] Template validation script created and passing
- [ ] Learnings lint script created and passing
- [ ] Maintenance reminder workflow configured
- [ ] Conflict resolution policy documented
- [ ] Override mechanism (`bigbang:override-start/end`) documented
- [ ] `CHANGELOG.md` template created
- [ ] `bigbang_audit.prompt.md` created and functional
- [ ] `README.md` includes quickstart instructions
- [ ] Versioning strategy documented

## Dependencies

- [Phase 02](02-repository-structure.md) — Repository structure must be finalized.
- [Phase 03](03-project-initialization.md) — Seeding must work for CI to validate templates.
- [Phase 04](04-back-propagation.md) — Harvesting workflow must exist for governance to manage it.
- [Phase 05](05-forward-propagation.md) — Push workflow must exist for governance to manage it.

## Hints

- Keep governance lightweight for a solo developer. The CI gates and monthly reminders are the minimum viable governance.
- The `bigbang_audit.prompt.md` is the most valuable governance tool — it offloads the review burden to the coding agent.
- Start without formal code review on PRs. Add it only if the team grows or quality issues emerge.
- The override mechanism (`bigbang:override-start/end`) is simple but effective. It avoids complex merge logic by clearly marking protected sections.

## Risk & Complexity Assessment

**Overall: Low**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Governance becomes overhead | Medium | Low | Keep it lightweight; CI + monthly reviews |
| Maintenance cadence not followed | Medium | Low | Automated reminders via GitHub Actions |
| Override markers not respected | Low | Medium | Push tool explicitly checks for markers |
| Changelog falls behind | Medium | Low | Include changelog update in commit prompt workflow |
| CI flaky tests | Low | Low | Keep tests deterministic; no network dependencies |
