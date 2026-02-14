"""
Tests for BigBang push.py tool.

This test module validates the core push workflow functionality including:
- Version checking
- Local modification detection
- Template rendering
- Hash computation
- Manifest updates
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the functions we need to test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from push import (
    Manifest,
    Update,
    compute_hash,
    compose_copilot_instructions,
    compose_learnings,
    detect_local_modifications,
    get_bigbang_version,
    load_manifest,
    render_template,
)


# ============================================================================
# Test: Manifest Loading
# ============================================================================


def test_load_manifest_valid():
    """
    Test loading a valid .bigbang.json manifest file.

    Expected: Manifest is parsed correctly with all fields.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        manifest_data = {
            "project_name": "test_project",
            "project_description": "A test project",
            "stack": ["python"],
            "bigbang_version": "0.1.0",
            "seeded_at": "2026-02-14T12:00:00Z",
            "last_harvest": None,
            "last_push": None,
            "artifact_hashes": {
                ".github/copilot-instructions.md": "sha256:abc123",
            },
        }

        manifest_path = target_path / ".bigbang.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        manifest = load_manifest(target_path)

        assert manifest.project_name == "test_project"
        assert manifest.stack == ["python"]
        assert manifest.bigbang_version == "0.1.0"
        assert ".github/copilot-instructions.md" in manifest.artifact_hashes


def test_load_manifest_missing():
    """
    Test loading manifest from a directory without .bigbang.json.

    Expected: FileNotFoundError is raised.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)

        with pytest.raises(FileNotFoundError):
            load_manifest(target_path)


# ============================================================================
# Test: Hash Computation
# ============================================================================


def test_compute_hash():
    """
    Test SHA-256 hash computation for a file.

    Expected: Hash is computed correctly and matches expected format.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        f.flush()
        file_path = Path(f.name)

    try:
        hash_value = compute_hash(file_path)

        # Verify format
        assert hash_value.startswith("sha256:")
        assert len(hash_value) == 71  # "sha256:" (7) + 64 hex chars

        # Verify consistency
        hash_value2 = compute_hash(file_path)
        assert hash_value == hash_value2
    finally:
        file_path.unlink()


# ============================================================================
# Test: Local Modification Detection
# ============================================================================


def test_detect_local_modifications_no_changes():
    """
    Test modification detection when files haven't changed.

    Expected: No modifications detected.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        test_file = target_path / "test.txt"
        test_file.write_text("original content")

        file_hash = compute_hash(test_file)
        manifest = Manifest(
            project_name="test",
            stack=["python"],
            bigbang_version="0.1.0",
            seeded_at="2026-02-14T12:00:00Z",
            artifact_hashes={"test.txt": file_hash},
        )

        modified = detect_local_modifications(target_path, manifest)

        assert len(modified) == 0


def test_detect_local_modifications_file_changed():
    """
    Test modification detection when a file has been changed.

    Expected: Changed file is detected.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        test_file = target_path / "test.txt"
        test_file.write_text("original content")

        file_hash = compute_hash(test_file)
        manifest = Manifest(
            project_name="test",
            stack=["python"],
            bigbang_version="0.1.0",
            seeded_at="2026-02-14T12:00:00Z",
            artifact_hashes={"test.txt": file_hash},
        )

        # Modify the file
        test_file.write_text("modified content")

        modified = detect_local_modifications(target_path, manifest)

        assert "test.txt" in modified


def test_detect_local_modifications_file_deleted():
    """
    Test modification detection when a file has been deleted.

    Expected: Deleted file is detected as modified.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        target_path = Path(tmpdir)
        manifest = Manifest(
            project_name="test",
            stack=["python"],
            bigbang_version="0.1.0",
            seeded_at="2026-02-14T12:00:00Z",
            artifact_hashes={"missing.txt": "sha256:abc123"},
        )

        modified = detect_local_modifications(target_path, manifest)

        assert "missing.txt" in modified


# ============================================================================
# Test: Template Rendering
# ============================================================================


def test_render_template():
    """
    Test template placeholder replacement.

    Expected: Placeholders are replaced with actual values.
    """
    template = "Project: {{project_name}}\nDescription: {{project_description}}"
    rendered = render_template(template, "myproject", "My test project")

    assert "{{project_name}}" not in rendered
    assert "{{project_description}}" not in rendered
    assert "myproject" in rendered
    assert "My test project" in rendered


def test_render_template_no_placeholders():
    """
    Test template rendering with no placeholders.

    Expected: Content remains unchanged.
    """
    template = "This is plain text without placeholders."
    rendered = render_template(template, "myproject", "description")

    assert rendered == template


# ============================================================================
# Test: Version Functions
# ============================================================================


def test_get_bigbang_version():
    """
    Test retrieval of current BigBang version.

    Expected: Version string in semantic version format.
    """
    version = get_bigbang_version()

    assert version is not None
    assert len(version.split(".")) == 3  # x.y.z format


# ============================================================================
# Test: Update Model
# ============================================================================


def test_update_model_creation():
    """
    Test creating Update model instances.

    Expected: Update objects are created with correct fields.
    """
    update = Update(
        path=".github/prompts/test_implement.prompt.md",
        artifact_type="prompt",
        action="create",
        content="# Test Prompt",
    )

    assert update.path == ".github/prompts/test_implement.prompt.md"
    assert update.artifact_type == "prompt"
    assert update.action == "create"
    assert update.diff is None


# ============================================================================
# Test Fixtures & Utilities
# ============================================================================


@pytest.fixture
def mock_bigbang_root(tmp_path):
    """
    Create a mock BigBang repository structure for testing.

    This fixture sets up a minimal BigBang structure with templates
    and learnings that can be used for testing the push workflow.
    """
    # Create template directories
    templates_dir = tmp_path / "templates"
    copilot_dir = templates_dir / "copilot-instructions"
    prompts_dir = templates_dir / "prompts"
    learnings_dir = tmp_path / "learnings"

    copilot_dir.mkdir(parents=True)
    prompts_dir.mkdir(parents=True)
    learnings_dir.mkdir(parents=True)

    # Create base copilot-instructions
    base_copilot = copilot_dir / "base.md"
    base_copilot.write_text("# Base Instructions\n\nGeneral rules...")

    # Create Python overlay
    python_copilot = copilot_dir / "python.md"
    python_copilot.write_text("# Python Rules\n\nPython-specific rules...")

    # Create a prompt template
    implement_prompt = prompts_dir / "_implement.prompt.md"
    implement_prompt.write_text(
        "# {{project_name}} Implementation\n\n{{project_description}}"
    )

    # Create learnings
    base_learnings = tmp_path / "LEARNINGS.md"
    base_learnings.write_text("# General Learnings\n\n- Learning 1\n- Learning 2")

    python_learnings = learnings_dir / "LEARNINGS.python.md"
    python_learnings.write_text("# Python Learnings\n\n- Python learning 1")

    return tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
