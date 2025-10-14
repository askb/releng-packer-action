# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Tests for shell scripts."""

import subprocess
import pytest
import shutil
from pathlib import Path


def has_shellcheck():
    """Check if shellcheck is available."""
    return shutil.which("shellcheck") is not None


@pytest.mark.skipif(not has_shellcheck(), reason="shellcheck not installed")
def test_shellcheck_passes_on_all_scripts():
    """Test that shellcheck passes on all shell scripts."""
    scripts = list(Path(".").glob("**/*.sh"))
    scripts = [s for s in scripts if ".venv" not in str(s) and "node_modules" not in str(s)]

    assert len(scripts) > 0, "No shell scripts found"

    for script in scripts:
        result = subprocess.run(
            ["shellcheck", "-x", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Shellcheck failed for {script}:\n{result.stdout}\n{result.stderr}"


def test_setup_script_exists():
    """Test that setup.sh exists and is executable."""
    setup_script = Path("setup.sh")
    assert setup_script.exists()
    assert setup_script.stat().st_mode & 0o111  # Has execute bit


def test_test_templates_script_exists():
    """Test that test-templates.sh exists."""
    test_script = Path("test-templates.sh")
    assert test_script.exists()
    assert test_script.stat().st_mode & 0o111


def test_baseline_provision_script_exists():
    """Test that baseline provision script exists."""
    baseline_script = Path("examples/provision/baseline.sh")
    assert baseline_script.exists()
    assert baseline_script.stat().st_mode & 0o111


def test_setup_script_syntax():
    """Test setup.sh has valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", "setup.sh"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in setup.sh: {result.stderr}"


def test_test_templates_script_syntax():
    """Test test-templates.sh has valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", "test-templates.sh"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in test-templates.sh: {result.stderr}"


def test_baseline_script_syntax():
    """Test baseline.sh has valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", "examples/provision/baseline.sh"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in baseline.sh: {result.stderr}"


def test_scripts_have_shebang():
    """Test that all shell scripts have proper shebang."""
    scripts = [
        "setup.sh",
        "test-templates.sh",
        "examples/provision/baseline.sh",
    ]

    for script_path in scripts:
        with open(script_path, "r") as f:
            first_line = f.readline()
            assert first_line.startswith("#!/"), f"{script_path} missing shebang"
            assert "bash" in first_line or "sh" in first_line, f"{script_path} shebang should use bash/sh"


def test_scripts_have_error_handling():
    """Test that scripts have proper error handling (set -e or set -euo pipefail)."""
    scripts = [
        "setup.sh",
        "test-templates.sh",
    ]

    for script_path in scripts:
        with open(script_path, "r") as f:
            content = f.read()
            # Check for error handling
            assert ("set -e" in content or "set -euo" in content or "set -o errexit" in content), \
                f"{script_path} should have error handling (set -e or set -euo pipefail)"


def test_no_hardcoded_secrets():
    """Test that scripts don't contain hardcoded secrets."""
    scripts = list(Path(".").glob("**/*.sh"))
    scripts = [s for s in scripts if ".venv" not in str(s)]

    # Common patterns that might indicate secrets
    secret_patterns = [
        "password=",
        "api_key=",
        "secret=",
        "token=",
        "AWS_SECRET",
        "OPENSTACK_PASSWORD",
    ]

    for script in scripts:
        with open(script, "r") as f:
            content = f.read().lower()
            for pattern in secret_patterns:
                if pattern.lower() in content:
                    # Check if it's referencing an env var (acceptable) or hardcoded (not acceptable)
                    lines = [line for line in content.split("\n") if pattern.lower() in line]
                    for line in lines:
                        # It's OK if it's ${VAR} or $VAR or reading from env
                        assert ("$" in line or "env" in line.lower()), \
                            f"Possible hardcoded secret in {script}: {line[:50]}"
