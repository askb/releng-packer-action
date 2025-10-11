# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Pytest configuration and fixtures for action tests."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        "GITHUB_WORKSPACE": "/tmp/workspace",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_ACTION_PATH": "/tmp/action",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def mock_secrets():
    """Mock GitHub secrets."""
    return {
        "VEXXHOST_AUTH_URL": "https://auth.vexxhost.net/v3/",
        "VEXXHOST_PROJECT_ID": "test-project-id",
        "VEXXHOST_USERNAME": "test-user",
        "VEXXHOST_PASSWORD_B64": "dGVzdC1wYXNzd29yZA==",  # base64: test-password
        "VEXXHOST_NETWORK_ID": "test-network-uuid",
        "TAILSCALE_AUTH_KEY": "tskey-auth-test",
        "CLOUD_ENV_JSON_B64": "eyJ0ZXN0IjogInZhbHVlIn0=",  # base64: {"test": "value"}
    }
