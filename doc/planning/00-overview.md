# Project Big Bang — Planning Overview

> Centralized knowledge & template repository for AI coding agent artifacts. Consolidates copilot instructions, prompt templates, and learnings across a portfolio of software projects.

## Vision

Big Bang is a canonical meta-repository that consolidates, versions, and distributes AI coding agent artifacts across a portfolio of projects. It acts as the single source of truth for:

- **Copilot instructions** — coding rules and best practices, split by domain
- **Prompt templates** — reusable agent workflow definitions for recurring tasks
- **Learnings** — domain-specific knowledge accumulated by coding agents over time

The system supports a complete lifecycle: initial consolidation of existing artifacts, bootstrapping new projects, harvesting improvements back, and forward-propagating updates.

## Architecture Summary

```
                         ┌─────────────────────────┐
                         │      BigBang Repo        │
                         │                          │
                         │  templates/              │
                         │    copilot-instructions/  │
                         │      base.md             │
                         │      python.md           │
                         │      typescript.md       │
                         │      cpp.md              │
                         │      devops.md           │
                         │    prompts/              │
                         │      _implement.prompt.md│
                         │      _commit.prompt.md   │
                         │      ...                 │
                         │  learnings/              │
                         │    LEARNINGS.python.md   │
                         │    LEARNINGS.typescript.md│
                         │    ...                   │
                         │  schemas/                │
                         │    manifest.schema.json  │
                         │  scripts/                │
                         │    seed.py               │
                         │    harvest.py            │
                         │    push.py               │
                         └────────┬────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                  │
                ▼                 ▼                  ▼
         ┌──────────┐     ┌──────────┐       ┌──────────┐
         │   SEED   │     │ HARVEST  │       │   PUSH   │
         │  ──────▶ │     │ ◀──────  │       │  ──────▶ │
         └──────────┘     └──────────┘       └──────────┘
                │                 │                  │
                ▼                 │                  ▼
    ┌───────────────────┐   │        ┌───────────────────┐
    │   New Project     │        │        │  Active Project   │
    │                   │        │        │                   │
    │ .bigbang.json     │        │        │ .bigbang.json     │
    │ .github/          │        │        │ .github/          │
    │   copilot-instr.  │        │        │   copilot-instr.  │
    │   prompts/        │        │        │   prompts/        │
    │ LEARNINGS.md      │        │        │ LEARNINGS.md      │
    └───────────────────┘        │        └───────────────────┘
                                 │                  │
                                 └──────────────────┘
```

**Three core flows**:

1. **Seed** (Phase 03) — Bootstrap a new project from BigBang templates. Renders templates with project-specific settings, creates the `.bigbang.json` manifest.
2. **Harvest** (Phase 04) — Extract evolved learnings and improvements from an active project back to BigBang. Agent-assisted classification and deduplication.
3. **Push** (Phase 05) — Forward-propagate BigBang improvements to active projects. Respects local modifications, supports selective updates.

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Language | Python 3.12+ | CLI scripts, automation, validation |
| CLI Framework | click | Command-line interfaces for seed/harvest/push |
| Schema Validation | jsonschema | Validating `.bigbang.json` manifests |
| Diffing | difflib | Computing diffs for harvest and push |
| Hashing | hashlib (SHA-256) | Artifact drift detection |
| Testing | pytest, pytest-cov | Script validation and coverage |
| Linting | ruff | Code quality for BigBang's own scripts |
| Type Checking | mypy | Static type analysis for scripts |
| CI | GitHub Actions | Automated validation on every commit |

## Implementation Steps

| Step | Document | Description | Model | Extended Thinking |
|------|----------|-------------|-------|-------------------|
| 01 | [Initial Consolidation](01-initial-consolidation.md) | Audit and merge existing artifacts from all repos | Sonnet | No |
| 02 | [Repository Structure](02-repository-structure.md) | Define structure, schemas, manifest, naming conventions | Opus | Yes |
| 03 | [Project Initialization](03-project-initialization.md) | Build seeding CLI and agent prompt | Sonnet | No |
| 04 | [Back-Propagation](04-back-propagation.md) | Build harvesting CLI and agent prompt | Opus | Yes |
| 05 | [Forward-Propagation](05-forward-propagation.md) | Build push CLI and agent prompt | Sonnet | No |
| 06 | [Governance](06-governance.md) | CI checks, maintenance cadence, conflict resolution | Sonnet | No |

