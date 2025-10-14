# Packer GitHub Action with Tailscale Bastion

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Packer](https://img.shields.io/badge/Packer-1.11.2-02A8EF?logo=packer&logoColor=white)](https://www.packer.io/)
[![Tailscale](https://img.shields.io/badge/Tailscale-VPN-00C896?logo=tailscale&logoColor=white)](https://tailscale.com/)

Reusable GitHub Action for Packer image validation and builds on OpenStack clouds using ephemeral Tailscale bastion hosts for secure connectivity.

## Features

- ✅ **Fully Automated** - Zero-configuration bastion deployment
- ✅ **Secure VPN** - Tailscale mesh network with OAuth support
- ✅ **Ephemeral Bastion** - Auto-provisioned and cleaned up per build
- ✅ **Gerrit Integration** - Triggered by Gerrit verify/merge events
- ✅ **Matrix Builds** - Parallel builds for multiple OS/platform combinations
- ✅ **OpenStack Native** - Works with any OpenStack cloud provider
- ✅ **Production Ready** - Comprehensive error handling and logging

## Architecture

```
GitHub Actions Runner  ←→  [Tailscale VPN]  ←→  Bastion (OpenStack)
         ↓                                              ↓
    Packer Build  ────────────────────────→  Target Instances
```

The action creates an ephemeral bastion host on OpenStack that joins your Tailscale network, enabling secure SSH connectivity for Packer builds without exposing instances to the internet.

## Quick Start

### Prerequisites

- GitHub repository with Packer templates
- OpenStack cloud account (VexxHost, etc.)
- Tailscale account (free tier sufficient)

### 1. Configure Tailscale

Create OAuth client (recommended) or auth key. See [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md) for detailed instructions.

**Quick setup:**

1. Go to [Tailscale OAuth Clients](https://login.tailscale.com/admin/settings/oauth)
2. Generate OAuth client with `auth_keys` scope and tags `tag:ci`, `tag:bastion`
3. Copy client ID and secret

### 2. Configure GitHub Secrets

Add these secrets to your repository:

| Secret                      | Description                 |
| --------------------------- | --------------------------- |
| `TAILSCALE_OAUTH_CLIENT_ID` | OAuth client ID             |
| `TAILSCALE_OAUTH_SECRET`    | OAuth client secret         |
| `OPENSTACK_AUTH_URL`        | OpenStack auth endpoint     |
| `OPENSTACK_USERNAME`        | OpenStack username          |
| `OPENSTACK_PASSWORD`        | OpenStack password          |
| `OPENSTACK_PROJECT_ID`      | OpenStack project/tenant ID |
| `OPENSTACK_REGION`          | OpenStack region name       |
| `OPENSTACK_NETWORK`         | OpenStack network ID        |

### 3. Use the Action

Create `.github/workflows/packer-verify.yaml`:

```yaml
name: Packer Verify

on:
  pull_request:
    paths:
      - "packer/**"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: lfit/releng-packer-action@v1
        with:
          mode: validate
          packer_template: templates/builder.pkr.hcl
          packer_vars: vars/ubuntu-22.04.pkrvars.hcl
```

For build workflows, see [examples/workflows/](examples/workflows/).

## Action Inputs

| Input                       | Description                           | Required         | Default      |
| --------------------------- | ------------------------------------- | ---------------- | ------------ |
| `mode`                      | Operation mode: `validate` or `build` | Yes              | `validate`   |
| `packer_template`           | Path to Packer template file          | Yes              | -            |
| `packer_vars`               | Path to Packer vars file or filter    | No               | -            |
| `tailscale_oauth_client_id` | Tailscale OAuth client ID             | No†              | -            |
| `tailscale_oauth_secret`    | Tailscale OAuth secret                | No†              | -            |
| `tailscale_auth_key`        | Tailscale auth key (legacy)           | No†              | -            |
| `openstack_*`               | OpenStack credentials                 | Yes (build mode) | -            |
| `bastion_*`                 | Bastion configuration                 | No               | See defaults |

† Either OAuth credentials or auth key required for `build` mode

See [action.yaml](action.yaml) for complete input reference.

## Action Outputs

| Output              | Description                       |
| ------------------- | --------------------------------- |
| `validation_status` | Validation result (passed/failed) |
| `build_status`      | Build result (success/failure)    |
| `image_name`        | Name of built image               |
| `bastion_ip`        | Tailscale IP of bastion host      |

## Examples

### Gerrit Verify (Validation Only)

Validates Packer templates when changes are submitted to Gerrit:

```yaml
name: Packer Verify

on:
  repository_dispatch:
    types: [gerrit-patchset-created, gerrit-change-updated]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: lfreleng-actions/gerrit-checkout-action@v1
        with:
          repository: ${{ github.event.client_payload.GERRIT_PROJECT }}
          ref: ${{ github.event.client_payload.GERRIT_PATCHSET_REVISION }}

      - uses: lfit/releng-packer-action@v1
        with:
          mode: validate
          packer_template: templates/*.pkr.hcl
          syntax_only: true
```

### Gerrit Merge (Build Images)

Builds images when changes are merged in Gerrit:

```yaml
name: Packer Build

on:
  repository_dispatch:
    types: [gerrit-change-merged]
  schedule:
    - cron: "0 2 1 * *" # Monthly rebuild

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.generate.outputs.matrix }}
    steps:
      - uses: lfreleng-actions/gerrit-checkout-action@v1

      - id: generate
        run: |
          # Generate matrix based on changed files
          matrix=$(python scripts/generate-matrix.py)
          echo "matrix=$matrix" >> $GITHUB_OUTPUT

  build:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
    steps:
      - uses: lfreleng-actions/gerrit-checkout-action@v1

      - uses: lfit/releng-packer-action@v1
        with:
          mode: build
          packer_template: ${{ matrix.template }}
          packer_vars: ${{ matrix.vars }}
          tailscale_oauth_client_id: ${{ secrets.TAILSCALE_OAUTH_CLIENT_ID }}
          tailscale_oauth_secret: ${{ secrets.TAILSCALE_OAUTH_SECRET }}
          openstack_auth_url: ${{ secrets.OPENSTACK_AUTH_URL }}
          openstack_username: ${{ secrets.OPENSTACK_USERNAME }}
          openstack_password: ${{ secrets.OPENSTACK_PASSWORD }}
          openstack_project_id: ${{ secrets.OPENSTACK_PROJECT_ID }}
          openstack_region: ${{ secrets.OPENSTACK_REGION }}
          openstack_network: ${{ secrets.OPENSTACK_NETWORK }}
```

More examples in [examples/workflows/](examples/workflows/).

## Packer Template Requirements

Templates must support bastion host connectivity:

```hcl
variable "bastion_host" {
  type    = string
  default = ""
}

variable "bastion_user" {
  type    = string
  default = "root"
}

source "openstack" "image" {
  # Standard OpenStack configuration
  flavor              = var.flavor
  image_name          = var.image_name
  source_image_filter = {
    name = var.source_image
  }

  # Bastion configuration for secure connectivity
  ssh_bastion_host     = var.bastion_host != "" ? var.bastion_host : null
  ssh_bastion_username = var.bastion_user

  # Target instance SSH
  ssh_username = "ubuntu"
  ssh_timeout  = "15m"
}
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:

- Local setup and testing
- Contributing guidelines
- Code style requirements
- Release process

### Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/lfit/releng-packer-action.git
cd releng-packer-action
pip install -r requirements-dev.txt
pre-commit install

# Run tests
pre-commit run --all-files
pytest

# Test workflows
gh workflow run test-action-validate.yaml
```

## Documentation

- **[README.md](README.md)** - This file, main overview
- **[TAILSCALE_SETUP.md](TAILSCALE_SETUP.md)** - Tailscale configuration guide
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Developer guide and contributing
- **[examples/](examples/)** - Example workflows for Gerrit integration

## Troubleshooting

### Common Issues

**Tailscale connection failed**

- Verify OAuth client or auth key in GitHub secrets
- Check ACL configuration includes required tags
- See [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md#troubleshooting)

**Bastion not joining Tailscale**

- Check bastion can reach `*.tailscale.com` (outbound HTTPS)
- Review cloud-init logs: `openstack console log show bastion-gh-xxxxx`

**Packer build failed**

- Enable debug mode in workflow
- Verify bastion SSH connectivity
- Check Packer template syntax

**OpenStack authentication failed**

- Verify all credentials in GitHub secrets
- Test with OpenStack CLI locally

See full troubleshooting guide in [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md#troubleshooting).

## License

SPDX-License-Identifier: Apache-2.0

Copyright (c) 2025 Linux Foundation - Licensed under Apache License 2.0

## Acknowledgments

Built using patterns from:

- [releng-reusable-workflows](https://github.com/lfit/releng-reusable-workflows)
- [releng-builder](https://github.com/lfit/releng-builder)

---

**Questions?** Open an [issue](https://github.com/lfit/releng-packer-action/issues) or see documentation above.
