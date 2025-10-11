# Packer VexxHost Bastion Action - Implementation Guide

## Overview

This repository has been converted into a reusable GitHub composite action that can be used by other repositories (like ci-management or builder repos) to build OpenStack images using Packer through a Tailscale bastion host.

## Repository Structure

```
packer-vexxhost-bastion-action/
├── action.yaml                           # Main composite action definition
├── ACTION_README.md                      # Action documentation for users
├── README.md                             # Repository documentation
├── examples/
│   ├── templates/
│   │   └── builder.pkr.hcl              # Example Packer template
│   ├── vars/
│   │   └── ubuntu-22.04.pkrvars.hcl     # Example variables
│   ├── provision/
│   │   └── baseline.sh                   # Example provisioning script
│   └── workflows/
│       └── use-action-example.yaml       # Example of using the action
├── templates/
│   └── bastion-cloud-init.yaml          # Bastion cloud-init template
└── .github/
    └── workflows/
        └── packer-vexxhost-bastion-build.yaml  # Self-test workflow
```

## How It Works

### As a Standalone Repository

The `.github/workflows/packer-vexxhost-bastion-build.yaml` workflow can still be used directly in this repository for testing and development.

### As a Reusable Action

Other repositories can use this action by referencing it in their workflows:

```yaml
- uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    packer_template: "path/to/template.pkr.hcl"
    packer_vars_file: "path/to/vars.pkrvars.hcl"
    # ... other inputs
```

## Usage from CI/Builder Repositories

### 1. Caller Repository Structure

A repository using this action should have:

```
ci-management/ or builder-repo/
├── .github/
│   └── workflows/
│       └── build-images.yaml    # Calls the action
├── packer/
│   ├── templates/
│   │   └── builder.pkr.hcl
│   ├── vars/
│   │   ├── ubuntu-22.04.pkrvars.hcl
│   │   └── ubuntu-24.04.pkrvars.hcl
│   └── provision/
│       └── scripts...
└── README.md
```

### 2. Required Secrets in Caller Repository

The calling repository must configure these secrets:

| Secret                  | Description                               | Example                         |
| ----------------------- | ----------------------------------------- | ------------------------------- |
| `CLOUD_ENV_JSON_B64`    | Base64-encoded cloud environment JSON     | See format below                |
| `VEXXHOST_AUTH_URL`     | OpenStack auth URL                        | `https://auth.vexxhost.net/v3/` |
| `VEXXHOST_PROJECT_ID`   | Project/Tenant UUID                       | `61975f2c-7c17-4d69-82fa-...`   |
| `VEXXHOST_USERNAME`     | OpenStack username                        | `user@example.com`              |
| `VEXXHOST_PASSWORD_B64` | Base64-encoded password                   | `base64-encoded-password`       |
| `VEXXHOST_NETWORK_ID`   | Network UUID for builds                   | `b5fcd86e-efac-4997-b8bc-...`   |
| `TAILSCALE_AUTH_KEY`    | Tailscale auth key with tag:ci permission | `tskey-auth-...`                |

### 3. Cloud Environment JSON Format

Create a `cloud-env.json` file:

```json
{
  "cloud_auth_url": "https://auth.vexxhost.net/v3/",
  "cloud_tenant": "your-project-id",
  "cloud_user": "your-username",
  "cloud_pass": "your-password",
  "cloud_network": "network-uuid",
  "ssh_proxy_host": ""
}
```

Encode it:

```bash
cat cloud-env.json | base64 -w 0 > cloud-env-b64.txt
```

Add the content of `cloud-env-b64.txt` as the `CLOUD_ENV_JSON_B64` secret.

**Note:** The `ssh_proxy_host` field will be automatically populated with the bastion's Tailscale IP by the action.

### 4. Example Caller Workflow

In your ci-management repository, create `.github/workflows/build-images.yaml`:

