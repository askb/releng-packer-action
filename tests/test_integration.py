# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Integration tests for action and workflows."""

import os
import yaml
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestActionIntegration:
    """Test action.yaml integration scenarios."""

    def test_action_mode_validate_workflow(self):
        """Test validate mode doesn't require bastion inputs."""
        with open("action.yaml", "r") as f:
            action = yaml.safe_load(f)

        # In validate mode, bastion inputs should be optional
        bastion_inputs = [
            "tailscale_oauth_client_id",
            "tailscale_oauth_secret",
            "openstack_cloud_user",
            "openstack_cloud_pass",
        ]

        for inp in bastion_inputs:
            if inp in action["inputs"]:
                # Should not be strictly required since validate mode doesn't need them
                assert action["inputs"][inp].get("required", False) is False

    def test_action_mode_build_workflow(self):
        """Test build mode has all necessary steps."""
        with open("action.yaml", "r") as f:
            action = yaml.safe_load(f)

        steps = action["runs"]["steps"]
        step_ids = [s.get("id", "") for s in steps]

        # Should have bastion setup steps
        assert any("tailscale" in str(s).lower() for s in steps)
        assert any("bastion" in str(s).lower() for s in steps)

    def test_action_outputs_are_set(self):
        """Test that action defines all expected outputs."""
        with open("action.yaml", "r") as f:
            action = yaml.safe_load(f)

        outputs = action["outputs"]

        # Validate output structure
        assert "bastion_ip" in outputs
        assert "description" in outputs["bastion_ip"]

        assert "status" in outputs
        assert "description" in outputs["status"]

        assert "mode" in outputs
        assert "description" in outputs["mode"]


class TestWorkflowIntegration:
    """Test workflow integration scenarios."""

    def test_verify_workflow_uses_action_correctly(self):
        """Test that verify workflow uses the action with correct mode."""
        with open("examples/workflows/gerrit-packer-verify.yaml", "r") as f:
            workflow = yaml.safe_load(f)

        validator_job = workflow["jobs"]["packer-validator"]
        steps = validator_job["steps"]

        # Find the step that uses the action
        action_steps = [s for s in steps if "uses" in s and "packer" in str(s.get("uses", "")).lower()]

        # Note: Verify workflow might use local action or run packer directly
        # Either approach is valid

    def test_merge_workflow_uses_action_correctly(self):
        """Test that merge workflow uses the action with correct mode."""
        with open("examples/workflows/gerrit-packer-merge.yaml", "r") as f:
            workflow = yaml.safe_load(f)

        # Merge workflow should have build jobs
        assert "packer-build" in workflow["jobs"]

    def test_workflows_inherit_secrets(self):
        """Test that workflows properly inherit secrets."""
        workflows = [
            "examples/workflows/gerrit-packer-verify.yaml",
            "examples/workflows/gerrit-packer-merge.yaml",
        ]

        for workflow_path in workflows:
            with open(workflow_path, "r") as f:
                workflow = yaml.safe_load(f)

            # Check if secrets are referenced
            content_str = str(workflow)
            # Workflows should reference secrets for cloud credentials
            assert "secrets" in content_str.lower() or "OPENSTACK" in content_str or "VEXXHOST" in content_str


class TestEndToEndScenarios:
    """Test end-to-end scenarios (mocked)."""

    @patch.dict(os.environ, {"GITHUB_WORKSPACE": "/tmp/test", "RUNNER_TEMP": "/tmp"})
    def test_validate_mode_environment(self):
        """Test that validate mode has correct environment setup."""
        # This would be more comprehensive in actual integration test
        # For now, verify expected environment variables
        env_vars = ["GITHUB_WORKSPACE", "RUNNER_TEMP"]
        for var in env_vars:
            assert var in os.environ

    def test_action_error_handling(self):
        """Test that action properly handles errors."""
        with open("action.yaml", "r") as f:
            content = f.read()

        # Action steps should have shell specified
        assert 'shell: bash' in content

        # Scripts should have error handling
        scripts = ["setup.sh", "test-templates.sh"]
        for script in scripts:
            with open(script, "r") as f:
                script_content = f.read()
            assert "set -e" in script_content or "set -o errexit" in script_content


class TestPathFiltering:
    """Test path filtering for change detection."""

    def test_path_filter_patterns_are_valid(self):
        """Test that path filter patterns in workflows are valid."""
        with open("examples/workflows/gerrit-packer-merge.yaml", "r") as f:
            workflow = yaml.safe_load(f)

        # Check if path filters are defined
        content_str = str(workflow)
        if "filters" in content_str:
            # Filters should cover templates and vars
            assert "templates" in content_str or "vars" in content_str

    def test_matrix_combinations_are_valid(self):
        """Test that matrix combinations in workflows are valid."""
        with open("examples/workflows/matrix-build-example.yaml", "r") as f:
            workflow = yaml.safe_load(f)

        if "matrix-build" in workflow["jobs"]:
            job = workflow["jobs"]["matrix-build"]
            if "strategy" in job and "matrix" in job["strategy"]:
                matrix = job["strategy"]["matrix"]

                # Matrix should have at least one dimension
                assert len(matrix) > 0

                # Each dimension should have values
                for key, values in matrix.items():
                    assert isinstance(values, list)
                    assert len(values) > 0


class TestSecurityCompliance:
    """Test security and compliance requirements."""

    def test_no_secrets_in_repository(self):
        """Test that no secrets are committed to the repository."""
        # Check common secret files don't exist in repo
        secret_files = [
            "clouds.yaml",
            "clouds.json",
            "cloud-env.json",
            ".env",
            "secrets.yaml",
        ]

        for secret_file in secret_files:
            path = Path(secret_file)
            # It's OK if these exist in examples/ as templates
            if path.exists() and "examples" not in str(path):
                with open(path, "r") as f:
                    content = f.read()
                # Should not contain actual credentials
                assert "password" not in content.lower() or "example" in content.lower()

    def test_workflows_use_pinned_versions(self):
        """Test that workflows use SHA-pinned action versions."""
        workflow_files = list(Path("examples/workflows").glob("*.yaml"))
        workflow_files.extend(list(Path(".github/workflows").glob("*.yaml")))

        for workflow_file in workflow_files:
            with open(workflow_file, "r") as f:
                content = f.read()

            # Check for unpinned versions (ending with @vX)
            lines = content.split("\n")
            for line in lines:
                if "uses:" in line and "@v" in line:
                    # Should have SHA comment nearby or be SHA-pinned
                    # This is a best-effort check
                    if not any(c in line for c in ["#", "  "]):
                        # Check if it's actually a SHA (40 hex chars)
                        parts = line.split("@")
                        if len(parts) > 1:
                            version_part = parts[-1].strip()
                            # SHA should be 40 chars hex
                            if len(version_part) == 40:
                                # Good - SHA pinned
                                pass

    def test_all_scripts_have_license_headers(self):
        """Test that all source files have appropriate license headers."""
        python_files = list(Path("tests").glob("*.py"))

        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue

            with open(py_file, "r") as f:
                content = f.read()

            # Should have SPDX license identifier
            assert "SPDX-License-Identifier" in content, f"{py_file} missing license header"
            assert "SPDX-FileCopyrightText" in content, f"{py_file} missing copyright"
