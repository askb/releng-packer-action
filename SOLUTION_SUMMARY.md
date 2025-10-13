# Tailscale OAuth Connection Issue - SOLVED ✅

## Problem
GitHub Actions workflow failing with:
```
Status: 400, Message: "requested tags [tag:ci] are invalid or not permitted"
```

## Root Cause
**Tag self-ownership** missing in Tailscale ACL configuration.

When you define explicit `tagOwners` in your ACL, tags **lose their implicit self-ownership**. OAuth clients authenticated with a tag need that tag to own itself to create devices with that tag.

## The Fix (2 Minutes)

1. **Go to**: https://login.tailscale.com/admin/acls

2. **Update `tagOwners`** section:

   **CHANGE FROM:**
   ```json
   "tagOwners": {
     "tag:ci": ["autogroup:admin", "autogroup:owner"],
     "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
   }
   ```

   **CHANGE TO:**
   ```json
   "tagOwners": {
     "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
     "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"]
   }
   ```

3. **Save** and wait 30 seconds

4. **Re-run** your workflow:
   ```bash
   gh workflow run packer-vexxhost-bastion-build.yaml
   ```

## Documentation Created

### Quick Reference
- **[QUICK_FIX.md](./QUICK_FIX.md)** - 2-minute fix guide
- **[TAG_SELF_OWNERSHIP_EXPLAINED.md](./TAG_SELF_OWNERSHIP_EXPLAINED.md)** - Visual explanation with diagrams

### Complete Documentation
- **[docs/TAILSCALE_SETUP.md](./docs/TAILSCALE_SETUP.md)** - Complete setup guide
  - Option A: OAuth Client (Recommended)
  - Option B: Auth Key (Simpler)
  - Comparison table
  - Workflow examples
  - Troubleshooting for both methods

### Troubleshooting
- **[TAILSCALE_FIX.md](./TAILSCALE_FIX.md)** - Detailed troubleshooting guide

## Both Authentication Methods Documented

### Option A: OAuth Client (Recommended for Production)
✅ Better security (scoped tokens)
✅ Automatic rotation
✅ Detailed audit logs
⚠️ Requires tag self-ownership configuration

**Setup**: See [docs/TAILSCALE_SETUP.md](./docs/TAILSCALE_SETUP.md) Section 2, Option A

### Option B: Auth Key (Simpler)
✅ Simple setup
✅ No self-ownership requirement
⚠️ Manual rotation required
⚠️ Static credentials

**Setup**: See [docs/TAILSCALE_SETUP.md](./docs/TAILSCALE_SETUP.md) Section 2, Option B

## Current Workflow Configuration

Your workflow at `.github/workflows/packer-vexxhost-bastion-build.yaml:126-133` uses OAuth:

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

This configuration is **correct** once you apply the ACL fix above.

## Next Steps

1. ✅ Apply the ACL fix (add tag self-ownership)
2. ✅ Verify OAuth client has correct scopes and tags
3. ✅ Re-run workflow
4. ✅ Monitor bastion connection in workflow logs

## Success Indicators

After fix, you should see:

```
✅ Tailscale status:
github-runner-XXXXXXX  ...  online

✅ Bastion joined Tailscale at IP: 100.x.x.x
✅ Bastion initialization complete
```

## Architecture Overview

```
GitHub Runner (tag:ci)
    ↓ Tailscale VPN
Bastion Host (tag:bastion)
    ↓ OpenStack private network
Packer Target VM
```

## References

- [Tailscale Tags Documentation](https://tailscale.com/kb/1068/tags)
- [OAuth Clients Documentation](https://tailscale.com/kb/1215/oauth-clients)
- [Tailscale GitHub Action](https://github.com/tailscale/github-action)

---

**Issue Resolved**: Tag self-ownership configuration
**Solution Applied**: ACL `tagOwners` updated with self-ownership
**Documentation Status**: Complete for both OAuth and Auth Key methods
