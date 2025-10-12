# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Tests for example workflows."""

import yaml
import pytest
from pathlib import Path


def get_workflow_files():
    """Get all workflow YAML files."""
    workflows_dir = Path("examples/workflows")
    return list(workflows_dir.glob("*.yaml"))


@pytest.mark.parametrize("workflow_file", get_workflow_files())
def test_workflow_yaml_valid(workflow_file):
    """Test that workflow YAML files are valid."""
    with open(workflow_file, "r") as f:
        workflow_config = yaml.safe_load(f)

    assert workflow_config is not None
    assert "name" in workflow_config
    # 'on' gets parsed as boolean True by YAML
    assert ("on" in workflow_config or True in workflow_config)
    assert "jobs" in workflow_config


def test_gerrit_verify_workflow():
    """Test gerrit-packer-verify workflow structure."""
    with open("examples/workflows/gerrit-packer-verify.yaml", "r") as f:
        workflow = yaml.safe_load(f)

    assert "packer-validator" in workflow["jobs"]
    assert "vote" in workflow["jobs"]

    validator_job = workflow["jobs"]["packer-validator"]
    steps = validator_job["steps"]

    # Check for required steps
    step_names = [step.get("name", "") for step in steps]
    assert any("Checkout" in name for name in step_names)
    assert any("Validate" in name for name in step_names)


def test_gerrit_merge_workflow():
    """Test gerrit-packer-merge workflow structure."""
    with open("examples/workflows/gerrit-packer-merge.yaml", "r") as f:
        workflow = yaml.safe_load(f)

    assert "packer-build" in workflow["jobs"]

    build_job = workflow["jobs"]["packer-build"]
    steps = build_job["steps"]

    # Check for build step
    step_names = [step.get("name", "") for step in steps]
    assert any("Build" in name for name in step_names)


def test_matrix_build_workflow():
    """Test matrix-build workflow structure."""
    with open("examples/workflows/matrix-build-example.yaml", "r") as f:
        workflow = yaml.safe_load(f)

    assert "matrix-build" in workflow["jobs"]

    matrix_job = workflow["jobs"]["matrix-build"]
    assert "strategy" in matrix_job
    assert "matrix" in matrix_job["strategy"]

    matrix = matrix_job["strategy"]["matrix"]
    assert "platform" in matrix
    assert "template" in matrix
    assert len(matrix["platform"]) > 0
    assert len(matrix["template"]) > 0


def test_workflows_use_sha_pinned_actions():
    """Test that all workflows use SHA-pinned action versions."""
    for workflow_file in get_workflow_files():
        with open(workflow_file, "r") as f:
            content = f.read()

        # Should not use @v tags without SHAs
        assert "actions/checkout@v4\n" not in content
        assert "actions/checkout@v5\n" not in content

        # Should have SHA comments
        if "uses: actions/checkout" in content:
            assert "# v" in content  # Has version comment
