#!/usr/bin/env python3
"""
BigBang Push Tool - Forward-propagate improvements to seeded projects.

This script implements the push workflow for distributing BigBang updates
to projects that were previously seeded.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from pydantic import BaseModel, Field


# ============================================================================
# Data Models
# ============================================================================


class Manifest(BaseModel):
    """Project manifest schema (.bigbang.json)."""

    project_name: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    project_description: str = ""
    stack: list[str] = Field(min_length=1)
    bigbang_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    seeded_at: str
    last_harvest: Optional[str] = None
    last_push: Optional[str] = None
    artifact_hashes: dict[str, str] = Field(default_factory=dict)


class Update(BaseModel):
    """Represents a single file update to be applied."""

    path: str
    artifact_type: str  # "prompt", "copilot-instructions", "learnings", etc.
    action: str  # "create", "update", "append"
    content: str
    diff: Optional[str] = None


class PushReport(BaseModel):
    """Report of push operation results."""

    status: str  # "up_to_date", "updated", "conflicts"
    updates: list[Update] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# ============================================================================
# Core Constants
# ============================================================================

# Current BigBang version - should match version control
BIGBANG_VERSION = "0.1.0"

# Get BigBang root directory (parent of scripts/)
BIGBANG_ROOT = Path(__file__).parent.parent


# ============================================================================
# Utility Functions
# ============================================================================


def compute_hash(file_path: Path) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hash string in format "sha256:hexdigest"
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def load_manifest(target_path: Path) -> Manifest:
    """
    Load and parse .bigbang.json manifest from target project.

    Args:
        target_path: Path to the target project

    Returns:
        Parsed Manifest object

    Raises:
        FileNotFoundError: If manifest doesn't exist
        ValueError: If manifest is invalid
    """
    manifest_path = target_path / ".bigbang.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No .bigbang.json manifest found in {target_path}. "
            "Is this a BigBang-seeded project?"
        )

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Manifest(**data)


def get_bigbang_version() -> str:
    """
    Get the current BigBang version.

    Returns:
        Version string (e.g., "0.1.0")
    """
    return BIGBANG_VERSION


def detect_local_modifications(
    target_path: Path, manifest: Manifest
) -> set[str]:
    """
    Find files that have been modified locally since last seed/push.

    Compares current file hashes with those stored in the manifest.

    Args:
        target_path: Path to the target project
        manifest: Project manifest

    Returns:
        Set of relative paths that have been modified
    """
    modified = set()
    for rel_path, stored_hash in manifest.artifact_hashes.items():
        file_path = target_path / rel_path
        if file_path.exists():
            current_hash = compute_hash(file_path)
            if current_hash != stored_hash:
                modified.add(rel_path)
        else:
            # File was deleted locally
            modified.add(rel_path)
    return modified


def render_template(
    content: str, project_name: str, project_description: str
) -> str:
    """
    Replace template placeholders with actual values.

    Args:
        content: Template content
        project_name: Project name
        project_description: Project description

    Returns:
        Rendered content
    """
    result = content.replace("{{project_name}}", project_name)
    result = result.replace("{{project_description}}", project_description)
    return result


def compose_copilot_instructions(manifest: Manifest) -> str:
    """
    Compose copilot-instructions from base + selected overlays.

    Args:
        manifest: Project manifest with stack information

    Returns:
        Composed copilot-instructions content
    """
    base_path = BIGBANG_ROOT / "templates" / "copilot-instructions" / "base.md"
    if not base_path.exists():
        raise FileNotFoundError(f"Base copilot-instructions not found: {base_path}")

    # Read base
    with open(base_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add header
    stack_str = ", ".join(manifest.stack)
    header = (
        f"<!-- Generated by BigBang v{BIGBANG_VERSION} — Do not edit this header -->\n"
        f"<!-- Stack: {stack_str} -->\n\n"
    )
    content = header + content

    # Append domain-specific overlays
    for domain in manifest.stack:
        overlay_path = (
            BIGBANG_ROOT / "templates" / "copilot-instructions" / f"{domain}.md"
        )
        if overlay_path.exists():
            with open(overlay_path, "r", encoding="utf-8") as f:
                overlay_content = f.read()
            content += f"\n\n# {domain.title()}\n\n{overlay_content}"

    return content


def compose_learnings(manifest: Manifest) -> str:
    """
    Compose LEARNINGS.md from base learnings + domain-specific learnings.

    Args:
        manifest: Project manifest with stack information

    Returns:
        Composed learnings content
    """
    base_path = BIGBANG_ROOT / "LEARNINGS.md"
    content = ""

    # Read base learnings if exists
    if base_path.exists():
        with open(base_path, "r", encoding="utf-8") as f:
            content = f.read()

    # Append domain-specific learnings
    for domain in manifest.stack:
        domain_path = BIGBANG_ROOT / "learnings" / f"LEARNINGS.{domain}.md"
        if domain_path.exists():
            with open(domain_path, "r", encoding="utf-8") as f:
                domain_content = f.read()
            if content:
                content += f"\n\n## {domain.title()} Learnings\n\n{domain_content}"
            else:
                content = domain_content

    return content


def render_templates_for_project(manifest: Manifest) -> dict[str, str]:
    """
    Render all BigBang templates for the target project.

    Args:
        manifest: Project manifest

    Returns:
        Dictionary mapping relative paths to rendered content
    """
    rendered = {}

    # Copilot instructions
    rendered[".github/copilot-instructions.md"] = compose_copilot_instructions(manifest)

    # Prompt templates
    prompts_dir = BIGBANG_ROOT / "templates" / "prompts"
    if prompts_dir.exists():
        for template_path in prompts_dir.glob("_*.prompt.md"):
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Render with project details
            rendered_content = render_template(
                template_content,
                manifest.project_name,
                manifest.project_description,
            )

            # Generate target filename
            template_name = template_path.name
            target_name = f"{manifest.project_name}{template_name}"  # _impl -> pulsar_impl
            target_path = f".github/prompts/{target_name}"
            rendered[target_path] = rendered_content

    # Learnings
    rendered["LEARNINGS.md"] = compose_learnings(manifest)

    return rendered


def compute_simple_diff(old_content: str, new_content: str, max_lines: int = 10) -> str:
    """
    Compute a simple diff summary between two strings.

    Args:
        old_content: Original content
        new_content: New content
        max_lines: Maximum lines to show in diff

    Returns:
        Simplified diff description
    """
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    if old_lines == new_lines:
        return "No changes"

    return (
        f"Content changed:\n"
        f"  - Old: {len(old_lines)} lines\n"
        f"  + New: {len(new_lines)} lines"
    )


def compute_updates(
    target_path: Path, rendered: dict[str, str], manifest: Manifest
) -> list[Update]:
    """
    Compare rendered templates with project's current files.

    Args:
        target_path: Path to target project
        rendered: Rendered templates
        manifest: Project manifest

    Returns:
        List of updates to be applied
    """
    updates = []

    for rel_path, new_content in rendered.items():
        file_path = target_path / rel_path

        # Determine artifact type
        if "copilot-instructions" in rel_path:
            artifact_type = "copilot-instructions"
        elif "prompts/" in rel_path:
            artifact_type = "prompt"
        elif "LEARNINGS" in rel_path:
            artifact_type = "learnings"
        else:
            artifact_type = "other"

        if file_path.exists():
            # File exists - check if it needs updating
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()

            if current_content != new_content:
                diff = compute_simple_diff(current_content, new_content)
                updates.append(
                    Update(
                        path=rel_path,
                        artifact_type=artifact_type,
                        action="update",
                        content=new_content,
                        diff=diff,
                    )
                )
        else:
            # New file
            updates.append(
                Update(
                    path=rel_path,
                    artifact_type=artifact_type,
                    action="create",
                    content=new_content,
                )
            )

    return updates


def write_update(target_path: Path, update: Update) -> None:
    """
    Write an update to disk.

    Args:
        target_path: Path to target project
        update: Update to apply
    """
    file_path = target_path / update.path

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(update.content)


def update_manifest_push(
    target_path: Path,
    manifest: Manifest,
    new_version: str,
    rendered: dict[str, str],
) -> None:
    """
    Update manifest after successful push.

    Args:
        target_path: Path to target project
        manifest: Current manifest
        new_version: New BigBang version
        rendered: Rendered templates
    """
    # Update version and timestamp
    manifest.bigbang_version = new_version
    manifest.last_push = datetime.utcnow().isoformat() + "Z"

    # Recompute hashes for all artifacts
    manifest.artifact_hashes = {}
    for rel_path in rendered.keys():
        file_path = target_path / rel_path
        if file_path.exists():
            manifest.artifact_hashes[rel_path] = compute_hash(file_path)

    # Write updated manifest
    manifest_path = target_path / ".bigbang.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, indent=2)
        f.write("\n")


# ============================================================================
# CLI Command
# ============================================================================


@click.command()
@click.argument("target_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview what would be updated without writing files",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite locally modified files without confirmation",
)
@click.option(
    "--skip-modified",
    is_flag=True,
    help="Skip files that have local modifications",
)
@click.option(
    "--learnings-only",
    is_flag=True,
    help="Only push new learnings, skip other artifacts",
)
def push(
    target_path: Path,
    dry_run: bool,
    force: bool,
    skip_modified: bool,
    learnings_only: bool,
) -> None:
    """
    Forward-propagate BigBang improvements to a seeded project.

    TARGET_PATH: Path to the seeded project directory
    """
    click.echo(f"BigBang Push Tool v{BIGBANG_VERSION}")
    click.echo(f"Target: {target_path}")
    click.echo()

    # 1. Read .bigbang.json from target project
    try:
        manifest = load_manifest(target_path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except ValueError as e:
        click.echo(f"Error: Invalid manifest: {e}", err=True)
        raise click.Abort()

    click.echo(f"Project: {manifest.project_name}")
    click.echo(f"Stack: {', '.join(manifest.stack)}")
    click.echo(f"Current BigBang version: {manifest.bigbang_version}")
    click.echo()

    # 2. Check version — is an update available?
    current_version = get_bigbang_version()
    if manifest.bigbang_version == current_version:
        click.echo("✓ Project is already up to date.")
        return

    click.echo(f"Update available: {manifest.bigbang_version} → {current_version}")
    click.echo()

    # 3. Detect local modifications via hash comparison
    local_changes = detect_local_modifications(target_path, manifest)
    if local_changes:
        click.echo(f"Found {len(local_changes)} locally modified file(s):")
        for path in sorted(local_changes):
            click.echo(f"  - {path}")
        click.echo()

    # 4. Render current BigBang templates with project settings
    try:
        rendered = render_templates_for_project(manifest)
    except Exception as e:
        click.echo(f"Error rendering templates: {e}", err=True)
        raise click.Abort()

    # 5. Compare rendered templates with project's current files
    updates = compute_updates(target_path, rendered, manifest)

    if not updates:
        click.echo("✓ No updates needed.")
        return

    click.echo(f"Found {len(updates)} update(s):")
    click.echo()

    # 6. Handle each update
    skipped = []
    applied = []

    for update in updates:
        # Filter by learnings-only flag
        if learnings_only and update.artifact_type != "learnings":
            continue

        # Handle locally modified files
        if update.path in local_changes:
            if skip_modified:
                click.echo(f"  SKIP (locally modified): {update.path}")
                skipped.append(update.path)
                continue
            if not force:
                click.echo(f"  CONFLICT: {update.path} has local modifications")
                if update.diff:
                    click.echo(f"    {update.diff}")
                if not dry_run:
                    if not click.confirm("    Overwrite?", default=False):
                        skipped.append(update.path)
                        continue

        # Display update action
        action_symbol = "+" if update.action == "create" else "~"
        click.echo(f"  {action_symbol} {update.path} ({update.action})")

        # Write update (unless dry-run)
        if not dry_run:
            write_update(target_path, update)
            applied.append(update.path)

    click.echo()

    # 7. Update manifest (unless dry-run)
    if not dry_run and applied:
        update_manifest_push(target_path, manifest, current_version, rendered)
        click.echo(f"✓ Updated {len(applied)} file(s)")
        click.echo(f"✓ Manifest updated to v{current_version}")
    elif dry_run:
        click.echo(f"Dry-run complete. Would update {len(updates)} file(s).")
    else:
        click.echo("No files were updated.")

    if skipped:
        click.echo(f"⚠ Skipped {len(skipped)} file(s)")


if __name__ == "__main__":
    push()
