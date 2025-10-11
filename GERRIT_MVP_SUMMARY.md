# Gerrit Integration MVP - Implementation Summary

## ✅ What Was Implemented

The action now supports **two modes** for Gerrit-based workflows:

### 1. Validate Mode (Pre-Merge)

- **Purpose**: Syntax validation before merge
- **When**: Triggered on Gerrit patchset-created
- **Infrastructure**: Runs on GitHub runner only (no bastion)
- **Speed**: ~30 seconds
- **Cost**: Minimal
- **Secrets needed**: None (just GERRIT_SSH_PRIVKEY for voting)

### 2. Build Mode (Post-Merge/Scheduled)

- **Purpose**: Build actual images
- **When**: After merge or scheduled
- **Infrastructure**: Creates Tailscale bastion + builds image
- **Speed**: ~5-15 minutes
- **Cost**: Moderate (bastion + build VM)
- **Secrets needed**: All VexxHost + Tailscale secrets

## 📁 Files Created/Modified

### Modified

- **action.yaml** - Added mode parameter, conditional steps

### Created

- **examples/workflows/gerrit-packer-verify.yaml** - Validation workflow
- **examples/workflows/gerrit-packer-merge.yaml** - Build workflow
- **examples/workflows/matrix-build-example.yaml** - Matrix builds
- **docs/GERRIT_INTEGRATION.md** - Complete integration guide

## 🎯 Key Features

1. **Mode-based execution**

   ```yaml
   with:
     mode: validate # or 'build'
   ```

2. **Conditional infrastructure**

   - Validate: No bastion, no Tailscale
   - Build: Full bastion setup

3. **Proper error handling**

   - Action exits with error code on failure
   - Caller handles Gerrit voting based on status

4. **Submodule support**

   - Caller checks out submodules
   - Works with common-packer structure

5. **Matrix builds**
   - Support for platform×template combinations
   - Matches JJB packer-builder-jobs pattern

## 📋 How Upstream Repos Use It

### In releng/builder Repository

1. **Create validation workflow** (`.github/workflows/gerrit-verify.yaml`):

   ```yaml
   - uses: lfit/packer-vexxhost-bastion-action@v1
     with:
       mode: validate
       packer_template: "templates/builder.pkr.hcl"
       packer_vars_file: "common-packer/vars/ubuntu-22.04.pkrvars.hcl"
       packer_working_dir: "packer"
   ```

2. **Create build workflow** (`.github/workflows/gerrit-merge.yaml`):

   ```yaml
   - uses: lfit/packer-vexxhost-bastion-action@v1
     with:
       mode: build
       packer_template: "templates/${{ inputs.template }}.pkr.hcl"
       packer_vars_file: "common-packer/vars/${{ inputs.platform }}.pkrvars.hcl"
       cloud_env_json: ${{ secrets.CLOUD_ENV_JSON_B64 }}
       vexxhost_auth_url: ${{ secrets.VEXXHOST_AUTH_URL }}
       # ... other secrets
       tailscale_auth_key: ${{ secrets.TAILSCALE_AUTH_KEY }}
   ```

3. **Configure secrets** in repository settings

4. **Set up Gerrit trigger** (webhook or Jenkins intermediary)

## 🔐 Required Secrets by Mode

### Validate Mode

- `GERRIT_SSH_PRIVKEY` (for voting)

### Build Mode (includes all from validate)

- `CLOUD_ENV_JSON_B64`
- `VEXXHOST_AUTH_URL`
- `VEXXHOST_PROJECT_ID`
- `VEXXHOST_USERNAME`
- `VEXXHOST_PASSWORD_B64`
- `VEXXHOST_NETWORK_ID`
- `TAILSCALE_AUTH_KEY`

## 📊 Comparison: Old vs New

### Before (JJB Only)

```yaml
# In Jenkins Job Builder
- job-template:
    name: "gerrit-packer-verify"
    builders:
      - shell: |
          cd packer
          packer validate templates/builder.pkr.hcl
```

