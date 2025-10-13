# QUICK FIX - Tailscale Tag Self-Ownership

## The Problem
```
Error: "requested tags [tag:ci] are invalid or not permitted"
```

## The Solution (2 minutes)

### 1. Go to Tailscale ACL
https://login.tailscale.com/admin/acls

### 2. Find `tagOwners` section and update it:

**Change FROM:**
```json
"tagOwners": {
  "tag:ci": ["autogroup:admin", "autogroup:owner"],
  "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci"]
}
```

**Change TO:**
```json
"tagOwners": {
  "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
  "tag:bastion": ["autogroup:admin", "autogroup:owner", "tag:ci", "tag:bastion"]
}
```

### 3. Save and wait 30 seconds

### 4. Re-run workflow
```bash
gh workflow run packer-vexxhost-bastion-build.yaml
```

## Why?
Tags lose implicit self-ownership when you define explicit owners. Adding the tag to its own owner list restores the ability for OAuth clients with that tag to create devices with the same tag.

**Reference**: [Tailscale Tags Documentation - Implicit Self-Ownership](https://tailscale.com/kb/1068/tags)
