# Step 05 — Forward-Propagation (Pushing Updates)

> Build a CLI tool and agent prompt that forward-propagates improvements from BigBang's canonical templates to active projects that were previously seeded.

<!-- Model: Sonnet | Extended Thinking: No -->

## Objective

Implement the push workflow — the mechanism that keeps active projects up-to-date with BigBang's latest templates, learnings, and best practices. When BigBang improves (through harvesting or direct edits), those improvements should be available to all seeded projects.

## Implementation Details

### 5.1 What Gets Pushed

| Artifact | Source (BigBang) | Target (Project) | Condition |
|----------|-----------------|-------------------|-----------|
| Updated prompt templates | `templates/prompts/_*.prompt.md` | `.github/prompts/{name}_*.prompt.md` | Template changed since project's `bigbang_version` |
| Updated copilot-instructions | `templates/copilot-instructions/*.md` | `.github/copilot-instructions.md` | Base or relevant overlay changed |
| New learnings | `learnings/LEARNINGS.<domain>.md` | `LEARNINGS.md` | New entries for project's stack |
| New prompt templates | `templates/prompts/_new.prompt.md` | `.github/prompts/{name}_new.prompt.md` | Prompt added to BigBang since seeding |

### 5.2 `scripts/push.py` CLI

```
Usage: bigbang-push [OPTIONS] TARGET_PATH

  Forward-propagate BigBang improvements to a seeded project.

Options:
  --dry-run              Preview what would be updated without writing
  --force                Overwrite locally modified files without confirmation
  --skip-modified        Skip files that have local modifications
  --learnings-only       Only push new learnings, skip other artifacts
  --help                 Show this message and exit
```

**Core workflow**:

```python
def push(target_path: Path, dry_run: bool, force: bool, skip_modified: bool, learnings_only: bool) -> PushReport:
    # 1. Read .bigbang.json from target project
    manifest = load_manifest(target_path)

    # 2. Check version — is an update available?
    current_version = get_bigbang_version()
    if manifest.bigbang_version == current_version:
        print("Project is already up to date.")
        return PushReport(status="up_to_date")

    # 3. Detect local modifications via hash comparison
    local_changes = detect_local_modifications(target_path, manifest)

    # 4. Render current BigBang templates with project settings
    rendered = render_templates_for_project(manifest)

    # 5. Compare rendered templates with project's current files
    updates = compute_updates(target_path, rendered, manifest)

    # 6. Handle each update
    for update in updates:
        if learnings_only and update.artifact_type != "learnings":
            continue

        if update.path in local_changes:
            if skip_modified:
                print(f"  SKIP (locally modified): {update.path}")
                continue
            if not force:
                print(f"  CONFLICT: {update.path} has local modifications")
                print(update.diff)
                if not confirm("Overwrite?"):
                    continue

        if not dry_run:
            write_update(target_path, update)

    # 7. Update manifest
    if not dry_run:
        update_manifest_push(target_path, manifest, current_version, rendered)

    return PushReport(status="updated", updates=updates)
```

### 5.3 Local Modification Detection

Before overwriting any file, check if the project has locally modified it:

```python
def detect_local_modifications(target_path: Path, manifest: Manifest) -> set[str]:
    """Find files that have been modified locally since last seed/push."""
    modified = set()
    for rel_path, stored_hash in manifest.artifact_hashes.items():
        file_path = target_path / rel_path
        if file_path.exists():
            current_hash = compute_hash(file_path)
            if current_hash != stored_hash:
                modified.add(rel_path)
    return modified
```

**Behavior matrix for locally modified files**:

| Flag | Locally Modified File | Unmodified File |
|------|----------------------|-----------------|
| *(default)* | Show diff, ask for confirmation | Update silently |
| `--force` | Overwrite without asking | Update silently |
| `--skip-modified` | Skip entirely | Update silently |
| `--dry-run` | Report as conflict | Report as update |

### 5.4 New Learnings Push

When BigBang has new learnings relevant to the project's stack:

```python
def compute_learnings_update(target_path: Path, manifest: Manifest) -> list[str]:
    """Find new learnings in BigBang that aren't in the project yet."""
    project_learnings = parse_learnings(target_path / "LEARNINGS.md")
    bigbang_learnings = load_learnings_for_stack(manifest.stack)

    new_entries = []
    for entry in bigbang_learnings:
        if not is_present_in(entry, project_learnings):
            new_entries.append(entry)
    return new_entries
```

New learnings are **appended** to the project's `LEARNINGS.md`, never replacing existing content. A section header marks BigBang updates:

```markdown
# Learnings

[existing project learnings...]

## BigBang Update (v0.2.0 — 2026-03-01)

- [python] New learning from another project...
```

### 5.5 New Prompt File Detection

When BigBang adds a new prompt template (e.g., `_review.prompt.md`), the push tool should:

1. Detect that the template has no corresponding file in the project.
2. Render it with the project's name and description.
3. Add it to the project's `.github/prompts/` directory.
4. Add its hash to the manifest.

