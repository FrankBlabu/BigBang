# Step 04 — Back-Propagation (Harvesting)

> Build a CLI tool and agent prompt that extracts evolved artifacts from active projects and merges them back into BigBang's canonical templates and learnings.

<!-- Model: Opus | Extended Thinking: Yes -->

## Objective

Implement the harvesting workflow — the feedback loop that makes BigBang a living system. When a project develops new learnings, improves prompt templates, or refines copilot-instructions, those improvements should flow back to BigBang so all future projects (and updates to existing projects) benefit.

This is the most complex phase because it requires judgment about what is generalizable vs. project-specific.

## Implementation Details

### 4.1 What Gets Harvested

| Artifact | Source (Project) | Target (BigBang) | Judgment Required |
|----------|-----------------|-------------------|-------------------|
| New learnings | `LEARNINGS.md` entries | `learnings/LEARNINGS.<domain>.md` | Classify by domain, check for duplicates |
| Prompt improvements | `.github/prompts/{name}_*.prompt.md` | `templates/prompts/_*.prompt.md` | Determine if change is generalizable |
| Instruction refinements | `.github/copilot-instructions.md` | `templates/copilot-instructions/*.md` | Classify as base or domain-specific |

**Critical principle**: Harvesting NEVER auto-merges into BigBang. It always produces a review-ready report or diff. The developer (or a reviewing agent) decides what to accept.

### 4.2 `scripts/harvest.py` CLI

```
Usage: bigbang-harvest [OPTIONS] SOURCE_PATH

  Extract improvements from an active project back to BigBang.

Options:
  --dry-run            Preview what would be harvested without making changes
  --report PATH        Write harvest report to file (default: stdout)
  --auto-classify      Attempt automatic domain classification of learnings
  --apply              Apply harvested changes to BigBang (with confirmation)
  --help               Show this message and exit
```

**Core workflow**:

```python
def harvest(source_path: Path, dry_run: bool, auto_classify: bool, apply: bool) -> HarvestReport:
    # 1. Read .bigbang.json from source project
    manifest = load_manifest(source_path)

    # 2. Detect changed artifacts via hash comparison
    changes = detect_changes(source_path, manifest)

    # 3. For each changed artifact, compute diff against BigBang template
    diffs = compute_diffs(changes, manifest)

    # 4. For LEARNINGS.md: extract new entries
    new_learnings = extract_new_learnings(source_path, manifest)

    # 5. Classify new learnings by domain
    if auto_classify:
        classified = auto_classify_learnings(new_learnings)
    else:
        classified = prompt_classification(new_learnings)

    # 6. Generate harvest report
    report = HarvestReport(
        project=manifest.project_name,
        new_learnings=classified,
        prompt_diffs=diffs.prompts,
        instruction_diffs=diffs.instructions,
    )

    # 7. Optionally apply changes
    if apply and not dry_run:
        apply_harvest(report, confirm=True)

    # 8. Update manifest with harvest timestamp
    if not dry_run:
        update_manifest_harvest(source_path, manifest)

    return report
```

### 4.3 Change Detection

Use the `artifact_hashes` from `.bigbang.json` to detect which files have been modified since seeding or last push:

```python
def detect_changes(source_path: Path, manifest: Manifest) -> list[ChangedArtifact]:
    """Compare current file hashes against manifest to find modifications."""
    changes = []
    for rel_path, stored_hash in manifest.artifact_hashes.items():
        file_path = source_path / rel_path
        if not file_path.exists():
            changes.append(ChangedArtifact(path=rel_path, change_type="deleted"))
            continue
        current_hash = compute_hash(file_path)
        if current_hash != stored_hash:
            changes.append(ChangedArtifact(path=rel_path, change_type="modified"))
    # Also check for new files in managed directories
    for new_file in find_new_artifacts(source_path, manifest):
        changes.append(ChangedArtifact(path=new_file, change_type="added"))
    return changes
```

### 4.4 Learning Extraction

Parse the project's `LEARNINGS.md` and identify entries not present in BigBang's learnings:

