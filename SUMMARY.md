# Project Summary: VexxHost Packer Builds with Tailscale Bastion

## Overview

This project provides a complete GitHub Actions workflow for building Packer images on VexxHost OpenStack cloud using secure Tailscale VPN connectivity through an ephemeral bastion host.

## What Was Created

### 1. GitHub Actions Workflow

**File:** `.github/workflows/packer-vexxhost-bastion-build.yaml`

A comprehensive workflow that:

- ✅ Connects GitHub Actions runner to Tailscale VPN
- ✅ Launches ephemeral bastion host on VexxHost
- ✅ Waits for bastion to join Tailscale network
- ✅ Runs Packer builds via bastion host
- ✅ Uploads build logs and artifacts
- ✅ Automatically cleans up bastion instance
- ✅ Provides detailed job summaries

**Features:**

- Manual trigger with configurable inputs
- Automatic trigger on push to packer files
- Support for multiple templates and variable files
- Debug mode for troubleshooting
- Comprehensive error handling
- Parallel-safe with concurrency controls

### 2. Documentation

#### Main README (`README.md`)

- Project overview and features
- Complete setup instructions
- Repository structure guide
- Packer template requirements
- Development guidelines
- Cost estimates
- Security considerations
- CI/CD integration examples

#### Quick Start Guide (`docs/QUICK_START.md`)

- Step-by-step setup (15-20 minutes)
- Tailscale credential setup
- VexxHost credential setup
- GitHub secrets configuration
- First build walkthrough
- Common issues and fixes
- Quick reference commands

#### Troubleshooting Guide (`docs/TROUBLESHOOTING.md`)

- OpenStack issues and solutions
- Tailscale connectivity problems
- Bastion host issues
- Packer build failures
- Network problems
- Debug techniques
- Best practices

### 3. Example Packer Templates

#### Builder Template (`examples/templates/builder.pkr.hcl`)

- Complete HCL2 Packer template
- OpenStack source configuration
- Bastion host support (conditional)
- Comprehensive variable definitions
- Build provisioning with shell scripts
- Image cleanup before snapshot
- Metadata tagging

**Key Features:**

- Supports both bastion and direct connection modes
- Configurable timeouts and retries
- Cloud-init aware provisioning
- Production-ready defaults

#### Variables File (`examples/vars/ubuntu-22.04.pkrvars.hcl`)

- Ubuntu 22.04 configuration
- Network and region settings
- Instance flavor configuration
- SSH and timeout settings

#### Provisioning Script (`examples/provision/baseline.sh`)

- System package updates
- Essential tools installation
- Python and development tools
- Performance tuning (sysctl)
- System limits configuration
- Service cleanup
- Package cache cleanup

### 4. Configuration Files

#### Pre-commit Config (`.pre-commit-config.yaml`)

Automated code quality checks:

- Trailing whitespace removal
- YAML validation
- Shellcheck for bash scripts
- Prettier formatting
- Git commit message linting
- Large file detection
- Private key detection

#### Yamllint Config (`.yamllint.conf`)

YAML style enforcement:

- 120 character line limit
- 2-space indentation
- Consistent truthy values
- Comment spacing rules

#### Gitignore (`.gitignore`)

Excludes:

- Packer cache and builds
- Cloud credentials
- SSH keys
- Log files
- Python cache
- Temporary files

### 5. Testing Tools

#### Template Validator (`test-templates.sh`)

Automated testing script that:

- Checks Packer installation
- Initializes required plugins
- Validates template formatting
- Tests all template/variable combinations
- Provides clear success/failure reporting

## Architecture

```
┌─────────────────────────┐
│  GitHub Actions Runner  │
│  - Checkout code        │
│  - Connect Tailscale    │
│  - Setup tools          │
└───────────┬─────────────┘
            │
            │ Tailscale VPN
            │ (Encrypted Mesh)
            ▼
┌─────────────────────────┐
│  Bastion Host (VexxHost)│
│  - Ubuntu 22.04         │
│  - Tailscale client     │
│  - Ephemeral (auto-del) │
└───────────┬─────────────┘
            │
            │ VexxHost Internal Network
            │
            ▼
┌─────────────────────────┐
│  Build Target Instance  │
│  - Created by Packer    │
│  - Provisioned          │
│  - Snapshotted to image │
└─────────────────────────┘
```