```python
def find_new_templates(manifest: Manifest) -> list[Path]:
    """Find BigBang templates that weren't present when the project was seeded."""
    template_dir = BIGBANG_ROOT / "templates" / "prompts"
    existing_templates = {
        path_to_template_name(rel_path)
        for rel_path in manifest.artifact_hashes
        if "prompts/" in rel_path
    }
    new_templates = []
    for template in template_dir.glob("_*.prompt.md"):
        if template.stem not in existing_templates:
            new_templates.append(template)
    return new_templates
```

### 5.6 `bigbang_push.prompt.md` Agent Prompt

```markdown
---
name: bigbang_push
description: Forward-propagate BigBang improvements to a seeded project
agent: agent
---

# Objective

> Your goal is to update a seeded project with the latest improvements from BigBang.

# Workflow

## Check for updates

- Read the project's `.bigbang.json` manifest.
- Compare the project's BigBang version with the current BigBang version.
- If already up to date, inform the user and stop.

## Preview changes

- Run `bigbang-push --dry-run <target_path>` to preview what would change.
- Present the list of updates to the user.
- Highlight any files with local modifications that would conflict.

## Apply updates

- After user confirmation, run `bigbang-push <target_path>`.
- For conflicting files, ask the user whether to overwrite, skip, or merge manually.

## Verify

- Verify that updated files are valid and consistent.
- Run the project's checks and tests if available.
- Confirm the manifest was updated with the new BigBang version.
```

### 5.7 Batch Push (`scripts/push_all.py`)

For pushing updates to multiple projects at once:

```
Usage: bigbang-push-all [OPTIONS]

  Forward-propagate BigBang improvements to all registered projects.

Options:
  --registry PATH     Path to registry file (default: registry.json)
  --dry-run           Preview all changes across all projects
  --skip-modified     Skip locally modified files in all projects
  --help              Show this message and exit
```

**Registry format** (`registry.json`):

```json
[
  {"path": "/home/frank/Projects/Pulsar", "name": "pulsar"},
  {"path": "/home/frank/Projects/AnotherProject", "name": "another"}
]
```

The batch push iterates over registered projects, runs `push()` for each, and produces a consolidated report.

### 5.8 Versioning Strategy

BigBang uses semantic versioning:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking template change | Minor (0.x.0) | Restructuring prompt workflow steps |
| New template or learning | Patch (0.0.x) | Adding `_review.prompt.md` |
| Typo fix or clarification | Patch (0.0.x) | Fixing a typo in base instructions |

The push tool uses `bigbang_version` from the manifest to determine what changed. It does not need to track individual template versions — the project manifest's `artifact_hashes` provide file-level change detection.

## Tests Required

| Test | Description | Expected Result |
|------|-------------|-----------------|
| Basic push | Push to mock project with outdated version | Files updated, manifest bumped |
| Already up-to-date | Push when versions match | "Up to date" message, no changes |
| Local modification detection | Modify a file in mock project before push | Detected and reported as conflict |
| Skip modified | Push with `--skip-modified` | Modified files skipped, others updated |
| Force overwrite | Push with `--force` | All files updated regardless of modifications |
| Dry-run safety | Push with `--dry-run` | Report generated, no files written |
| New template | Add new template to BigBang, push | New prompt file created in project |
| Learnings append | Add new learning to BigBang, push | Appended to project's LEARNINGS.md |
| Manifest update | Push successfully | Version, hashes, timestamp updated |
| Batch push | Push to two mock projects | Both updated, consolidated report |

## Acceptance Criteria

- [ ] `bigbang-push /path/to/project` updates artifacts to latest BigBang version
- [ ] Locally modified files are detected and require confirmation (not silently overwritten)
- [ ] `--skip-modified` and `--force` flags work correctly
- [ ] New prompt files from BigBang are added with correct project-name prefix
- [ ] New learnings are appended (not replacing existing content)
- [ ] Manifest updated with current BigBang version, new hashes, `last_push` timestamp
- [ ] `--dry-run` produces a report without writing files
- [ ] `bigbang_push.prompt.md` provides interactive update workflow
- [ ] `bigbang-push-all` handles batch updates with consolidated reporting
- [ ] All tests pass

## Dependencies

- [Phase 02](02-repository-structure.md) — Template structure and manifest schema must be defined.
- [Phase 03](03-project-initialization.md) — Seeded projects with manifests must exist.

## Hints

- The push workflow mirrors the seed workflow but with conflict detection. Reuse the template rendering and hash computation functions from `seed.py`.
- Keep the learnings append strategy simple: always append, never modify existing entries. The developer can clean up manually or during a maintenance cycle.
- The registry file (`registry.json`) for batch push could alternatively be auto-discovered by scanning a parent directory for `.bigbang.json` files.
- Consider adding a `--changelog` flag that shows what changed in BigBang between the project's version and the current version.

## Risk & Complexity Assessment

**Overall: Medium**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Silent overwrites | Low | High | Hash comparison mandatory; `--force` requires explicit flag |
| Version tracking desync | Low | Medium | Manifest is single source of truth; always update atomically |
| Batch push errors | Medium | Medium | Dry-run first; confirm before each project in batch mode |
| Merge conflicts with local changes | Medium | Medium | Interactive resolution via agent prompt |
| Stale registry entries | Low | Low | Validate paths exist before pushing; warn for missing projects |