```python
def extract_new_learnings(source_path: Path, manifest: Manifest) -> list[Learning]:
    """Extract learning entries that are new since last seed/harvest."""
    project_learnings = parse_learnings(source_path / "LEARNINGS.md")
    bigbang_learnings = load_all_bigbang_learnings()

    new_entries = []
    for entry in project_learnings:
        if not is_duplicate(entry, bigbang_learnings):
            new_entries.append(entry)
    return new_entries
```

**Duplicate detection** uses normalized text comparison:

```python
def is_duplicate(entry: Learning, existing: list[Learning]) -> bool:
    """Check if a learning is substantially similar to an existing one."""
    normalized = normalize(entry.text)  # lowercase, strip whitespace, remove punctuation
    for existing_entry in existing:
        if similarity(normalized, normalize(existing_entry.text)) > 0.85:
            return True
    return False
```

Use a simple approach: normalize both strings and check for substring containment or high character overlap. Avoid heavy NLP dependencies — simple text similarity is sufficient for detecting near-duplicates.

### 4.5 Domain Classification

Learnings can be classified by domain using tag prefixes:

**Automatic classification** (when `--auto-classify` is used):
1. Check for explicit `[domain]` tag prefix: `- [python] Use pathlib...` → domain: python.
2. Check for domain keywords: mentions of `pydantic`, `pytest`, `pip` → likely python.
3. Fall back to the project's primary stack from the manifest.

**Keyword-based heuristic**:

| Domain | Keywords |
|--------|----------|
| `python` | python, pydantic, pytest, pip, venv, pyproject, ruff, mypy |
| `typescript` | typescript, npm, node, electron, tsx, eslint, webpack |
| `cpp` | c++, qt, cmake, gcc, clang, qml, moc |
| `devops` | ci, cd, pipeline, docker, kubernetes, azure, github actions |
| `general` | (no domain keywords matched) |

**Manual classification**: When `--auto-classify` is not used, print each untagged learning and ask the user to assign a domain.

### 4.6 Diff Generation for Prompts and Instructions

For modified prompt files, generate a readable diff:

```python
def compute_prompt_diff(project_path: Path, template_path: Path, manifest: Manifest) -> str:
    """Generate a diff between a project's prompt and the BigBang template."""
    # Re-render the template with the project's settings to get "expected" content
    template_content = render_template(
        template_path.read_text(),
        manifest.project_name,
        manifest.project_description,
    )
    project_content = project_path.read_text()

    diff = difflib.unified_diff(
        template_content.splitlines(keepends=True),
        project_content.splitlines(keepends=True),
        fromfile=f"bigbang/{template_path.name}",
        tofile=f"{manifest.project_name}/{project_path.name}",
    )
    return "".join(diff)
```

