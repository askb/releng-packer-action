# Tailscale Setup for Packer VexxHost Bastion Action

This document provides the required Tailscale configuration for using the Packer VexxHost Bastion Action.

## Prerequisites

1. A Tailscale account (sign up at https://tailscale.com)
2. Admin access to your Tailscale network (tailnet)
3. Ability to modify ACLs in the Tailscale admin console

## Required Configuration

### 1. Tailscale ACL Configuration

The action requires specific Access Control List (ACL) rules in your Tailscale network to allow:

- GitHub Actions runners (`tag:ci`) to connect to the tailnet
- Bastion hosts (`tag:bastion`) to join the network
- SSH connections from runners to bastion hosts

Navigate to your Tailscale admin console at https://login.tailscale.com/admin/acls and configure the following:

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

  "grants": [
    {
      "src": ["*"],
      "dst": ["*"],
      "ip": ["*"]
    }
  ],

  "ssh": [
    {
      "action": "accept",
      "src": ["autogroup:member", "tag:ci"],
      "dst": ["tag:bastion"],
      "users": ["root", "ubuntu", "autogroup:nonroot"]
    }
  ],

  "autoApprovers": {
    "routes": {
      "0.0.0.0/0": ["autogroup:admin"],
      "::/0": ["autogroup:admin"]
    },
    "exitNode": ["autogroup:admin"]
  }
}
```

### Configuration Explanation

#### Tag Owners

```json
"tagOwners": {
    "tag:ci":      ["autogroup:admin", "autogroup:owner"],
    "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"],
}
```

- **`tag:ci`**: Assigned to GitHub Actions runners
  - Owners: Admins and owners can create devices with this tag
- **`tag:bastion`**: Assigned to ephemeral bastion hosts
  - Owners: Admins, owners, and the `tag:ci` tag itself can create bastion hosts
  - Note: `tag:ci` is listed as an owner to allow the workflow to create bastions

#### ACLs (Network Access)

```json
"acls": [
    {
        "action": "accept",
        "src":    ["autogroup:admin", "tag:ci", "tag:bastion"],
        "dst":    ["*:*"],
    },
]
```

- Allows admins, CI runners, and bastion hosts to access all services on all hosts
- Required for bastion to access VexxHost OpenStack network

#### Grants (IP-level Access)

```json
"grants": [
    {
        "src": ["*"],
        "dst": ["*"],
        "ip":  ["*"],
    },
]
```

- Allows all IP-level traffic between nodes
- Simplifies connectivity for the build process

#### SSH Rules (Critical for Action)

```json
"ssh": [
    {
        "action": "accept",
        "src":    ["autogroup:member", "tag:ci"],
        "dst":    ["tag:bastion"],
        "users":  ["root", "ubuntu", "autogroup:nonroot"],
    },
]
```

- **Most Important Rule**: Allows SSH from CI runners to bastion hosts
- `src`: Who can SSH in (members and CI runners)
- `dst`: Where they can SSH to (bastion hosts)
- `users`: Which system users can be accessed

**Without this rule, Packer builds will fail with "tailnet policy does not permit you to SSH to this node"**

#### Auto Approvers (Optional)

```json
"autoApprovers": {
    "routes": {
        "0.0.0.0/0": ["autogroup:admin"],
        "::/0":      ["autogroup:admin"],
    },
    "exitNode": ["autogroup:admin"],
}
```

- Allows admins to approve subnet routes and exit nodes
- Not strictly required for the action, but useful for network management

### 2. Create Tailscale Auth Key

After configuring ACLs, create an auth key for GitHub Actions:

1. Go to https://login.tailscale.com/admin/settings/keys
2. Click **Generate auth key**
3. Configure the key:
   - **Description**: `GitHub Actions CI`
   - **Reusable**: ✅ Yes (allows multiple runners to use it)
   - **Ephemeral**: ✅ Yes (recommended for CI - devices auto-cleanup)
   - **Tags**: Add `tag:ci`
   - **Expiration**: Choose appropriate duration (or never expire for CI)
4. Copy the generated key (starts with `tskey-auth-`)
5. Store it as a GitHub secret named `TAILSCALE_AUTH_KEY`

### 3. Verify Configuration

After applying the ACL configuration, you can test it:

#### Test ACL Syntax

Tailscale will validate your ACL syntax when you save it. Look for:

- ✅ Green checkmark: Configuration is valid
- ❌ Red error: Fix syntax errors before proceeding

#### Test SSH Access

Once a build runs:

1. Check that bastion appears in Tailscale admin console
2. Verify it has `tag:bastion`
3. From your local machine (if you're a member):
   ```bash
   tailscale ssh ubuntu@bastion-gh-XXXXXXX
   ```

## Troubleshooting

### Error: "requested tags [tag:bastion] are invalid or not permitted"

**Cause**: Auth key doesn't have permission to create devices with `tag:bastion`

**Solution**:

1. Check that `tag:bastion` is listed in the auth key's tags
2. Verify `tagOwners` includes `tag:ci` as an owner of `tag:bastion`
3. Create a new auth key with correct tag permissions

### Error: "tailnet policy does not permit you to SSH to this node"

**Cause**: Missing or incorrect SSH rule in ACL

**Solution**:

1. Verify the SSH rule is present in your ACL
2. Ensure `tag:ci` is in the `src` array
3. Ensure `tag:bastion` is in the `dst` array
4. Save the ACL and wait ~30 seconds for it to propagate

### Error: "SSH_AUTH_SOCK is not set"

**Cause**: SSH agent not running (should be handled by action)

**Solution**:

- This should be automatically handled by the action
- If it persists, check the "Setup SSH agent" step in the workflow logs

### Bastion doesn't appear in Tailscale

**Cause**: Bastion failed to join tailnet or cloud-init failed

**Solution**:

1. Check OpenStack console logs:
   ```bash
   openstack console log show bastion-gh-XXXXXX
   ```
2. Look for Tailscale installation errors
3. Verify `TAILSCALE_OAUTH_CLIENT_ID` and `TAILSCALE_OAUTH_SECRET` secrets are set correctly (or `TAILSCALE_AUTH_KEY` for legacy setup)
4. Check network connectivity from VexxHost to Tailscale servers

## Security Considerations

### Principle of Least Privilege

The provided configuration is permissive to simplify setup. For production:

1. **Restrict SSH Users**: Instead of allowing all users, specify only what's needed:

   ```json
   "users": ["ubuntu", "root"]  // Remove autogroup:nonroot if not needed
   ```

2. **Limit Network Access**: Instead of `*:*`, specify only required ports:

   ```json
   "dst": ["tag:bastion:22,443"]  // Only SSH and HTTPS
   ```

3. **Separate Environments**: Use different tag sets for dev/staging/prod:
   ```json
   "tag:ci-dev", "tag:ci-prod", "tag:bastion-dev", "tag:bastion-prod"
   ```

### Auth Key Management

- **Rotate regularly**: Create new auth keys periodically
- **Use ephemeral keys**: Devices auto-cleanup when disconnected
- **Monitor usage**: Check Tailscale admin console for active devices
- **Revoke compromised keys**: Immediately revoke if key is exposed

### Audit Logging

Enable Tailscale audit logging to track:

- Device connections/disconnections
- SSH sessions
- ACL changes
- Auth key usage

## Reference Links

- [Tailscale ACL Documentation](https://tailscale.com/kb/1018/acls)
- [Tailscale SSH Documentation](https://tailscale.com/kb/1193/tailscale-ssh)
- [Tailscale Policy Syntax](https://tailscale.com/kb/1337/policy-syntax)
- [Auth Keys Documentation](https://tailscale.com/kb/1085/auth-keys)

## Example: Adding to Existing ACL

If you already have an ACL configuration, merge the sections:

```json
{
  // Your existing tagOwners
  "tagOwners": {
    "tag:existing": ["autogroup:admin"],
    // Add these:
    "tag:ci": ["autogroup:admin", "autogroup:owner"],
    "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
  },

  // Your existing acls
  "acls": [
    // ... your existing rules ...
    // Add this:
    {
      "action": "accept",
      "src": ["tag:ci", "tag:bastion"],
      "dst": ["*:*"]
    }
  ],

  // Add or merge with existing ssh section
  "ssh": [
    // ... your existing SSH rules ...
    // Add this:
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:bastion"],
      "users": ["root", "ubuntu", "autogroup:nonroot"]
    }
  ]
}
```

## Support

If you encounter issues:

1. Check Tailscale admin console for device status
2. Review workflow logs for error messages
3. Verify ACL syntax in Tailscale admin console
4. File an issue in this repository with logs
