# Tag Self-Ownership Explained

## Visual Guide to the Tag Permission Issue

### The Problem: Tag Self-Ownership

```
┌─────────────────────────────────────────────────────────────┐
│  Tailscale Default Behavior (No explicit tagOwners)        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  tag:ci ──────┐                                            │
│               │ implicit                                    │
│               │ self-ownership ✅                           │
│               └──> tag:ci                                  │
│                                                             │
│  Result: OAuth client with tag:ci CAN create               │
│          devices with tag:ci ✅                             │
└─────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│  Your Current ACL (Explicit tagOwners - BROKEN)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "tagOwners": {                                            │
│    "tag:ci": ["autogroup:admin", "autogroup:owner"]       │
│  }                                                         │
│                                                             │
│  tag:ci ──────┐                                            │
│               │ NO self-ownership ❌                        │
│               X (lost implicit ownership)                   │
│                                                             │
│  Result: OAuth client with tag:ci CANNOT create            │
│          devices with tag:ci ❌                             │
│  Error: "requested tags [tag:ci] are invalid"              │
└─────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│  Fixed ACL (Explicit Self-Ownership - WORKING)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "tagOwners": {                                            │
│    "tag:ci": ["autogroup:admin", "autogroup:owner",       │
│               "tag:ci"]  ← Added!                          │
│  }                                                         │
│                                                             │
│  tag:ci ──────┐                                            │
│               │ explicit                                    │
│               │ self-ownership ✅                           │
│               └──> tag:ci                                  │
│                                                             │
│  Result: OAuth client with tag:ci CAN create               │
│          devices with tag:ci ✅                             │
└─────────────────────────────────────────────────────────────┘
```

## The Authentication Flow

### OAuth Client with tag:ci

```
┌──────────────────┐
│ GitHub Runner    │
│ (OAuth client)   │
└────────┬─────────┘
         │
         │ 1. tailscale up --advertise-tags=tag:ci
         │    using OAuth token
         ↓
┌─────────────────────────────────────────────┐
│ Tailscale Control Plane                     │
│                                             │
│ Checks: Can OAuth client use tag:ci?       │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ tagOwners ACL:                      │   │
│ │   "tag:ci": [                       │   │
│ │     "autogroup:admin",              │   │
│ │     "autogroup:owner",              │   │
│ │     "tag:ci"  ← Must be present!    │   │
│ │   ]                                 │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ ✅ tag:ci owns tag:ci → APPROVED           │
└─────────────────────────────────────────────┘
         │
         │ 2. Device registered successfully
         ↓
┌──────────────────┐
│ github-runner-   │
│ 18440856972      │
│ Tag: tag:ci ✅   │
└──────────────────┘
```

### Without Self-Ownership (Broken)

```
┌──────────────────┐
│ GitHub Runner    │
│ (OAuth client)   │
└────────┬─────────┘
         │
         │ 1. tailscale up --advertise-tags=tag:ci
         │    using OAuth token
         ↓
┌─────────────────────────────────────────────┐
│ Tailscale Control Plane                     │
│                                             │
│ Checks: Can OAuth client use tag:ci?       │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ tagOwners ACL:                      │   │
│ │   "tag:ci": [                       │   │
│ │     "autogroup:admin",              │   │
│ │     "autogroup:owner"               │   │
│ │     // ❌ tag:ci NOT in list!       │   │
│ │   ]                                 │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ ❌ tag:ci does NOT own tag:ci → DENIED     │
│ Error: "requested tags are invalid"        │
└─────────────────────────────────────────────┘
         │
         │ 2. Registration fails
         ↓
     ❌ FAILED
```

## Why This Happens

### Tailscale's Tag Ownership Rules

1. **Default Behavior (No `tagOwners` defined)**:

   - All tags implicitly own themselves
   - OAuth client with `tag:ci` can create devices with `tag:ci`
   - Simple and works out of the box

2. **With Explicit `tagOwners` (Your case)**:
   - Tags **lose** implicit self-ownership
   - You must explicitly add tags to their own owner list
   - This is by design for security and flexibility

### The Fix is Simple

Add each tag to its own owner list:

```json
"tagOwners": {
  // BEFORE: Missing self-ownership
  "tag:ci": ["autogroup:admin", "autogroup:owner"],

  // AFTER: With self-ownership
  "tag:ci": ["autogroup:admin", "autogroup:owner", "tag:ci"],
  //                                                 ^^^^^^^^
  //                                                 Add this!
}
```

## Complete Working Configuration

```json
{
  "tagOwners": {
    "tag:ci": [
      "autogroup:admin", // Admins can create devices with tag:ci
      "autogroup:owner", // Owners can create devices with tag:ci
      "tag:ci" // OAuth clients WITH tag:ci can create devices with tag:ci
    ],
    "tag:bastion": [
      "autogroup:admin", // Admins can create bastions
      "autogroup:owner", // Owners can create bastions
      "tag:ci", // CI runners can create bastions
      "tag:bastion" // Bastions can create other bastions (self-ownership)
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
      "users": ["root", "ubuntu"]
    }
  ]
}
```

## Reference

- [Tailscale Tags Documentation](https://tailscale.com/kb/1068/tags)
- [OAuth Clients Documentation](https://tailscale.com/kb/1215/oauth-clients)
- [QUICK_FIX.md](./QUICK_FIX.md) - 2-minute fix
- [TAILSCALE_SETUP.md](./docs/TAILSCALE_SETUP.md) - Complete setup guide
