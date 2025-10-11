# Packer VexxHost Tailscale Bastion Action

A reusable GitHub Action for building OpenStack images using Packer through a Tailscale bastion host on VexxHost.

## Features

- 🔒 Secure builds through Tailscale-connected bastion host
- ☁️ OpenStack/VexxHost image building with Packer
- 🚀 Automated bastion creation and cleanup
- 📦 Flexible input configuration via JSON/YAML files
- 🔍 Optional debug logging and artifact upload

## Usage

### Basic Example

```yaml
name: Build Image
on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Build Packer Image
        uses: lfit/packer-vexxhost-bastion-action@v1
        with:
          # Packer configuration
          packer_template: "templates/builder.pkr.hcl"
          packer_vars_file: "vars/ubuntu-22.04.pkrvars.hcl"
          packer_working_dir: "packer"
          
          # Cloud configuration (base64 encoded)
          cloud_env_json: ${{ secrets.CLOUD_ENV_JSON_B64 }}
          
          # VexxHost credentials
          vexxhost_auth_url: ${{ secrets.VEXXHOST_AUTH_URL }}
          vexxhost_project_id: ${{ secrets.VEXXHOST_PROJECT_ID }}
          vexxhost_username: ${{ secrets.VEXXHOST_USERNAME }}
          vexxhost_password: ${{ secrets.VEXXHOST_PASSWORD_B64 }}
          vexxhost_network_id: ${{ secrets.VEXXHOST_NETWORK_ID }}
          
          # Tailscale
          tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
```

### Advanced Example with Custom Bastion

```yaml
- name: Build Packer Image
  uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    # Packer configuration
    packer_template: "templates/builder.pkr.hcl"
    packer_vars_file: "vars/ubuntu-22.04.pkrvars.hcl"
    packer_working_dir: "."
    packer_version: "1.11.2"
    
    # Cloud configuration
    cloud_env_json: ${{ secrets.CLOUD_ENV_JSON_B64 }}
    clouds_yaml: ${{ secrets.CLOUDS_YAML_B64 }}  # Optional
    
    # VexxHost credentials
    vexxhost_auth_url: "https://auth.vexxhost.net/v3/"
    vexxhost_project_id: ${{ secrets.VEXXHOST_PROJECT_ID }}
    vexxhost_username: ${{ secrets.VEXXHOST_USERNAME }}
    vexxhost_password: ${{ secrets.VEXXHOST_PASSWORD_B64 }}
    vexxhost_region: "ca-ymq-1"
    vexxhost_network_id: ${{ secrets.VEXXHOST_NETWORK_ID }}
    
    # Bastion configuration
    bastion_flavor: "v3-standard-4"
    bastion_image: "Ubuntu 22.04.5 LTS (x86_64) [2025-03-27]"
    bastion_network: "odlci"
    bastion_wait_timeout: "600"
    
    # Tailscale
    tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
    
    # Build options
    debug_mode: "true"
    upload_logs: "true"
    log_retention_days: "7"
```

## Inputs

### Required Inputs

| Input | Description |
|-------|-------------|
| `packer_template` | Path to Packer template file (e.g., `templates/builder.pkr.hcl`) |
| `packer_vars_file` | Path to Packer variables file (e.g., `vars/ubuntu-22.04.pkrvars.hcl`) |
| `cloud_env_json` | Cloud environment JSON configuration (base64 encoded) |
| `vexxhost_auth_url` | VexxHost/OpenStack authentication URL |
| `vexxhost_project_id` | VexxHost/OpenStack project/tenant ID |
| `vexxhost_username` | VexxHost/OpenStack username |
| `vexxhost_password` | VexxHost/OpenStack password (base64 encoded recommended) |
| `vexxhost_network_id` | VexxHost/OpenStack network UUID for Packer builds |
| `tailscale_auth_key` | Tailscale authentication key |

