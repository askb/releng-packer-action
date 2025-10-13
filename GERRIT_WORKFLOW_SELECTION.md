# Gerrit-to-GitHub Workflow Selection Mechanism

## Overview
The `gerrit_to_platform` system automatically discovers and triggers GitHub workflows when Gerrit events occur. Here's how it selects which workflows to run:

## Workflow Filename Requirements

### Basic Rules (ALL workflows must follow):
1. **Must contain "gerrit"** in the filename (case-insensitive)
2. **Must contain the event filter** in the filename:
   - `verify` - for patchset-created events
   - `merge` - for change-merged events
   - Custom keyword - for comment-added events (configured in gerrit_to_platform.ini)

### Example Filenames:
- ✅ `gerrit-packer-verify.yaml` - Contains "gerrit" + "verify"
- ✅ `gerrit-verify.yaml` - Contains "gerrit" + "verify"
- ✅ `gerrit-sonar-novote-verify.yaml` - Contains "gerrit" + "verify"
- ✅ `gerrit-packer-merge.yaml` - Contains "gerrit" + "merge"
- ❌ `packer-verify.yaml` - Missing "gerrit"
- ❌ `gerrit-build.yaml` - Missing event filter (verify/merge)

## How gerrit_to_platform Finds Workflows

### Step 1: Event Mapping
When a Gerrit event occurs:
- **patchset-created** → searches for workflows with "verify"
- **change-merged** → searches for workflows with "merge"
- **comment-added** (e.g., "recheck") → uses mapping from config file

### Step 2: Workflow Discovery
The system searches for workflows in TWO locations:

1. **Project-specific workflows** (in the GitHub mirror repo):
   - Path: `.github/workflows/`
   - Filters: filename contains "gerrit" + event filter (e.g., "verify")
   - Excludes: workflows with "required" in filename
   - Example: `.github/workflows/gerrit-packer-verify.yaml`

2. **Organization-wide required workflows** (in ORG/.github repo):
   - Path: `.github/workflows/` in the magic `.github` repository
   - Filters: filename contains "gerrit" + event filter + "required"
   - Example: `.github/workflows/gerrit-required-verify.yaml`

### Step 3: Filtering Logic (from github.py)
```python
# All workflows must contain the event filter (e.g., "verify")
filtered = filter(contains_search_filter, workflows)

# All workflows must contain "gerrit"
filtered = filter(contains_gerrit, filtered)

# For project repos: exclude "required" workflows
# For .github repo: include only "required" workflows
if search_required:
    filtered = filter(contains_required, filtered)
else:
    filtered = filter(NOT contains_required, filtered)
```

## Multiple Workflows with Same Event Type

**The system triggers ALL matching workflows!**

If you have:
- `gerrit-packer-verify.yaml`
- `gerrit-ci-management-verify.yaml`
- `gerrit-shellcheck-verify.yaml`

On a patchset-created event, **ALL THREE** will be triggered.

## Why Your Filenames Work

Your examples follow the pattern correctly:
- ✅ `gerrit-packer-verify.yaml` → Triggered on patchset-created
- ✅ `gerrit-packer-merge.yaml` → Triggered on change-merged

Both contain "gerrit" + the appropriate event filter.

## Required Workflows (Organization-wide)

If you want workflows that run for ALL projects in the organization:
1. Place them in the `ORG/.github` repository
2. Filename must contain: "gerrit" + event filter + "required"
3. Example: `gerrit-required-verify.yaml`
4. Must include `TARGET_REPO` input parameter

## Summary

The gerrit_to_platform system:
1. Watches for Gerrit events (patchset-created, change-merged, comment-added)
2. Maps events to search filters (verify, merge, or custom)
3. Searches `.github/workflows/` for files matching:
   - Contains "gerrit" (case-insensitive)
   - Contains the event filter (case-insensitive)
   - Does NOT contain "required" (for project workflows)
4. Triggers ALL matching workflows with Gerrit event data as inputs

**Key Insight**: The `<description>` part in `gerrit-<event-type>-<description>.yaml` is just for your organization - the system only cares about the presence of "gerrit" and the event type keyword.

Signed-off-by: Anil Belur <askb23@gmail.com>
