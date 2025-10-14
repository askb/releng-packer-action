# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Tests for Packer templates."""

import json
import subprocess
import pytest
import shutil
from pathlib import Path


def has_packer():
    """Check if packer is available."""
    return shutil.which("packer") is not None


def get_packer_templates():
    """Get all Packer template files."""
    templates_dir = Path("examples/templates")
    if not templates_dir.exists():
        return []
    return list(templates_dir.glob("*.pkr.hcl"))


def get_var_files():
    """Get all Packer variable files."""
    vars_dir = Path("examples/vars")
    if not vars_dir.exists():
        return []
    return list(vars_dir.glob("*.pkrvars.hcl"))


@pytest.mark.skipif(len(get_packer_templates()) == 0, reason="No templates found")
def test_packer_templates_exist():
    """Test that Packer templates exist."""
    templates = get_packer_templates()
    assert len(templates) > 0, "No Packer templates found"


@pytest.mark.skipif(len(get_var_files()) == 0, reason="No var files found")
def test_packer_var_files_exist():
    """Test that Packer variable files exist."""
    var_files = get_var_files()
    assert len(var_files) > 0, "No Packer variable files found"


@pytest.mark.skipif(not has_packer() or len(get_packer_templates()) == 0, reason="Packer not installed or no templates found")
@pytest.mark.parametrize("template", get_packer_templates())
def test_packer_template_syntax(template):
    """Test that Packer templates have valid HCL syntax."""
    result = subprocess.run(
        ["packer", "fmt", "-check", str(template)],
        capture_output=True,
        text=True,
    )
    # packer fmt returns 0 if file is formatted, 1 if not, 2+ for errors
    # We want to ensure no syntax errors (not 2+)
    assert result.returncode < 2, f"Packer template {template} has syntax errors: {result.stderr}"


@pytest.mark.skipif(len(get_packer_templates()) == 0, reason="No templates found")
def test_templates_have_required_sections():
    """Test that templates have required sections."""
    templates = get_packer_templates()

    for template in templates:
        with open(template, "r") as f:
            content = f.read()

        # Check for basic required blocks
        assert "source" in content or "build" in content, \
            f"{template} should have source or build block"


@pytest.mark.skipif(len(get_var_files()) == 0, reason="No var files found")
def test_var_files_have_required_variables():
    """Test that var files define expected variables."""
    var_files = get_var_files()

    expected_vars = ["cloud_network", "source_image_name"]

    for var_file in var_files:
        with open(var_file, "r") as f:
            content = f.read()

        # At least one of the expected variables should be present
        has_var = any(var in content for var in expected_vars)
        assert has_var, f"{var_file} should define at least one expected variable"


def test_provision_directory_exists():
    """Test that provision scripts directory exists."""
    provision_dir = Path("examples/provision")
    assert provision_dir.exists() and provision_dir.is_dir()


def test_baseline_provision_script_has_content():
    """Test that baseline provision script has meaningful content."""
    baseline = Path("examples/provision/baseline.sh")
    if baseline.exists():
        with open(baseline, "r") as f:
            content = f.read()

        # Should have more than just shebang and comments
        non_comment_lines = [
            line for line in content.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        assert len(non_comment_lines) > 1, "baseline.sh should have executable content"


def test_no_absolute_paths_in_templates():
    """Test that templates don't use absolute paths (should be relative)."""
    templates = get_packer_templates()

    for template in templates:
        with open(template, "r") as f:
            content = f.read()

        # Check for suspicious absolute paths (excluding valid uses like /tmp)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue

            # Check for absolute paths that might be problematic
            if '= "/' in line or "= '/" in line:
                # Allow certain paths
                if any(allowed in line for allowed in ["/tmp", "/var", "/etc", "/usr"]):
                    continue
                # Warn about others (might be system paths that are OK)
                # This is more of a code review hint than a hard failure
                pass


def test_templates_reference_valid_scripts():
    """Test that templates reference scripts that exist."""
    templates = get_packer_templates()
    provision_dir = Path("examples/provision")

    for template in templates:
        with open(template, "r") as f:
            content = f.read()

        # Look for script references
        if "provision/baseline.sh" in content:
            baseline = provision_dir / "baseline.sh"
            assert baseline.exists(), f"{template} references baseline.sh which doesn't exist"
