# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Tests for action.yaml configuration."""

import yaml
import pytest


def test_action_yaml_exists():
    """Test that action.yaml exists and is valid YAML."""
    with open("action.yaml", "r") as f:
        action_config = yaml.safe_load(f)

    assert action_config is not None
    assert "name" in action_config
    assert "description" in action_config
    assert "inputs" in action_config
    assert "outputs" in action_config
    assert "runs" in action_config


def test_action_has_mode_input():
    """Test that action has mode input parameter."""
    with open("action.yaml", "r") as f:
        action_config = yaml.safe_load(f)

    assert "mode" in action_config["inputs"]
    mode_input = action_config["inputs"]["mode"]
    assert mode_input["required"] is False
    assert mode_input["default"] == "build"


def test_action_required_inputs():
    """Test that all required inputs are defined."""
    with open("action.yaml", "r") as f:
        action_config = yaml.safe_load(f)

    # These inputs exist but are optional to support auto-discovery in validate mode
    optional_but_important_inputs = ["packer_template", "packer_vars_file"]
    for input_name in optional_but_important_inputs:
        assert input_name in action_config["inputs"]
        # They're optional (required: false) to support auto-discovery
        assert "required" in action_config["inputs"][input_name]


def test_action_outputs():
    """Test that all expected outputs are defined."""
    with open("action.yaml", "r") as f:
        action_config = yaml.safe_load(f)

    expected_outputs = ["bastion_ip", "status", "mode"]
    for output_name in expected_outputs:
        assert output_name in action_config["outputs"]


def test_action_uses_sha_pinned_versions():
    """Test that actions use SHA-pinned versions."""
    with open("action.yaml", "r") as f:
        content = f.read()

    # Check that we don't use @v tags without SHAs
    assert "tailscale/github-action@v2" not in content
    assert "actions/setup-python@v5" not in content
    assert "hashicorp/setup-packer@main" not in content or "35a288e72c00399c0ae4c0c15b0e435e7896e903" in content


def test_action_is_composite():
    """Test that action runs as composite."""
    with open("action.yaml", "r") as f:
        action_config = yaml.safe_load(f)

    assert action_config["runs"]["using"] == "composite"
    assert "steps" in action_config["runs"]
    assert len(action_config["runs"]["steps"]) > 0


def test_action_has_conditional_steps():
    """Test that bastion steps are conditional on mode."""
    with open("action.yaml", "r") as f:
        content = f.read()

    # Bastion-related steps should have conditional checks
    assert "if: inputs.mode == 'build'" in content
    assert "if: inputs.mode == 'validate'" in content
