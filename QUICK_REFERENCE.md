# Quick Reference Guide

## For Action Users

### Minimal Working Example

```yaml
- uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    packer_template: "templates/builder.pkr.hcl"
    packer_vars_file: "vars/ubuntu-22.04.pkrvars.hcl"
    cloud_env_json: ${{ secrets.CLOUD_ENV_JSON_B64 }}
    vexxhost_auth_url: ${{ secrets.VEXXHOST_AUTH_URL }}
    vexxhost_project_id: ${{ secrets.VEXXHOST_PROJECT_ID }}
    vexxhost_username: ${{ secrets.VEXXHOST_USERNAME }}
    vexxhost_password: ${{ secrets.VEXXHOST_PASSWORD_B64 }}
    vexxhost_network_id: ${{ secrets.VEXXHOST_NETWORK_ID }}
    tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
```

### Required GitHub Secrets

| Secret Name | How to Get It |
|-------------|---------------|
| `CLOUD_ENV_JSON_B64` | `cat cloud-env.json \| base64 -w 0` |
| `VEXXHOST_AUTH_URL` | `https://auth.vexxhost.net/v3/` |
| `VEXXHOST_PROJECT_ID` | From VexxHost dashboard |
| `VEXXHOST_USERNAME` | Your VexxHost username |
| `VEXXHOST_PASSWORD_B64` | `echo "password" \| base64` |
| `VEXXHOST_NETWORK_ID` | `openstack network list` (UUID) |
| `TAILSCALE_AUTH_KEY` | https://login.tailscale.com/admin/settings/keys |

### Cloud Environment JSON Format

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

**Note:** Leave `ssh_proxy_host` empty - it will be auto-filled with bastion IP.

### Tailscale ACL (Minimum Required)

```json
{
  "tagOwners": {
    "tag:ci": ["autogroup:admin", "autogroup:owner"],
    "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
  },
  "ssh": [
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:bastion"],
      "users": ["root", "ubuntu"]
    }
  ]
}
```

**Full config:** See [docs/TAILSCALE_SETUP.md](docs/TAILSCALE_SETUP.md)

## Common Tasks

### Create Base64-Encoded Secret

```bash
# For cloud-env.json
cat cloud-env.json | base64 -w 0 > cloud-env-b64.txt

# For password
echo -n "your-password" | base64

# For clouds.yaml (optional)
cat clouds.yaml | base64 -w 0 > clouds-b64.txt
```

### Get Network UUID

```bash
# Set OpenStack credentials first
export OS_AUTH_URL=https://auth.vexxhost.net/v3/
export OS_PROJECT_ID=your-project-id
export OS_USERNAME=your-username
export OS_PASSWORD=your-password

# List networks
openstack network list

# Get specific network
openstack network show odlci -c id -f value
```

### Test Packer Template Locally

```bash
# Initialize
packer init templates/builder.pkr.hcl

# Validate
packer validate \
  -var-file=cloud-env.json \
  -var-file=vars/ubuntu-22.04.pkrvars.hcl \
  templates/builder.pkr.hcl
```

## Troubleshooting

### Build Fails Immediately

1. Check GitHub secrets are set correctly
2. Verify Tailscale auth key is valid
3. Check VexxHost credentials with `openstack server list`

### SSH Connection Fails

1. Verify Tailscale ACL has SSH rule (see [docs/TAILSCALE_SETUP.md](docs/TAILSCALE_SETUP.md))
2. Check bastion appears in Tailscale admin console
3. Verify auth key has `tag:ci` permission

### Packer Validation Fails

1. Check template syntax: `packer validate`
2. Verify all required variables are in vars file
3. Ensure provision scripts exist at correct paths

### Bastion Doesn't Start

1. Check OpenStack quotas: `openstack quota show`
2. Verify flavor exists: `openstack flavor list`
3. Check image exists: `openstack image list | grep Ubuntu`
4. Review console logs: `openstack console log show bastion-gh-XXXXX`

## Documentation Index

- **[ACTION_README.md](ACTION_README.md)** - How to use the action
- **[ACTION_IMPLEMENTATION.md](ACTION_IMPLEMENTATION.md)** - Architecture & development
- **[CONVERSION_SUMMARY.md](CONVERSION_SUMMARY.md)** - Overview of changes
- **[docs/TAILSCALE_SETUP.md](docs/TAILSCALE_SETUP.md)** - Tailscale configuration
- **[examples/](examples/)** - Example Packer templates and workflows

## Quick Commands

```bash
# Trigger a build
gh workflow run build-images.yaml

# Watch the build
gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')

# View logs
gh run view --log

# List recent runs
gh run list --workflow=build-images.yaml --limit 5

# Download artifacts
gh run download <run-id>
```

## Support

- 📖 Read the docs (links above)
- 🐛 [File an issue](../../issues)
- 💬 Ask in discussions
- 📧 Contact maintainers

## Version Information

- **Current Version**: Check [releases](../../releases)
- **Stable**: Use `@v1` in workflows
- **Latest**: Use `@main` for development

## Quick Links

- [Tailscale Admin Console](https://login.tailscale.com/admin)
- [VexxHost Dashboard](https://console.vexxhost.net)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Packer Documentation](https://developer.hashicorp.com/packer/docs)