**Generalization decision**: The developer must review each prompt diff and decide:
- Is this change **project-specific** (don't propagate)?
- Is this change **generalizable** (update the BigBang template)?
- Is this change a **mixed improvement** (extract the general part)?

### 4.7 Applying Harvested Changes

When `--apply` is used, changes are written to BigBang's files with confirmation:

```python
def apply_harvest(report: HarvestReport, confirm: bool) -> None:
    """Apply harvested changes to BigBang repository."""
    # 1. Append new learnings to appropriate domain files
    for domain, entries in report.new_learnings_by_domain.items():
        target = LEARNINGS_DIR / f"LEARNINGS.{domain}.md"
        if confirm:
            print(f"Append {len(entries)} entries to {target}? [y/N]")
            # ... confirmation logic
        append_learnings(target, entries)

    # 2. For prompt changes, show diff and ask
    for diff in report.prompt_diffs:
        if confirm:
            print(f"Apply changes to {diff.template_path}?")
            print(diff.unified_diff)
            # ... confirmation logic
```

### 4.8 `bigbang_harvest.prompt.md` Agent Prompt

The agent prompt is the **primary harvesting interface** — it leverages the LLM's judgment for classification and generalization decisions:

```markdown
---
name: bigbang_harvest
description: Extract learnings and improvements from a project back to BigBang
agent: agent
---

# Objective

> Your goal is to harvest improvements from an active project and propose
> changes to the BigBang canonical repository.

# Workflow

## Read project state

- Read the project's `.bigbang.json` manifest to identify the project.
- Read the project's `LEARNINGS.md` for new learnings.
- Read the project's `.github/copilot-instructions.md` for instruction changes.
- Read the project's `.github/prompts/` for prompt improvements.

## Compare with BigBang

- Compare each artifact against the corresponding BigBang template.
- Identify what has changed and classify each change:
  - **New learning**: A new insight worth preserving.
  - **Prompt improvement**: A workflow step or instruction that was improved.
  - **Instruction refinement**: A coding rule that was refined.
  - **Project-specific**: A change that only applies to this project.

## Classify and propose

- For each new learning, classify by domain (python, typescript, cpp, devops, general).
- For each prompt improvement, determine if it is generalizable.
- Present all findings as a structured report with recommendations.
- Ask the user to approve or reject each proposed change.

## Apply approved changes

- Run `bigbang-harvest --apply <project_path>` with the approved changes.
- Verify the changes were applied correctly.
```

### 4.9 Harvest Report Format

```
═══════════════════════════════════════════════════
  BigBang Harvest Report — Project: pulsar
  Harvested at: 2026-02-14T15:30:00Z
═══════════════════════════════════════════════════

📋 New Learnings (3 found)
──────────────────────────
  [python] HDF5 datasets should use chunked storage for append operations.
  [python] Use structlog bound loggers for per-request context.
  [general] Always validate external API responses before processing.

📝 Modified Prompts (1 found)
─────────────────────────────
  pulsar_implement.prompt.md:
    + Added step: "Check for API rate limits before batch operations"
    Recommendation: GENERALIZE — useful for all projects

📐 Modified Instructions (0 found)

═══════════════════════════════════════════════════
```

## Tests Required

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Change detection | Modify a file in mock project | Detected as "modified" in harvest |
| New learning extraction | Add entries to mock LEARNINGS.md | New entries identified correctly |
| Duplicate detection | Add entry that already exists in BigBang | Flagged as duplicate, not harvested |
| Domain classification | Entry with `[python]` tag | Classified as python domain |
| Auto-classify keywords | Entry mentioning "pytest" without tag | Auto-classified as python |
| Diff generation | Modify a prompt file | Readable unified diff produced |
| Dry-run safety | Run with `--dry-run` | No changes to BigBang files |
| Manifest update | Harvest without `--dry-run` | `last_harvest` timestamp updated |
| Deleted artifact | Remove a managed file from project | Reported as "deleted" |

## Acceptance Criteria

- [ ] `bigbang-harvest /path/to/project` produces a clear harvest report
- [ ] New learnings are correctly identified and classified by domain
- [ ] Duplicate learnings are detected and excluded
- [ ] Modified prompts produce readable diffs
- [ ] `--apply` appends learnings to correct domain files in BigBang
- [ ] `--dry-run` makes no changes to any files
- [ ] Manifest `last_harvest` timestamp is updated after harvest
- [ ] Agent prompt `bigbang_harvest.prompt.md` provides interactive harvesting workflow
- [ ] All tests pass

## Dependencies

- [Phase 02](02-repository-structure.md) — Schemas and file conventions must be defined.
- [Phase 03](03-project-initialization.md) — Seeded projects with manifests must exist to harvest from.

## Hints

- The agent prompt is the preferred harvesting interface. The CLI generates reports and applies changes, but the LLM provides the judgment layer for classification and generalization.
- Start with two-way diff (project vs. BigBang-current). Three-way diff (project vs. BigBang-at-seed-time vs. BigBang-current) is a future enhancement enabled by the `bigbang_version` in the manifest.
- Conservative duplicate detection: prefer false negatives (miss a duplicate) over false positives (reject a unique learning). It's better to have a near-duplicate than to lose a valid insight.
- The harvest report format uses Unicode box-drawing characters for visual clarity in terminal output.

## Risk & Complexity Assessment

**Overall: High** — This is the most complex phase.

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Overly aggressive harvesting | Medium | High | Never auto-merge; always present for review |
| Learning deduplication false positives | Low | Medium | Use conservative matching threshold (0.85) |
| Prompt generalization errors | Medium | Medium | Present diffs with context; let developer decide |
| Three-way diff complexity | N/A | N/A | Defer to future; start with two-way diff |
| Project-specific content polluting BigBang | Medium | High | Agent prompt provides classification judgment layer |
| Performance with many learnings | Low | Low | File-based learnings are small; linear scan is fine |
