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
    "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
    "tag:bastion": [
      "autogroup:admin",
      "autogroup:owner",
      "tag:ci",
      "tag:bastion"
    ]
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
    "tag:ci":      ["autogroup:admin", "autogroup:owner", "tag:ci"],
    "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"],
}
```

- **`tag:ci`**: Assigned to GitHub Actions runners
  - Owners: Admins, owners, and **`tag:ci` itself** (self-ownership required for OAuth)
  - **Important**: `tag:ci` must own itself to allow OAuth clients with this tag to create devices
- **`tag:bastion`**: Assigned to ephemeral bastion hosts
  - Owners: Admins, owners, `tag:ci`, and **`tag:bastion` itself** (self-ownership)
  - This allows both CI runners and bastion hosts to create other bastion instances
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

### 2. Authentication Setup

You have two options for authenticating GitHub Actions with Tailscale: **OAuth clients** (recommended) or **auth keys**. Both methods are supported.

#### Comparison Table

| Feature              | OAuth Client (Recommended)                    | Auth Key                                      |
| -------------------- | --------------------------------------------- | --------------------------------------------- |
| **Security**         | ✅ Better - scoped tokens, automatic rotation | ⚠️ Good - static keys require manual rotation |
| **Audit Trail**      | ✅ Detailed OAuth audit logs                  | ⚠️ Basic key usage logs                       |
| **Key Rotation**     | ✅ Automatic (tokens expire quickly)          | ❌ Manual rotation required                   |
| **Setup Complexity** | Medium - requires tag self-ownership config   | Easy - straightforward key generation         |
| **Best For**         | Production CI/CD pipelines                    | Quick testing, simple setups                  |
| **Expiration**       | Short-lived tokens (hours)                    | Can be set to never expire                    |
| **Compromise Risk**  | ✅ Lower - tokens auto-expire                 | ⚠️ Higher - long-lived credentials            |

---

#### Option A: OAuth Client (Recommended for Production)

OAuth clients provide better security and are recommended for production CI/CD environments.

##### Step 1: Create OAuth Client

1. Go to **Tailscale OAuth clients page**:

   ```
   https://login.tailscale.com/admin/settings/oauth
   ```

2. Click **Generate OAuth client**

3. Configure the OAuth client:

   - **Description**: `GitHub Actions CI`
   - **Tags**: Select `tag:ci` (and optionally `tag:bastion`)
   - **Scopes**: Select the following:
     - ✅ `devices:read` - Required to list devices
     - ✅ `devices:write` - Required to register new devices
     - ⚠️ `all` - Alternative to individual scopes (less secure, not recommended)

4. Click **Generate client**

5. **Save the credentials** (you won't be able to see them again):
   - **OAuth Client ID**: Starts with `kDN...` or similar
   - **OAuth Client Secret**: Long secret string

##### Step 2: Store OAuth Credentials as GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add two secrets:

   | Secret Name                 | Secret Value             | Example                      |
   | --------------------------- | ------------------------ | ---------------------------- |
   | `TAILSCALE_OAUTH_CLIENT_ID` | Your OAuth client ID     | `kDNxxxxxxxxxxxxxxxxxxxxxxx` |
   | `TAILSCALE_OAUTH_SECRET`    | Your OAuth client secret | `tskey-client-xxxxxxxxxxxxx` |

##### Step 3: Workflow Configuration for OAuth

Use this configuration in your workflow (`.github/workflows/packer-vexxhost-bastion-build.yaml`):

```yaml
- name: Setup Tailscale VPN
  uses: tailscale/github-action@v2
  with:
    oauth-client-id: ${{ secrets.TAILSCALE_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TAILSCALE_OAUTH_SECRET }}
    tags: tag:ci
    hostname: github-runner-${{ github.run_id }}
    args: --ssh --accept-routes --accept-dns=false