```yaml
name: Build Images

on:
  workflow_dispatch:
    inputs:
      image_type:
        description: "Image to build"
        required: true
        type: choice
        options:
          - ubuntu-22.04
          - ubuntu-24.04

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build ${{ inputs.image_type }} Image
        uses: lfit/packer-vexxhost-bastion-action@v1
        with:
          packer_template: "packer/templates/builder.pkr.hcl"
          packer_vars_file: "packer/vars/${{ inputs.image_type }}.pkrvars.hcl"
          packer_working_dir: "packer"
          cloud_env_json: ${{ secrets.CLOUD_ENV_JSON_B64 }}
          vexxhost_auth_url: ${{ secrets.VEXXHOST_AUTH_URL }}
          vexxhost_project_id: ${{ secrets.VEXXHOST_PROJECT_ID }}
          vexxhost_username: ${{ secrets.VEXXHOST_USERNAME }}
          vexxhost_password: ${{ secrets.VEXXHOST_PASSWORD_B64 }}
          vexxhost_network_id: ${{ secrets.VEXXHOST_NETWORK_ID }}
          tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
```

## Input Configuration Methods

### Method 1: Pass Files as Base64-Encoded Inputs (Recommended)

- Store cloud-env.json and clouds.yaml as base64-encoded secrets
- Action decodes them at runtime
- Most secure, no files in repository

### Method 2: Files in Repository

- Store templates and vars in the calling repository
- Reference them via `packer_template` and `packer_vars_file` inputs
- Credentials still come from secrets

### Method 3: Hybrid (Best Practice)

- Templates and vars in calling repository (version controlled)
- Credentials as base64-encoded secrets (secure)
- This is what the example demonstrates

## Action Workflow

When a caller repository uses this action, it:

1. **Sets up Tailscale** - Connects GitHub runner to Tailscale network
2. **Installs OpenStack CLI** - For managing bastion instance
3. **Creates Bastion** - Launches ephemeral bastion on VexxHost
4. **Waits for Bastion** - Confirms bastion joined Tailscale
5. **Prepares Cloud Config** - Creates cloud-env.json with bastion IP
6. **Sets up Packer** - Installs specified Packer version
7. **Initializes** - Runs `packer init`
8. **Validates** - Runs `packer validate`
9. **Builds** - Runs `packer build` through bastion
10. **Cleans up** - Destroys bastion instance

## Outputs

The action provides outputs that can be used in subsequent steps:

```yaml
- name: Build Image
  id: build
  uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    # inputs...

- name: Use outputs
  run: |
    echo "Bastion IP was: ${{ steps.build.outputs.bastion_ip }}"
    echo "Build status: ${{ steps.build.outputs.build_status }}"
```

## Development and Testing

### Testing the Action Locally

Use the included workflow in this repository:

```bash
gh workflow run packer-vexxhost-bastion-build.yaml
```

### Testing from Another Repository

1. Push changes to this repository
2. In caller repository, reference the action:
   ```yaml
   uses: owner/packer-vexxhost-bastion-action@main
   ```
3. Run the workflow in caller repository

### Versioning

- Development: Use `@main`
- Production: Create tags (`@v1`, `@v1.0.0`)

## Migration from Standalone to Action Usage

If you have an existing repository using the standalone workflow:

1. **Keep your Packer files** in the original repository
2. **Add the action** to your workflow:
   - Replace the standalone workflow
   - Reference this action
   - Pass paths to your Packer files
3. **Move secrets** if needed
4. **Test** before removing old workflow

## Benefits

1. **Reusability** - Use from multiple repositories
2. **Centralized Updates** - Fix bugs once, benefits all users
3. **Simplified Workflows** - Caller workflows are much simpler
4. **Consistent Behavior** - Same bastion setup across projects
5. **Version Control** - Pin to specific versions

## Next Steps

1. **Create a Release** - Tag v1.0.0 for stable version
2. **Document Packer Template Requirements** - What variables/structure needed
3. **Add Tests** - Automated testing of the action
4. **Create More Examples** - Different cloud providers, etc.

## Support

For issues or questions:

- File an issue in this repository
- See ACTION_README.md for usage documentation
- Check examples/ directory for working examples