### After (GitHub Actions with this action)

```yaml
# In .github/workflows/gerrit-verify.yaml
- uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    mode: validate
    packer_template: "templates/builder.pkr.hcl"
    packer_vars_file: "common-packer/vars/ubuntu-22.04.pkrvars.hcl"
```

## 🚀 Workflow Flow

### Gerrit Verify (Pre-Merge)

```
Gerrit Change Created
    ↓
GitHub Workflow Triggered (workflow_dispatch)
    ↓
Checkout Gerrit Change (with submodules)
    ↓
Check for Packer Changes (paths-filter)
    ↓
Validate Mode Action
    ├─ Setup Packer
    ├─ Initialize Templates
    └─ Validate Syntax
    ↓
Post Vote to Gerrit (✅ or ❌)
```

### Gerrit Merge (Post-Merge Build)

```
Gerrit Change Merged
    ↓
GitHub Workflow Triggered
    ↓
Checkout Branch (with submodules)
    ↓
Build Mode Action
    ├─ Setup Tailscale
    ├─ Create Bastion
    ├─ Setup Packer
    ├─ Build Image
    └─ Cleanup Bastion
    ↓
Publish Image to Cloud
```

## 📖 Documentation

- **[ACTION_README.md](ACTION_README.md)** - Action usage
- **[docs/GERRIT_INTEGRATION.md](docs/GERRIT_INTEGRATION.md)** - Gerrit guide
- **[examples/workflows/](examples/workflows/)** - Working examples
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup

## ✅ Testing Checklist

- [x] Validate mode works without secrets
- [x] Build mode creates bastion
- [x] Error codes propagate correctly
- [x] Submodule checkout supported
- [x] Matrix builds work
- [x] Gerrit examples documented
- [ ] Test with actual builder repo ← **Next step**

## 🎯 Next Steps for Deployment

1. **Test in builder repo:**

   ```bash
   # In releng/builder
   cp examples/workflows/gerrit-packer-verify.yaml \
      .github/workflows/
   ```

2. **Configure secrets** in builder repo

3. **Test validation:**

   - Create Gerrit change touching packer/
   - Trigger workflow manually
   - Verify vote posted

4. **Test build** (optional for now):

   - Create full build workflow
   - Test with one platform+template
   - Verify image created

5. **Create release:**
   ```bash
   git tag -a v1.0.0 -m "Initial release with Gerrit support"
   git push origin v1.0.0
   ```

## 💡 Usage Examples

### Simple Validation

```yaml
- uses: lfit/packer-vexxhost-bastion-action@v1
  with:
    mode: validate
    packer_template: "templates/builder.pkr.hcl"
    packer_vars_file: "common-packer/vars/ubuntu-22.04.pkrvars.hcl"
    packer_working_dir: "packer"
```

### Matrix Build

```yaml
strategy:
  matrix:
    platform: [ubuntu-22.04, ubuntu-24.04]
    template: [builder, docker]
steps:
  - uses: lfit/packer-vexxhost-bastion-action@v1
    with:
      mode: build
      packer_template: "templates/${{ matrix.template }}.pkr.hcl"
      packer_vars_file: "common-packer/vars/${{ matrix.platform }}.pkrvars.hcl"
      # ... secrets
```

## 🐛 Known Limitations

1. **No automatic Gerrit triggering** - Requires webhook or Jenkins intermediary
2. **One template per call** - Use matrix for multiple combinations
3. **Submodules** - Must be checked out by caller
4. **Cloud creds for validate** - Optional but may be needed for some templates

## 📞 Support

- **Issues**: File in this repository
- **Examples**: See `examples/workflows/`
- **Docs**: See `docs/GERRIT_INTEGRATION.md`
- **Questions**: Open discussion in repository

---

**Status**: ✅ Ready for testing in upstream repositories
**Version**: v1.0.0-rc1 (release candidate)
