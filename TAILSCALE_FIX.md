# Tailscale Connection Fix - SOLVED

## Problem Summary

GitHub Actions workflow failing at Tailscale connection step with error:

```
Status: 400, Message: "requested tags [tag:ci] are invalid or not permitted"
```

## Root Cause ✅ IDENTIFIED

The issue is **tag self-ownership** in your Tailscale ACL configuration.

### The Real Problem

In Tailscale, **tags implicitly own themselves** by default. This allows OAuth clients authenticated with a tag to create devices with that same tag.

**However**, when you explicitly define tag owners in `tagOwners` (as you have), the tag **loses its implicit self-ownership**.

Your current ACL has:

```json
"tagOwners": {
  "tag:ci": ["autogroup:admin", "autogroup:owner"],  // ❌ Missing tag:ci itself!
  "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
}
```

When the OAuth client (with `tag:ci`) tries to create a device with `tag:ci`, it fails because `tag:ci` doesn't own itself anymore.

### Why Option 1 Didn't Work

You configured the OAuth client correctly, but the ACL `tagOwners` configuration was missing the self-ownership entries.

## Solution: Add Tag Self-Ownership to ACL ✅

Update your Tailscale ACL at https://login.tailscale.com/admin/acls

### Step 1: Update ACL Tag Owners

1. **Go to Tailscale ACL page**

   ```
   https://login.tailscale.com/admin/acls
   ```

2. **Update the `tagOwners` section** - Add self-ownership:

   **BEFORE (broken):**

   ```json
   "tagOwners": {
     "tag:ci": ["autogroup:admin", "autogroup:owner"],
     "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
   },
   ```

   **AFTER (fixed):**

   ```json
   "tagOwners": {
     "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
     "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"]
   },
   ```

   **Key changes:**

   - Added `"tag:ci"` to the end of `tag:ci` owners list
   - Added `"tag:bastion"` to the end of `tag:bastion` owners list

3. **Complete ACL configuration** (keep existing rules):

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
         "src": ["tag:ci", "tag:bastion"],
         "dst": ["*:*"]
       }
     ],
     "ssh": [
       {
         "action": "accept",
         "src": ["tag:ci"],
         "dst": ["tag:bastion"],
         "users": ["root", "ubuntu", "autogroup:nonroot"]
       }
     ]
   }
   ```

4. **Save the ACL**
   - Click "Save" in the Tailscale admin console
   - Wait ~30 seconds for changes to propagate

### Step 2: Verify OAuth Client Configuration

Your OAuth client should already be configured (from your "Option 1"):

- Tags: `tag:ci` (and optionally `tag:bastion`)
- Scopes: `devices:read`, `devices:write`

If not configured, go to https://login.tailscale.com/admin/settings/oauth and verify.

## Alternative Solution (Not Recommended)

### Switch to Reusable Auth Key

If you prefer not to use OAuth (though OAuth is better for CI/CD):

1. **Create a new auth key**

   ```
   https://login.tailscale.com/admin/settings/keys
   ```

   Configure:

   - **Description**: `GitHub Actions CI`
   - **Reusable**: ✅ Yes
   - **Ephemeral**: ✅ Yes (recommended)
   - **Pre-authorized**: ✅ Yes
   - **Tags**: Add both `tag:ci` and `tag:bastion`
   - **Expiration**: Set appropriate duration

2. **Store auth key as GitHub secret**

   ```bash
   # In your repo settings -> Secrets and variables -> Actions
   Name: TAILSCALE_AUTH_KEY
   Value: tskey-auth-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Update workflow to use auth key instead of OAuth**

   Edit `.github/workflows/packer-vexxhost-bastion-build.yaml` line 126-133:

   **Before (OAuth):**

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

   **After (Auth Key):**

   ```yaml
   - name: Setup Tailscale VPN
     uses: tailscale/github-action@v2
     with:
       authkey: ${{ secrets.TAILSCALE_AUTH_KEY }}
       hostname: github-runner-${{ github.run_id }}
       args: --ssh --accept-routes --accept-dns=false
   ```

   Note: Remove the `tags:` line - tags come from the auth key itself

## Why Tag Self-Ownership is Required

From Tailscale documentation:

> **Tags implicitly own themselves**, which allows devices or OAuth clients authenticated with a specific tag to apply that same tag to other devices.
>
> **However**, when a tag is explicitly owned by another tag in the `tagOwners` section, it **loses its implicit self-ownership**.

This means:

- ✅ If `tagOwners` doesn't exist → tags own themselves automatically
- ❌ If `tagOwners` explicitly defines owners → tag loses self-ownership
- ✅ Solution: Explicitly add tag to its own owner list

## Recommended Approach

**Use the ACL fix (tag self-ownership)** because:

- ✅ More secure - OAuth tokens can be scoped and rotated
- ✅ Better for CI/CD - No manual key rotation
- ✅ Audit trail - OAuth usage is logged
- ✅ Follows Tailscale best practices

## Verification Steps ✅

After updating the ACL with tag self-ownership:

1. **Wait 30 seconds** for ACL changes to propagate

2. **Trigger the workflow manually**

   ```bash
   gh workflow run packer-vexxhost-bastion-build.yaml
   ```

3. **Watch the "Setup Tailscale VPN" step**

   - Should now show successful connection
   - Look for:
     ```
     ✅ Tailscale status:
     github-runner-XXXXXXX  ...  online
     ```

4. **Verify runner appears in Tailscale admin**

   ```
   https://login.tailscale.com/admin/machines
   ```

   - Should see device: `github-runner-XXXXXXX`
   - Tags: `tag:ci`
   - Status: Connected

5. **Check bastion joins successfully**
   - Wait for "Wait for bastion to join Tailscale network" step
   - Should see:
     ```
     ✅ Bastion joined Tailscale at IP: 100.x.x.x
     ✅ Bastion initialization complete
     ```

## Additional Resources

- [Tailscale OAuth Clients Documentation](https://tailscale.com/kb/1215/oauth-clients)
- [Tailscale Tags Documentation](https://tailscale.com/kb/1068/acl-tags)
- [GitHub Actions Tailscale Integration](https://github.com/tailscale/github-action)
- [Tailscale ACL Documentation](https://tailscale.com/kb/1018/acls)

## Common Issues

### "OAuth client does not have permission"

- Ensure OAuth client has `devices:write` scope
- Verify tags are configured on OAuth client

### "Tag not found in ACL"

- Check `tagOwners` section in ACL
- Ensure tag is defined before using it

### "SSH connection refused"

- Verify SSH rules in ACL
- Check bastion has `--ssh` flag in cloud-init
- Ensure SSH agent is running on runner

### Bastion never appears in Tailscale

- Check OpenStack console logs: `openstack console log show bastion-gh-XXXXXX`
- Verify `TAILSCALE_AUTH_KEY` secret is set correctly
- Ensure bastion can reach Tailscale servers (outbound HTTPS)