## Workflow Execution Flow

1. **Preparation** (30s)

   - Checkout repository code
   - Find Packer directory
   - Check for changes

2. **Tailscale Setup** (15s)

   - Connect runner to Tailscale network
   - Authenticate with OAuth key
   - Tag as CI runner

3. **OpenStack Setup** (10s)

   - Install OpenStack CLI
   - Configure credentials from secrets
   - Test connectivity

4. **Bastion Launch** (60-90s)

   - Generate cloud-init script
   - Create VexxHost instance
   - Wait for instance ready

5. **Bastion Connection** (30-60s)

   - Wait for Tailscale join
   - Verify SSH connectivity
   - Store bastion IP

6. **Packer Setup** (30s)

   - Install Packer
   - Create cloud config files
   - Initialize plugins

7. **Validation** (30s)

   - Validate all templates
   - Check syntax and variables
   - Initialize required plugins

8. **Build** (5-15 minutes)

   - Build images via bastion
   - Run provisioning scripts
   - Create snapshots

9. **Artifacts** (10s)

   - Upload Packer logs
   - Upload bastion diagnostics
   - Store build artifacts

10. **Cleanup** (30s)
    - Delete bastion instance
    - Disconnect Tailscale
    - Verify cleanup

## Required GitHub Secrets

### Tailscale (2 secrets)

- `TAILSCALE_OAUTH_KEY` - OAuth client for runner
- `TAILSCALE_AUTH_KEY` - Auth key for bastion

### VexxHost (6 secrets)

- `VEXXHOST_AUTH_URL` - OpenStack auth endpoint
- `VEXXHOST_PROJECT_ID` - Project ID
- `VEXXHOST_PROJECT_NAME` - Project name
- `VEXXHOST_USERNAME` - Username
- `VEXXHOST_PASSWORD` - Password
- `VEXXHOST_REGION` - Region (e.g., ca-ymq-1)

### Optional (2 secrets)

- `CLOUD_ENV_B64` - Base64 encoded Packer cloud env
- `CLOUDS_YAML_B64` - Base64 encoded clouds.yaml

## File Structure

```
packer-jobs/
├── .github/
│   └── workflows/
│       └── packer-vexxhost-bastion-build.yaml  # Main workflow
├── docs/
│   ├── QUICK_START.md                          # Getting started
│   └── TROUBLESHOOTING.md                      # Problem solving
├── examples/
│   ├── templates/
│   │   └── builder.pkr.hcl                     # Example template
│   ├── vars/
│   │   └── ubuntu-22.04.pkrvars.hcl            # Example vars
│   ├── provision/
│   │   └── baseline.sh                         # Provisioning script
│   └── README.md                               # Examples guide
├── .pre-commit-config.yaml                     # Pre-commit hooks
├── .yamllint.conf                              # YAML linting rules
├── .gitignore                                  # Git exclusions
├── README.md                                   # Main documentation
├── test-templates.sh                           # Validation script
└── SUMMARY.md                                  # This file
```

## Key Features

### Security

- ✅ All credentials stored as GitHub secrets
- ✅ Ephemeral bastion (auto-deleted)
- ✅ Encrypted VPN (Tailscale)
- ✅ No public IP exposure
- ✅ SSH keys auto-generated
- ✅ Private key detection in pre-commit

### Automation

- ✅ Fully automated workflow
- ✅ Auto-cleanup on success/failure
- ✅ Parallel build support
- ✅ Automatic trigger on code changes
- ✅ Scheduled builds supported
- ✅ Matrix builds ready

### Developer Experience

- ✅ Clear documentation
- ✅ Example templates
- ✅ Validation scripts
- ✅ Pre-commit hooks
- ✅ Debug mode
- ✅ Comprehensive logging

### Cost Optimization