```

##### Important: Tag Self-Ownership Requirement

**Critical**: When using OAuth clients with tags, you **must** ensure tags own themselves in the ACL `tagOwners` section:

```json
"tagOwners": {
  "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],  // ← tag:ci must own itself!
  "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"]
}
```

**Why?** Tags implicitly own themselves by default. However, when you explicitly define owners in `tagOwners`, tags **lose their implicit self-ownership**. OAuth clients authenticated with a tag need that tag to own itself to create devices.

**Common Error Without Self-Ownership:**

```
Status: 400, Message: "requested tags [tag:ci] are invalid or not permitted"
```

---

#### Option B: Auth Key (Simpler Alternative)

Auth keys are simpler to set up but require manual rotation and provide less security.

##### Step 1: Create Auth Key

1. Go to **Tailscale auth keys page**:

   ```
   https://login.tailscale.com/admin/settings/keys
   ```

2. Click **Generate auth key**

3. Configure the key:

   - **Description**: `GitHub Actions CI & Bastion`
   - **Reusable**: ✅ Yes (allows multiple runners to use it)
   - **Ephemeral**: ✅ Yes (recommended for CI - devices auto-cleanup)
   - **Pre-authorized**: ✅ Yes (automatically approves new devices)
   - **Tags**: Select both:
     - ✅ `tag:ci`
     - ✅ `tag:bastion`
   - **Expiration**: Choose appropriate duration:
     - 90 days (recommended for production)
     - 1 year (for long-term testing)
     - Never (not recommended - rotation required)

4. Click **Generate key**

5. **Copy the auth key** (starts with `tskey-auth-`)

##### Step 2: Store Auth Key as GitHub Secret

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add one secret:

   | Secret Name          | Secret Value  | Example                                    |
   | -------------------- | ------------- | ------------------------------------------ |
   | `TAILSCALE_AUTH_KEY` | Your auth key | `tskey-auth-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

##### Step 3: Workflow Configuration for Auth Key

**For GitHub Runner (Option B1 - using auth key in workflow):**

```yaml
- name: Setup Tailscale VPN
  uses: tailscale/github-action@v2
  with:
    authkey: ${{ secrets.TAILSCALE_AUTH_KEY }}
    hostname: github-runner-${{ github.run_id }}
    args: --ssh --accept-routes --accept-dns=false
```

**Note**: Do NOT include `tags:` parameter - tags come from the auth key itself.

**For Bastion Host (cloud-init, already configured):**

The bastion host uses the same `TAILSCALE_AUTH_KEY` in the cloud-init script:

```yaml
tailscale up \
--authkey="${TAILSCALE_AUTH_KEY}" \
--hostname="${BASTION_HOSTNAME}" \
--advertise-tags=tag:bastion \
--ssh
```

---

#### Which Method Should I Use?

**Use OAuth Client (Option A) if:**

- ✅ You're running production CI/CD pipelines
- ✅ You need detailed audit trails
- ✅ You want automatic credential rotation
- ✅ You have time to configure tag self-ownership

**Use Auth Key (Option B) if:**

- ✅ You're testing or prototyping
- ✅ You want the simplest setup
- ✅ You're okay with manual key rotation
- ✅ You need long-lived credentials

**Recommendation**: Start with **Auth Key for testing**, then migrate to **OAuth Client for production**.

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

### Error: "requested tags [tag:ci] are invalid or not permitted"

**Affects**: OAuth clients (Option A)

**Cause**: Tag self-ownership is not configured in ACL `tagOwners`

**Solution**:

1. Go to https://login.tailscale.com/admin/acls
2. Update `tagOwners` to include self-ownership:
   ```json
   "tagOwners": {
     "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
     "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"]
   }
   ```
3. Save ACL and wait 30 seconds for propagation
4. Re-run workflow

**Why this happens**: When you explicitly define tag owners, tags lose their implicit self-ownership. OAuth clients need tags to own themselves.

**Reference**: See [QUICK_FIX.md](../QUICK_FIX.md) for detailed explanation.

---

### Error: "requested tags [tag:bastion] are invalid or not permitted"

**Affects**: Auth keys (Option B)

**Cause**: Auth key doesn't have permission to create devices with `tag:bastion`

**Solution**:

1. Check that `tag:bastion` is listed in the auth key's tags when you created it
2. Verify `tagOwners` in ACL includes both:
   - `tag:ci` as an owner of `tag:bastion`
   - `tag:bastion` as an owner of itself (self-ownership)
3. If auth key is missing tags, create a new auth key with correct permissions:
   - Go to https://login.tailscale.com/admin/settings/keys
   - Create new key with both `tag:ci` AND `tag:bastion` selected
   - Update `TAILSCALE_AUTH_KEY` secret in GitHub

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

1. **Check OpenStack console logs**:

   ```bash
   openstack console log show bastion-gh-XXXXXX
   ```

   Look for Tailscale installation or connection errors

2. **Verify authentication secrets** (depending on your auth method):

   **If using OAuth (Option A)**:

   - Verify `TAILSCALE_OAUTH_CLIENT_ID` secret exists
   - Verify `TAILSCALE_OAUTH_SECRET` secret exists
   - Check OAuth client has `devices:write` scope
   - Ensure OAuth client has `tag:bastion` assigned

   **If using auth key (Option B)**:

   - Verify `TAILSCALE_AUTH_KEY` secret exists in GitHub
   - Ensure auth key has both `tag:ci` AND `tag:bastion` tags
   - Check auth key hasn't expired
   - Verify auth key is marked as "Reusable"

