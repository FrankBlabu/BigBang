# Step 01 — Initial Consolidation

> Audit all existing AI coding agent artifacts across the developer's repository portfolio, identify commonalities and domain-specific variations, and consolidate them into the BigBang repository structure.

<!-- Model: Sonnet | Extended Thinking: No -->

## Objective

This is a one-time migration phase. The goal is to discover, classify, and merge all copilot instructions, prompt files, and learnings scattered across existing repositories into BigBang as the canonical source of truth.

## Implementation Details

### 1.1 Artifact Inventory

Create a comprehensive inventory of all repositories and their agent artifacts. Use a script or manual audit to populate this table:

| Repository | Platform | Stack | copilot-instructions | Prompts | LEARNINGS | AGENTS/CLAUDE.md |
|------------|----------|-------|---------------------|---------|-----------|------------------|
| BigBang | GitHub | Python | Yes | 6 files | Empty | No |
| Pulsar | GitHub | Python | ? | ? | ? | ? |
| *(others)* | GitHub/AzDO | TS/C++/etc | ? | ? | ? | ? |

**Tooling**: A shell script (`scripts/audit.sh`) that iterates over a list of local repo paths and checks for:
- `.github/copilot-instructions.md`
- `.github/prompts/*.prompt.md`
- `.copilot/` directory
- `LEARNINGS.md`
- `AGENTS.md`, `CLAUDE.md`

```bash
#!/usr/bin/env bash
# scripts/audit.sh — Scan local repos for agent artifacts
REPOS=("$@")
for repo in "${REPOS[@]}"; do
  echo "=== $(basename "$repo") ==="
  [ -f "$repo/.github/copilot-instructions.md" ] && echo "  copilot-instructions: YES" || echo "  copilot-instructions: NO"
  count=$(find "$repo/.github/prompts" -name "*.prompt.md" 2>/dev/null | wc -l)
  echo "  prompt files: $count"
  [ -f "$repo/LEARNINGS.md" ] && echo "  LEARNINGS.md: YES" || echo "  LEARNINGS.md: NO"
  [ -f "$repo/AGENTS.md" ] && echo "  AGENTS.md: YES" || echo "  AGENTS.md: NO"
  [ -f "$repo/CLAUDE.md" ] && echo "  CLAUDE.md: YES" || echo "  CLAUDE.md: NO"
done
```

### 1.2 Content Analysis

For each discovered artifact, perform the following classification:

**Copilot Instructions**:
- Extract rules that are **domain-agnostic** (e.g., "follow best practices", "prefer VSCode tasks over shell commands").
- Extract rules that are **domain-specific** (e.g., "use `pydantic` for Python", "always use a virtual environment").
- Identify **duplicated** rules across repos.
- Identify **conflicting** rules (different repos recommend different approaches for the same concern).

**Prompt Files**:
- Identify prompts that are **universal** (commit, implement, maintenance, update, coverage — these apply to any project).
- Identify prompts that are **domain-specific** (e.g., a prompt for running `pytest` specifically).
- Note structural patterns: YAML frontmatter, Objective section, Workflow section.

**Learnings**:
- Classify each entry by domain: `python`, `typescript`, `cpp`, `devops`, `git`, `general`.
- Remove outdated or incorrect entries.
- Consolidate overlapping entries.

### 1.3 Merging Strategy

| Artifact Type | Source | Target in BigBang |
|---------------|--------|-------------------|
| Domain-agnostic rules | All `copilot-instructions.md` | `templates/copilot-instructions/base.md` |
| Python-specific rules | Python repos | `templates/copilot-instructions/python.md` |
| TypeScript-specific rules | TS repos | `templates/copilot-instructions/typescript.md` |
| C++/Qt-specific rules | C++ repos | `templates/copilot-instructions/cpp.md` |
| DevOps-specific rules | CI/CD configs | `templates/copilot-instructions/devops.md` |
| Universal prompts | All repos | `templates/prompts/_*.prompt.md` (parameterized) |
| Domain learnings | All `LEARNINGS.md` | `learnings/LEARNINGS.<domain>.md` |

**Parameterization**: Replace project-specific names (e.g., `bigbang_` prefix in prompt names) with `{{project_name}}` placeholders. Example:

```markdown
# Before (in BigBang repo)
name: bigbang_implement

# After (in template)
name: {{project_name}}_implement
```

### 1.4 Conflict Resolution

When two repos have conflicting rules:

1. **Prefer the more recent/evolved version** — later iterations typically reflect lessons learned.
2. **Document the conflict** in an `doc/audit-report.md` file for developer review.
3. **Flag for manual resolution** — do not auto-resolve conflicts that change behavior.

Example conflict: Repo A says "use `unittest`" while Repo B says "use `pytest`". Resolution: document both, recommend `pytest` as the modern standard, place in the Python domain overlay.

## Tests Required

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Template placeholders | All prompt templates contain `{{project_name}}` | No hardcoded project names in templates |
| Base isolation | Base instructions contain no domain-specific language | No references to Python/TS/C++/Qt in `base.md` |
| Overlay self-containment | Each domain overlay makes sense independently | Overlay files are coherent without base context |
| No duplicates | No rule appears in both base and an overlay | Grep for duplicate sentences across files |

## Acceptance Criteria

- [ ] All existing repos audited and inventory table complete
- [ ] `doc/audit-report.md` created with findings, conflicts, and resolutions
- [ ] Base copilot-instructions separated from domain overlays
- [ ] All prompt files generalized with `{{project_name}}` placeholder
- [ ] Domain-specific learnings extracted and filed into `learnings/LEARNINGS.<domain>.md`
- [ ] No duplicate rules across base and overlays
- [ ] Audit script committed as `scripts/audit.sh`

## Dependencies

None — this is the first phase.

## Hints

- The existing six prompt files in BigBang's `.github/prompts/` are the initial reference and can serve as the first set of universal templates.
- The `copilot-instructions.md` already contains mostly domain-agnostic rules, with the Python-specific rule "All code must be fully typed. Use `pydantic` for Python" which should move to the Python overlay.
- Start with the repos you have local access to. Remote-only repos can be audited later using `gh repo clone` or direct API access.

## Risk & Complexity Assessment

**Overall: Low-Medium**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missing repos during audit | Medium | Low | Maintain inventory table, add repos incrementally |
| Premature generalization | Medium | Medium | Start with concrete content from existing repos, generalize only proven patterns |
| Loss of project-specific nuance | Low | Medium | Keep audit report for reference, domain overlays preserve specificity |
