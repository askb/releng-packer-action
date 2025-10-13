# OAuth Client Support Implementation Summary

## Changes Made

### 1. Updated `action.yaml` Inputs

Added new OAuth-specific inputs with proper ordering (OAuth first as recommended):

- **`tailscale_oauth_client_id`**: OAuth client ID (recommended)
- **`tailscale_oauth_secret`**: OAuth client secret (recommended)
- **`tailscale_auth_key`**: Legacy auth key (deprecated but supported)
- **`tailscale_tags`**: Flexible tag assignment (default: `tag:ci`)

### 2. Updated Tailscale Setup Steps

The action now supports both authentication methods:

**OAuth Method (Primary):**
```yaml
- name: Setup Tailscale VPN (OAuth)
  if: inputs.mode == 'build' && inputs.tailscale_oauth_client_id != '' && inputs.tailscale_oauth_secret != ''
  uses: tailscale/github-action@6cae46e2d796f265265cfcf628b72a32b4d7cade # v3.3.0
  with:
    oauth-client-id: ${{ inputs.tailscale_oauth_client_id }}
    oauth-secret: ${{ inputs.tailscale_oauth_secret }}
    version: ${{ inputs.tailscale_version }}
    tags: ${{ inputs.tailscale_tags }}
    hostname: github-runner-${{ github.run_id }}
    args: --ssh --accept-routes --accept-dns=false
```

**Auth Key Method (Legacy):**
```yaml
- name: Setup Tailscale VPN (Auth Key - Legacy)
  if: inputs.mode == 'build' && (inputs.tailscale_oauth_client_id == '' || inputs.tailscale_oauth_secret == '') && inputs.tailscale_auth_key != ''
  uses: tailscale/github-action@6cae46e2d796f265265cfcf628b72a32b4d7cade # v3.3.0
  with:
    authkey: ${{ inputs.tailscale_auth_key }}
    version: ${{ inputs.tailscale_version }}
    hostname: github-runner-${{ github.run_id }}
    args: --ssh --accept-routes --accept-dns=false
```

### 3. Added Credential Validation

A validation step ensures proper configuration:

```bash
if [[ -z "$tailscale_oauth_client_id" ]] && [[ -z "$tailscale_auth_key" ]]; then
  echo "❌ Error: Either OAuth or auth key must be provided"
  exit 1
fi
```

### 4. Example Workflows Updated

The `gerrit-packer-merge.yaml` already uses OAuth inputs:

```yaml
tailscale_oauth_client_id: ${{ secrets.TAILSCALE_OAUTH_CLIENT_ID }}
tailscale_oauth_secret: ${{ secrets.TAILSCALE_OAUTH_SECRET }}
```

## Usage

### Using OAuth (Recommended)

```yaml
- uses: lfit/packer-action@main
  with:
    mode: build
    tailscale_oauth_client_id: ${{ secrets.TAILSCALE_OAUTH_CLIENT_ID }}
    tailscale_oauth_secret: ${{ secrets.TAILSCALE_OAUTH_SECRET }}
    tailscale_tags: "tag:ci,tag:bastion"
    # ... other inputs
```

### Using Auth Key (Legacy)

```yaml
- uses: lfit/packer-action@main
  with:
    mode: build
    tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
    # ... other inputs
```

## Required Secrets

### For OAuth Method
- `TAILSCALE_OAUTH_CLIENT_ID` - OAuth client ID
- `TAILSCALE_OAUTH_SECRET` - OAuth client secret

### For Auth Key Method
- `TAILSCALE_AUTH_KEY` - Pre-generated auth key

## Documentation

The `docs/TAILSCALE_SETUP.md` already contains:
- Complete ACL configuration examples
- OAuth vs Auth Key comparison table
- Step-by-step setup instructions for both methods
- Required Tailscale tag configuration

## Validation

The implementation includes:
- Input validation to ensure credentials are provided
- Conditional execution based on authentication method
- Clear error messages for misconfiguration
- Backward compatibility with existing auth key usage