### Optional Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `packer_working_dir` | Working directory containing Packer files | `.` |
| `packer_version` | Packer version to use | `1.11.2` |
| `clouds_yaml` | OpenStack clouds.yaml configuration (base64 encoded) | `""` |
| `vexxhost_region` | VexxHost/OpenStack region | `ca-ymq-1` |
| `bastion_flavor` | OpenStack flavor for bastion instance | `v3-standard-2` |
| `bastion_image` | Base image for bastion host | `Ubuntu 22.04.5 LTS (x86_64) [2025-03-27]` |
| `bastion_network` | Network name for bastion host | `odlci` |
| `bastion_ssh_key` | SSH key name for bastion | `""` |
| `bastion_wait_timeout` | Timeout in seconds to wait for bastion | `300` |
| `tailscale_version` | Tailscale version | `latest` |
| `debug_mode` | Enable debug logging | `false` |
| `upload_logs` | Upload build logs as artifacts | `true` |
| `log_retention_days` | Days to retain log artifacts | `30` |

## Outputs

| Output | Description |
|--------|-------------|
| `bastion_ip` | Tailscale IP address of the bastion host |
| `build_status` | Status of the Packer build (`success` or `failure`) |
| `image_name` | Name of the built image |

## Cloud Environment JSON Format

The `cloud_env_json` input should be a base64-encoded JSON file with the following structure:

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

**Note:** The `ssh_proxy_host` field will be automatically populated with the bastion's Tailscale IP.

### Creating Base64 Encoded JSON

```bash
cat cloud-env.json | base64 -w 0 > cloud-env-b64.txt
```

Then add the contents of `cloud-env-b64.txt` as a GitHub secret.

## Prerequisites

### 1. Tailscale ACL Configuration

Your Tailscale ACL must allow SSH connections from CI runners to bastion hosts.

**See [docs/TAILSCALE_SETUP.md](docs/TAILSCALE_SETUP.md) for complete Tailscale configuration guide.**

Quick reference - required ACL rules:

```json
{
  "tagOwners": {
    "tag:ci": ["autogroup:admin", "autogroup:owner"],
    "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["autogroup:admin", "tag:ci", "tag:bastion"],
      "dst": ["*:*"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["autogroup:member", "tag:ci"],
      "dst": ["tag:bastion"],
      "users": ["root", "ubuntu", "autogroup:nonroot"]
    }
  ]
}
```

### 2. GitHub Secrets

Configure these secrets in your repository:

- `CLOUD_ENV_JSON_B64`: Base64-encoded cloud environment JSON
- `VEXXHOST_AUTH_URL`: VexxHost authentication URL
- `VEXXHOST_PROJECT_ID`: Your VexxHost project ID
- `VEXXHOST_USERNAME`: VexxHost username
- `VEXXHOST_PASSWORD_B64`: Base64-encoded VexxHost password
- `VEXXHOST_NETWORK_ID`: Network UUID for your builds
- `TAILSCALE_AUTH_KEY`: Tailscale auth key with `tag:ci` permission

### 3. Packer Template Requirements

Your Packer template must:
- Use `ssh_bastion_agent_auth = true` for bastion connection
- Accept `bastion_host` and `bastion_user` variables
- Use variables from `cloud_env_json` for cloud credentials

## Example Repository Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── build-image.yaml
├── packer/
│   ├── templates/
│   │   └── builder.pkr.hcl
│   ├── vars/
│   │   ├── ubuntu-22.04.pkrvars.hcl
│   │   └── ubuntu-24.04.pkrvars.hcl
│   └── provision/
│       └── baseline.sh
└── README.md
```

## Troubleshooting

### Bastion fails to join Tailscale

- Verify `TAILSCALE_AUTH_KEY` has correct permissions
- Check Tailscale ACL allows `tag:bastion`
- Increase `bastion_wait_timeout`

### SSH connection to bastion fails

- Ensure Tailscale ACL has SSH rule for `tag:ci` → `tag:bastion`
- Verify SSH agent is running (action handles this automatically)

### Packer build fails

- Enable `debug_mode: "true"` for detailed logs
- Check `cloud_env_json` has correct credentials
- Verify network UUID in `vexxhost_network_id`

## License

Apache-2.0

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