**Recommended implementation order**: 01 → 02 → 03 → 04 → 05 → 06 (sequential, each phase depends on the previous).

## New Prompts Introduced

This plan introduces three new agent prompts for BigBang repository operations:

| Prompt | Purpose | Phase |
|--------|---------|-------|
| `bigbang_seed.prompt.md` | Interactive project bootstrapping | Phase 03 |
| `bigbang_harvest.prompt.md` | Interactive back-propagation with classification | Phase 04 |
| `bigbang_push.prompt.md` | Interactive forward-propagation with conflict resolution | Phase 05 |
| `bigbang_audit.prompt.md` | Periodic self-audit of BigBang health | Phase 06 |

## Milestones

| Milestone | Phase | Acceptance Criteria |
|-----------|-------|---------------------|
| **M1: Consolidated** | 01 | All existing repos audited; artifacts classified and merged into BigBang structure; audit report committed |
| **M2: Structured** | 02 | Full directory structure implemented; manifest schema defined; templates parameterized; `pyproject.toml` working |
| **M3: Seedable** | 03 | `bigbang-seed` CLI bootstraps a new project with one command; manifest and hashes generated; dry-run works |
| **M4: Harvestable** | 04 | `bigbang-harvest` extracts new learnings and diffs; domain classification works; report generation works |
| **M5: Propagatable** | 05 | `bigbang-push` updates active projects; local modification detection works; batch push available |
| **M6: Governed** | 06 | CI pipeline active; template validation automated; maintenance reminders configured; audit prompt functional |

## Risk Assessment Summary

| Phase | Risk Level | Key Risks |
|-------|-----------|-----------|
| 01 — Consolidation | Low-Medium | Missing repos during audit; premature generalization |
| 02 — Structure | Medium | Over-engineering manifest schema; template parameterization complexity |
| 03 — Seeding | Low-Medium | Path handling edge cases; template rendering conflicts |
| 04 — Harvesting | **High** | Overly aggressive harvesting; learning deduplication accuracy; generalization judgment |
| 05 — Pushing | Medium | Silent overwrites; version tracking desync; batch push errors |
| 06 — Governance | Low | Governance overhead; maintenance cadence adherence |

**Highest risk area**: Phase 04 (Harvesting) requires the most careful implementation. The agent prompt is critical here — it provides the judgment layer that determines what is generalizable vs. project-specific. Start with conservative defaults (never auto-merge, always require review).

## Open Questions

These questions should be answered before or during implementation:

### Scope

1. **Which repos to include in Phase 01?** List all repos with AI coding agent artifacts that should be audited.
2. **GitHub only or Azure DevOps too?** Do Azure DevOps repos support `.github/prompts/` or need a different layout?
3. **How many domains initially?** Start with python, typescript, cpp, devops — or add more?

### Design Decisions

4. **Learning granularity**: One `LEARNINGS.md` per domain in BigBang, or one per project-domain combination?
   - **Recommendation**: One per domain (simpler, sufficient for the current scale).
5. **Template rendering**: `str.replace()` vs. Jinja2?
   - **Recommendation**: `str.replace()` for simplicity. Only 2 placeholders needed.
6. **Naming convention**: Should seeded projects keep the `bigbang_` prefix during transition?
   - **Recommendation**: No. Replace immediately with `{project_name}_` for clarity.

### Operations

7. **Harvesting mode**: Fully automated (CI-triggered) vs. manual (prompt-based)?
   - **Recommendation**: Manual/prompt-based initially. Automate after the workflow is proven reliable.
8. **Conflict resolution default**: When BigBang and a project diverge, who wins?
   - **Recommendation**: Neither automatically. Always present diffs for human review. BigBang is authoritative for cross-cutting rules; projects are authoritative for their customizations.
9. **Registry management**: How are seeded projects tracked for batch push?
   - **Recommendation**: Simple `registry.json` file in BigBang, manually maintained.

### Future Considerations

10. **Multi-agent support**: Should templates support both GitHub Copilot and Claude Code (CLAUDE.md)?
    - **Recommendation**: Start with the current `.github/` structure. Add `CLAUDE.md` support as a future enhancement.
11. **Template inheritance**: Should templates support inheritance (e.g., a Python web template extends the base Python template)?
    - **Recommendation**: Not initially. Simple composition (base + overlays) is sufficient. Add inheritance only if overlay complexity grows.
