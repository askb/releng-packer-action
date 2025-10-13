# Gerrit-to-GitHub Trigger Mechanism Summary

## How It Works

The `gerrit-to-platform` system automatically discovers and triggers GitHub workflows when Gerrit events occur. The mechanism is **filename-based** - no special configuration needed in the workflows themselves beyond the standard structure.

## Key Points

### 1. Automatic Discovery
- When a Gerrit event occurs (patchset created, change merged, etc.), `gerrit-to-platform` queries the GitHub API for all active workflows in the target repository
- It filters these workflows based on filename patterns
- Matching workflows are automatically dispatched with Gerrit event data as inputs

### 2. Filename Convention (CRITICAL)
Workflows are discovered by their filenames. A workflow will be triggered if its filename contains:

**For Verify Events (patchset-created, comment-added):**
- Must contain: `gerrit` (case-insensitive)
- Must contain: `verify` (case-insensitive)
- Must NOT contain: `required` (unless in `.github` magic repo)

**For Merge Events (change-merged):**
- Must contain: `gerrit` (case-insensitive)
- Must contain: `merge` (case-insensitive)
- Must NOT contain: `required` (unless in `.github` magic repo)

**Examples:**
- ✅ `gerrit-packer-verify.yaml` - Will be triggered on verify events
- ✅ `gerrit-packer-merge.yaml` - Will be triggered on merge events
- ✅ `gerrit-verify-build.yaml` - Will be triggered on verify events
- ✅ `my-gerrit-merge-job.yaml` - Will be triggered on merge events
- ❌ `packer-verify.yaml` - Missing "gerrit", won't be triggered
- ❌ `gerrit-build.yaml` - Missing event type, won't be triggered

### 3. Workflow Structure Requirements

All Gerrit-triggered workflows must:

a) Use `workflow_dispatch` trigger with Gerrit inputs:
```yaml
on:
  workflow_dispatch:
    inputs:
      GERRIT_BRANCH:
        required: true
        type: string
      GERRIT_CHANGE_ID:
        required: true
        type: string
      GERRIT_CHANGE_NUMBER:
        required: true
        type: string
      GERRIT_CHANGE_URL:
        required: true
        type: string
      GERRIT_EVENT_TYPE:
        required: true
        type: string
      GERRIT_PATCHSET_NUMBER:
        required: true
        type: string
      GERRIT_PATCHSET_REVISION:
        required: true
        type: string
      GERRIT_PROJECT:
        required: true
        type: string
      GERRIT_REFSPEC:
        required: true
        type: string
```

b) Fetch the Gerrit refspec to work with the actual change:
```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    ref: ${{ inputs.GERRIT_BRANCH }}
    fetch-depth: 0

- name: Fetch Gerrit patchset
  run: |
    git fetch origin ${{ inputs.GERRIT_REFSPEC }}
    git checkout FETCH_HEAD
```

### 4. Two Deployment Modes

**Mode A: Repository-Specific Workflows** (What you're using)
- Workflow files live in `.github/workflows/` of the Gerrit-mirrored repo
- Triggered only for events in that specific repository
- Most common use case
- Examples:
  - `builder` repo has its own `gerrit-packer-verify.yaml`
  - `ci-management` repo has its own `gerrit-packer-verify.yaml`

**Mode B: Organization-Wide Required Workflows** (Not applicable here)
- Workflow files live in `.github/workflows/` of the `.github` repository
- Must contain "required" in filename
- Triggered for events across ALL repositories in the organization
- Receive additional `TARGET_REPO` input

### 5. The Filter Process

When a patchset is created in Gerrit:

1. Gerrit hook fires → `gerrit-to-platform` receives event
2. System looks up repository mapping (Gerrit project → GitHub repo)
3. Queries GitHub API: "Give me all active workflows in `owner/repo`"
4. Filters the list:
   - Keep workflows with "gerrit" in filename ✓
   - Keep workflows with "verify" in filename ✓
   - Remove workflows with "required" in filename ✗
5. For each matching workflow:
   - Call GitHub API: `dispatch_workflow(owner, repo, workflow_id, ref, inputs)`
6. GitHub Actions starts the workflow with provided inputs

## Why This Approach?

**Advantages:**
- No hardcoded workflow names in `gerrit-to-platform`
- Repositories can add new Gerrit-triggered workflows just by naming them correctly
- Self-documenting: filename tells you it's Gerrit-triggered
- Flexible: can have multiple verify/merge workflows (e.g., `gerrit-packer-verify.yaml`, `gerrit-docker-verify.yaml`)

**Disadvantages:**
- Filename convention must be followed strictly
- Not immediately obvious to developers unfamiliar with the system

## Your Current Setup

**Repository:** `askb/releng-packer-action` (and will be copied to `lfit/releng-packer-action`)

**Example Workflows Provided:**
1. `examples/workflows/gerrit-packer-verify.yaml` - For Gerrit verify events
2. `examples/workflows/gerrit-packer-merge.yaml` - For Gerrit merge events

**How Consumers Use It:**

A consumer repository (e.g., `lfit/releng-builder`) will:
1. Copy example workflows to their `.github/workflows/` directory
2. Customize inputs, secrets, matrix, etc. as needed
3. When Gerrit events occur, `gerrit-to-platform` automatically discovers and triggers them
4. The workflows use your `releng-packer-action` via:
   ```yaml
   uses: lfit/releng-packer-action@main
   ```

## Common Pitfall

**TARGET_REPO Confusion:**
- `TARGET_REPO` is ONLY for organization-wide required workflows in the `.github` repo
- Regular repository-specific workflows do NOT need `TARGET_REPO`
- When `gerrit-packer-verify.yaml` is in `lfit/releng-builder/.github/workflows/`, it automatically runs against `lfit/releng-builder`
- The workflow already knows its own repository via `${{ github.repository }}`

## Testing Your Workflows

Since the example workflows use `workflow_dispatch`, they can be manually triggered:

```bash
gh workflow run gerrit-packer-verify.yaml \
  -f GERRIT_BRANCH=main \
  -f GERRIT_CHANGE_ID=I1234567890abcdef \
  -f GERRIT_CHANGE_NUMBER=12345 \
  -f GERRIT_CHANGE_URL=https://gerrit.linuxfoundation.org/infra/c/releng/builder/+/12345 \
  -f GERRIT_EVENT_TYPE=patchset-created \
  -f GERRIT_PATCHSET_NUMBER=1 \
  -f GERRIT_PATCHSET_REVISION=abc123 \
  -f GERRIT_PROJECT=releng/builder \
  -f GERRIT_REFSPEC=refs/changes/45/12345/1
```

This allows testing without actually pushing to Gerrit.

## References

See `docs/GERRIT_GITHUB_INTEGRATION.md` for full documentation.

Key source files in `gerrit-to-platform`:
- `src/gerrit_to_platform/github.py::filter_workflows()` - The filename filtering logic
- `src/gerrit_to_platform/helpers.py::find_and_dispatch()` - The discovery and dispatch loop
- `src/gerrit_to_platform/patchset_created.py` - Verify event handler
- `src/gerrit_to_platform/change_merged.py` - Merge event handler