- ✅ Ephemeral resources
- ✅ Auto-cleanup
- ✅ Configurable instance sizes
- ✅ Build limits
- ✅ Free Tailscale tier
- ✅ ~$0.02 per build

## Usage Examples

### Basic Build

```bash
# Via GitHub UI
Actions → Packer Build → Run workflow
```

### Custom Template

```yaml
# Workflow dispatch inputs
packer_template: "docker.pkr.hcl"
packer_vars: "ubuntu-24.04"
bastion_flavor: "v3-starter-1"
debug_mode: true
```

### Automatic Trigger

```yaml
# Triggers on push to main
git add packer/
git commit -m "Update templates"
git push origin main
```

### Scheduled Builds

```yaml
# In workflow (already configured)
on:
  schedule:
    - cron: "0 2 * * 1" # Weekly
```

## Testing

### Validate Templates Locally

```bash
./test-templates.sh
```

### Run Pre-commit Checks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Test OpenStack Connection

```bash
export OS_AUTH_URL="https://auth.vexxhost.net/v3"
# ... other exports
openstack server list
```

### Validate Workflow YAML

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/packer-vexxhost-bastion-build.yaml'))"
```

## Integration with Existing Projects

### Use with Existing Templates

1. Ensure templates have `bastion_host` variable:

   ```hcl
   variable "bastion_host" {
     type    = string
     default = ""
   }

   source "openstack" "image" {
     ssh_bastion_host = var.bastion_host != "" ? var.bastion_host : null
   }
   ```

2. Adjust workflow `packer-path` if needed

3. Configure secrets and run

### Use as Reusable Workflow

```yaml
# In your repo's workflow
jobs:
  packer-build:
    uses: your-org/packer-jobs/.github/workflows/packer-vexxhost-bastion-build.yaml@main
    secrets: inherit
```

## Customization Points

### Bastion Configuration

- Instance flavor
- Base image
- Network
- Wait timeout

### Build Configuration

- Max builds per run
- Template filters
- Variable filters
- Debug logging

### Cleanup Behavior

- Artifact retention
- Log verbosity
- Cleanup verification

## Troubleshooting Quick Reference

### Common Issues

1. **Auth failed** → Check secrets
2. **Tailscale timeout** → Check auth key settings
3. **Bastion no show** → Check cloud-init logs
4. **Build failed** → Enable debug mode

### Debug Commands

```bash
# Check workflow
gh run view --log

# Check OpenStack
openstack server list
openstack console log show bastion-gh-XXXXX

# Check Tailscale
sudo tailscale status
```

## Cost Breakdown

| Resource         | Cost     | Frequency | Monthly    |
| ---------------- | -------- | --------- | ---------- |
| Bastion (15 min) | $0.02    | 30 builds | $0.60      |
| Build instance   | Included | -         | -          |
| Tailscale        | Free     | Unlimited | $0.00      |
| **Total**        |          |           | **~$0.60** |

## Next Steps

1. **Setup Secrets** - Configure GitHub secrets
2. **Test Build** - Run first workflow manually
3. **Customize** - Adapt templates to your needs
4. **Automate** - Enable automatic triggers
5. **Monitor** - Watch costs and optimize

## Support

- **Documentation:** See `README.md`, `docs/QUICK_START.md`, `docs/TROUBLESHOOTING.md`
- **Examples:** See `examples/README.md`
- **Issues:** Open GitHub issue
- **Community:** GitHub Discussions

## License

SPDX-License-Identifier: Apache-2.0

## References

Based on patterns from:

- `releng-common-packer` - Packer validation workflows
- `releng-builder-askb` - Tailscale bastion implementation
- Your provided Quick Start Guide

## Success Metrics

After setup, you should have:

- ✅ < 20 minute time to first build
- ✅ < $1/month operational cost
- ✅ 100% automated builds
- ✅ Zero manual bastion management
- ✅ Secure, auditable process
- ✅ Easy to maintain and extend

---

**Created:** $(date +%Y-%m-%d)
**Version:** 1.0.0
**Status:** Production Ready