3. **Check network connectivity**:

   - Ensure bastion can reach Tailscale coordination servers (outbound HTTPS)
   - VexxHost network should allow outbound connections to `*.tailscale.com`

4. **Review cloud-init logs on bastion** (if accessible):
   ```bash
   # SSH to bastion if reachable via OpenStack network
   cat /var/log/cloud-init-output.log
   cat /var/log/bastion-init.log
   ```

### Error: "OAuth client does not have permission"

**Affects**: OAuth clients (Option A)

**Cause**: OAuth client missing required scopes or tag permissions

**Solution**:

1. Go to https://login.tailscale.com/admin/settings/oauth
2. Find your OAuth client
3. Verify it has:
   - **Scopes**: `devices:read`, `devices:write`
   - **Tags**: `tag:ci` (and optionally `tag:bastion`)
4. If missing permissions, you may need to:
   - Delete the old OAuth client
   - Create a new one with correct permissions
   - Update GitHub secrets with new credentials

### Error: Auth key has expired

**Affects**: Auth keys (Option B)

**Cause**: Auth key reached its expiration date

**Solution**:

1. Go to https://login.tailscale.com/admin/settings/keys
2. Create a new auth key (see Option B setup instructions)
3. Update `TAILSCALE_AUTH_KEY` secret in GitHub repository
4. Re-run the workflow

### Switching Between Auth Methods

**From Auth Key → OAuth Client**:

1. Follow "Option A: OAuth Client" setup instructions
2. Create OAuth client and store credentials in GitHub secrets
3. Update workflow to use `oauth-client-id` and `oauth-secret` parameters
4. **Important**: Add tag self-ownership to ACL `tagOwners`
5. You can keep the auth key for bastion or switch that to OAuth too

**From OAuth Client → Auth Key**:

1. Follow "Option B: Auth Key" setup instructions
2. Create auth key and store in GitHub secrets
3. Update workflow to use `authkey` parameter (remove `tags:` line)
4. Auth key method doesn't require tag self-ownership (but it doesn't hurt to keep it)

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

### Authentication Management

#### OAuth Client Best Practices (Option A)

- **Scope properly**: Only grant necessary scopes (`devices:read`, `devices:write`)
- **Monitor usage**: Check Tailscale admin console for OAuth client activity
- **Rotate secrets**: If compromised, regenerate OAuth client and update GitHub secrets
- **Tag ownership**: Always ensure tags have self-ownership in ACL
- **Audit logs**: Review OAuth client usage in Tailscale admin console regularly

#### Auth Key Best Practices (Option B)

- **Rotate regularly**: Create new auth keys every 90 days
- **Use ephemeral keys**: Enable ephemeral option for automatic device cleanup
- **Pre-authorize**: Enable pre-authorization to avoid manual approval
- **Set expiration**: Don't use "never expire" - set reasonable expiration dates
- **Monitor usage**: Check Tailscale admin console for active devices
- **Revoke compromised keys**: Immediately revoke and rotate if key is exposed
- **Tag assignment**: Always include both `tag:ci` and `tag:bastion` tags

### Audit Logging

Enable Tailscale audit logging to track:

- Device connections/disconnections
- SSH sessions
- ACL changes
- Auth key usage

## Reference Links

### General Documentation

- [Tailscale ACL Documentation](https://tailscale.com/kb/1018/acls)
- [Tailscale SSH Documentation](https://tailscale.com/kb/1193/tailscale-ssh)
- [Tailscale Policy Syntax](https://tailscale.com/kb/1337/policy-syntax)
- [Tailscale Tags Documentation](https://tailscale.com/kb/1068/tags)

### Authentication Methods

- [OAuth Clients Documentation](https://tailscale.com/kb/1215/oauth-clients)
- [Auth Keys Documentation](https://tailscale.com/kb/1085/auth-keys)
- [Tailscale GitHub Action](https://github.com/tailscale/github-action)

### Troubleshooting Resources

- [QUICK_FIX.md](../QUICK_FIX.md) - Fast fix for OAuth tag permission issues
- [TAILSCALE_FIX.md](../TAILSCALE_FIX.md) - Detailed troubleshooting guide

## Example: Adding to Existing ACL

If you already have an ACL configuration, merge the sections. **Important**: Include self-ownership for tags!

```json
{
  // Your existing tagOwners
  "tagOwners": {
    "tag:existing": ["autogroup:admin"],
    // Add these (note self-ownership):
    "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
    "tag:bastion": [
      "autogroup:admin",
      "autogroup:owner",
      "tag:ci",
      "tag:bastion"
    ]
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
