# VexxHost Tailscale Bastion MVP - Automated Packer Builds

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Packer](https://img.shields.io/badge/Packer-1.11.2-02A8EF?logo=packer&logoColor=white)](https://www.packer.io/)
[![Tailscale](https://img.shields.io/badge/Tailscale-VPN-00C896?logo=tailscale&logoColor=white)](https://tailscale.com/)
[![VexxHost](https://img.shields.io/badge/VexxHost-Cloud-FF6B6B)](https://vexxhost.com/)

Automated Packer image builds on VexxHost OpenStack cloud using GitHub Actions with **ephemeral Tailscale bastion hosts** for secure, zero-configuration connectivity.

## 🌟 Key Features

- ✅ **Fully Automated** - No manual intervention required
- ✅ **Secure VPN** - Tailscale mesh network encryption
- ✅ **Ephemeral Bastion** - Auto-created and destroyed per build
- ✅ **Zero SSH Config** - Tailscale SSH handles authentication
- ✅ **OpenStack Native** - Full VexxHost integration
- ✅ **Cost Effective** - ~$0.02 per build, < $1/month
- ✅ **Production Ready** - Comprehensive error handling and logging
- ✅ **Developer Friendly** - Pre-commit hooks and validation tools

## 🏗️ Architecture

```
GitHub Actions Runner  ←→  [Tailscale VPN]  ←→  Bastion (VexxHost)
         ↓                                              ↓
    Packer Build  ────────────────────────→  Target Instances
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for detailed architecture and workflow stages.

## 🚀 Quick Start

### Prerequisites

- ✅ GitHub repository with Packer files
- ✅ VexxHost account with OpenStack access
- ✅ Tailscale account (free tier works)

### 1. Get Tailscale Credentials

#### Create OAuth Key

1. Go to [Tailscale Settings → OAuth Clients](https://login.tailscale.com/admin/settings/oauth)
2. Click **Generate OAuth client**
3. Settings:
   - **Scopes:** `devices:write`
   - **Tags:** `tag:ci`
4. Copy the client secret → `TAILSCALE_OAUTH_KEY`

#### Create Auth Key

1. Go to [Tailscale Settings → Auth Keys](https://login.tailscale.com/admin/settings/keys)
2. Click **Generate auth key**
3. Settings:
   - ✅ **Ephemeral** (auto-cleanup)
   - ✅ **Reusable** (use for multiple workflows)
   - ✅ **Pre-authorized** (no approval needed)
   - **Tags:** `tag:bastion`
4. **Recommended**: Create OAuth client (see [docs/TAILSCALE_SETUP.md](docs/TAILSCALE_SETUP.md))
   - Or legacy: Copy the auth key → `TAILSCALE_AUTH_KEY`

### 2. Get VexxHost Credentials

1. Log in to [VexxHost Dashboard](https://console.vexxhost.net)
2. Navigate to **API Access** or **Project → API Access**
3. Download OpenStack RC file (v3) or note these values:

```bash
OS_AUTH_URL=https://auth.vexxhost.net/v3
OS_PROJECT_ID=your-project-id
OS_PROJECT_NAME=your-project-name
OS_USERNAME=your-username
OS_PASSWORD=your-password
OS_REGION_NAME=ca-ymq-1  # or your region
```

### 3. Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**

Required secrets:

| Secret Name             | Description          | Example                        |
| ----------------------- | -------------------- | ------------------------------ |
| `TAILSCALE_OAUTH_KEY`   | OAuth client secret  | `tskey-client-...`             |
| `TAILSCALE_AUTH_KEY`    | Auth key for bastion | `tskey-auth-...`               |
| `VEXXHOST_AUTH_URL`     | OpenStack endpoint   | `https://auth.vexxhost.net/v3` |
| `VEXXHOST_PROJECT_ID`   | Project ID           | `abc123...`                    |
| `VEXXHOST_PROJECT_NAME` | Project name         | `my-project`                   |
| `VEXXHOST_USERNAME`     | Your username        | `user@example.com`             |
| `VEXXHOST_PASSWORD`     | Your password        | `your-password`                |
| `VEXXHOST_REGION`       | Region code          | `ca-ymq-1`                     |

Optional secrets (if using existing packer templates):

| Secret Name       | Description                          |
| ----------------- | ------------------------------------ |
| `CLOUD_ENV_B64`   | Base64 encoded Packer cloud env      |
| `CLOUDS_YAML_B64` | Base64 encoded OpenStack clouds.yaml |

### 4. Run Your First Build

1. Go to GitHub → **Actions** tab
2. Select **Packer Build with VexxHost Tailscale Bastion** workflow
3. Click **Run workflow**
4. Configure options (or use defaults):
   - **Packer template:** `builder.pkr.hcl`
   - **Packer vars:** `ubuntu-22.04`
   - **Bastion flavor:** `v3-standard-2`
   - **Bastion image:** `Ubuntu 22.04`
5. Click **Run workflow** (green button)

## Workflow Details

### Architecture

```
GitHub Actions Runner
    ↓ (Tailscale VPN)
Bastion Host (VexxHost)
    ↓ (Internal network)
Build Targets (VexxHost)
```

### Process Flow

1. **Setup** (30s)

   - Checkout code
   - Connect to Tailscale
   - Install OpenStack CLI

2. **Bastion Launch** (60-90s)

   - Create cloud-init script
   - Launch VexxHost instance
   - Wait for Tailscale connection

3. **Packer Build** (5-15 min)

   - Initialize Packer plugins
   - Validate templates
   - Build images via bastion

4. **Cleanup** (30s)
   - Upload logs/artifacts
   - Delete bastion instance
   - Disconnect Tailscale

### Workflow Inputs

| Input             | Description          | Default           |
| ----------------- | -------------------- | ----------------- |
| `packer_template` | Template to build    | `builder.pkr.hcl` |
| `packer_vars`     | Vars file filter     | `ubuntu-22.04`    |
| `bastion_flavor`  | Instance flavor      | `v3-standard-2`   |
| `bastion_image`   | Base image           | `Ubuntu 22.04`    |
| `debug_mode`      | Enable debug logging | `false`           |

## Repository Structure

```
packer-jobs/
├── .github/
│   └── workflows/
│       └── packer-vexxhost-bastion-build.yaml
├── .pre-commit-config.yaml
├── .yamllint.conf
├── README.md
├── docs/
│   ├── QUICK_START.md
│   └── TROUBLESHOOTING.md
└── packer/ or common-packer/
    ├── templates/
    │   └── *.pkr.hcl
    ├── vars/
    │   └── *.pkrvars.hcl
    └── provision/
        └── provisioning scripts
```

## Packer Template Requirements

Your Packer templates should support bastion host configuration:

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
  # ... other config ...

  # Use bastion for SSH connectivity
  ssh_bastion_host     = var.bastion_host
  ssh_bastion_username = var.bastion_user
}
```

## 🛠️ Development

### Setup Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Local Testing

**Test OpenStack credentials:**

```bash
export OS_AUTH_URL="https://auth.vexxhost.net/v3"
export OS_PROJECT_NAME="your-project"
export OS_USERNAME="your-username"
export OS_PASSWORD="your-password"
export OS_REGION_NAME="ca-ymq-1"

openstack server list
```

**Validate Packer templates:**

```bash
./test-templates.sh
```

**Test cloud-init syntax:**

```bash
cloud-init schema --config-file templates/bastion-cloud-init.yaml
```

## 🐛 Troubleshooting

### Common Issues

| Problem               | Solution                                      |
| --------------------- | --------------------------------------------- |
| OpenStack auth failed | Verify credentials in GitHub secrets          |
| Tailscale timeout     | Check auth key settings (ephemeral, reusable) |
| Bastion not joining   | Review cloud-init logs via console            |
| Packer build failed   | Enable debug mode, check SSH connectivity     |

**Detailed troubleshooting:** See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

### Debug Mode

```yaml
# Workflow dispatch input
debug_mode: true

# Or set in workflow
env:
  PACKER_LOG: 1
  ACTIONS_STEP_DEBUG: true
```

### View Bastion Logs

```bash
# Via OpenStack console
openstack console log show bastion-gh-12345 --lines 100

# Via SSH (if accessible)
ssh root@<bastion-ip> cat /var/log/bastion-init.log
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 15 minutes
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed design and workflow
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Cloud-Init Reference](docs/BASTION_CLOUD_INIT.md)** - Bastion configuration
- **[Setup Checklist](CHECKLIST.md)** - Verification steps
- **[Examples](examples/README.md)** - Sample Packer templates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Install pre-commit hooks (`pre-commit install`)
4. Make changes and commit (`git commit -am 'Add feature'`)
5. Push to branch (`git push origin feature/amazing`)
6. Open Pull Request

## 📖 Resources

- **Tailscale:** https://tailscale.com/kb/
- **VexxHost:** https://docs.vexxhost.com/
- **Packer:** https://developer.hashicorp.com/packer/docs
- **OpenStack:** https://docs.openstack.org/python-openstackclient/
- **GitHub Actions:** https://docs.github.com/en/actions

## 📄 License

SPDX-License-Identifier: Apache-2.0

Copyright (c) 2025 - Licensed under the Apache License, Version 2.0

## ⭐ Acknowledgments

Based on patterns from:

- [releng-common-packer](https://github.com/lfit/releng-common-packer) - Packer validation workflows
- [releng-builder](https://github.com/lfit/releng-builder) - Tailscale bastion implementation

---

**Questions?** Open an issue or see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
