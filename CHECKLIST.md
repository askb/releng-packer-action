# VexxHost Packer Workflow - Setup Checklist

Use this checklist to ensure your setup is complete and working correctly.

## Pre-Setup Checklist

- [ ] GitHub repository created or accessible
- [ ] VexxHost account active with API access
- [ ] Tailscale account created (free tier is fine)
- [ ] Local development environment ready (optional)

## Step 1: Tailscale Configuration

### OAuth Client
- [ ] Logged in to Tailscale admin console
- [ ] Navigated to Settings → OAuth Clients
- [ ] Generated OAuth client with:
  - [ ] Scope: `devices:write`
  - [ ] Tags: `tag:ci`
- [ ] Copied OAuth client secret
- [ ] Saved as `TAILSCALE_OAUTH_KEY`

### Auth Key
- [ ] Navigated to Settings → Auth Keys
- [ ] Generated auth key with:
  - [ ] Reusable enabled
  - [ ] Ephemeral enabled
  - [ ] Pre-authorized enabled
  - [ ] Tags: `tag:bastion`
- [ ] Copied auth key
- [ ] Saved as `TAILSCALE_AUTH_KEY`

## Step 2: VexxHost Configuration

### Credentials
- [ ] Logged in to VexxHost dashboard
- [ ] Located API access section
- [ ] Noted down:
  - [ ] Auth URL: `https://auth.vexxhost.net/v3`
  - [ ] Project ID
  - [ ] Project name
  - [ ] Username
  - [ ] Password
  - [ ] Region (e.g., `ca-ymq-1`)

### Testing (Optional)
- [ ] Installed `python-openstackclient`
- [ ] Exported credentials to environment
- [ ] Ran `openstack server list` successfully
- [ ] Verified access to flavors: `openstack flavor list`
- [ ] Verified access to images: `openstack image list`

## Step 3: GitHub Repository Setup

### Repository Configuration
- [ ] Repository created or forked
- [ ] Cloned to local machine
- [ ] Checked out main/master branch

### Secrets Configuration
Navigate to: **Settings → Secrets and variables → Actions**

- [ ] Created `TAILSCALE_OAUTH_KEY`
- [ ] Created `TAILSCALE_AUTH_KEY`
- [ ] Created `VEXXHOST_AUTH_URL`
- [ ] Created `VEXXHOST_PROJECT_ID`
- [ ] Created `VEXXHOST_PROJECT_NAME`
- [ ] Created `VEXXHOST_USERNAME`
- [ ] Created `VEXXHOST_PASSWORD`
- [ ] Created `VEXXHOST_REGION`

Optional secrets:
- [ ] Created `CLOUD_ENV_B64` (if using existing templates)
- [ ] Created `CLOUDS_YAML_B64` (if using existing templates)

### Verify Secrets
- [ ] All required secrets show in secrets list
- [ ] No typos in secret names
- [ ] Values pasted correctly (no extra spaces)

## Step 4: Workflow Files

### Copy/Create Files
- [ ] Copied workflow file to `.github/workflows/packer-vexxhost-bastion-build.yaml`
- [ ] Created `.pre-commit-config.yaml`
- [ ] Created `.yamllint.conf`
- [ ] Created `.gitignore`
- [ ] Created `README.md`

### Documentation
- [ ] Created `docs/QUICK_START.md`
- [ ] Created `docs/TROUBLESHOOTING.md`

### Helper Scripts
- [ ] Created `setup.sh` (and made executable)
- [ ] Created `test-templates.sh` (and made executable)

## Step 5: Packer Templates

### Example Templates
- [ ] Created `examples/templates/builder.pkr.hcl`
- [ ] Created `examples/vars/ubuntu-22.04.pkrvars.hcl`
- [ ] Created `examples/provision/baseline.sh` (and made executable)

### Your Templates (if using existing)
- [ ] Templates include `bastion_host` variable
- [ ] Templates configure `ssh_bastion_host` conditionally
- [ ] Templates tested locally (optional)
- [ ] Variable files validated

## Step 6: Local Validation (Optional)

### Pre-commit
- [ ] Installed pre-commit: `pip install pre-commit`
- [ ] Ran `pre-commit install`
- [ ] Ran `pre-commit run --all-files`
- [ ] Fixed any issues reported

### Workflow YAML
- [ ] Validated workflow YAML syntax
- [ ] Checked for indentation issues
- [ ] Verified all secret references correct

### Packer Templates
- [ ] Ran `./test-templates.sh` successfully
- [ ] All templates validated
- [ ] No syntax errors

## Step 7: Commit and Push

### Git Operations
- [ ] Staged all files: `git add .`
- [ ] Committed: `git commit -m "Add VexxHost Packer workflow"`
- [ ] Pushed to GitHub: `git push`
- [ ] Verified files appear in GitHub web UI

## Step 8: First Workflow Run

### Trigger Workflow
- [ ] Navigated to **Actions** tab in GitHub
- [ ] Found **Packer Build with VexxHost Tailscale Bastion**
- [ ] Clicked **Run workflow**
- [ ] Selected branch (main/master)
- [ ] Used default inputs or customized:
  - [ ] `packer_template`: `builder.pkr.hcl`
  - [ ] `packer_vars`: `ubuntu-22.04`
  - [ ] `bastion_flavor`: `v3-standard-2`
  - [ ] `bastion_image`: `Ubuntu 22.04`
  - [ ] `debug_mode`: `false`
- [ ] Clicked **Run workflow** (green button)

### Monitor Execution
- [ ] Workflow started successfully
- [ ] Prepare job completed
- [ ] Packer build job started
- [ ] Tailscale setup completed
- [ ] OpenStack CLI installed
- [ ] Bastion instance created
- [ ] Bastion joined Tailscale
- [ ] Packer validation passed
- [ ] Packer build started
- [ ] Build completed (or in progress)

### Check Progress
- [ ] Viewed real-time logs in GitHub Actions
- [ ] Monitored Tailscale admin console for bastion
- [ ] Checked VexxHost dashboard for instances

## Step 9: Verify Results

### Successful Completion
- [ ] Workflow completed with green checkmark
- [ ] All jobs succeeded
- [ ] Build artifacts uploaded
- [ ] Logs available for download

### VexxHost Verification
- [ ] New image created in VexxHost
- [ ] Bastion instance deleted automatically
- [ ] No lingering resources

### Tailscale Verification
- [ ] Bastion device removed (if ephemeral)
- [ ] Runner disconnected
- [ ] No orphaned devices

### Artifacts
- [ ] Downloaded packer-logs artifact
- [ ] Reviewed build logs
- [ ] Checked for warnings/errors

## Step 10: Cleanup and Optimization

### Manual Cleanup (if needed)
- [ ] No bastion instances left in VexxHost
- [ ] No extra Tailscale devices
- [ ] GitHub Actions workflow logs archived

### Optimization
- [ ] Adjusted bastion flavor if needed
- [ ] Configured auto-trigger (if desired)
- [ ] Set up scheduled builds (if desired)
- [ ] Enabled notifications (if desired)

## Troubleshooting Checklist

If workflow failed, check:

### OpenStack Issues
- [ ] Credentials are correct
- [ ] Project has sufficient quota
- [ ] Region is correct
- [ ] Image name exists
- [ ] Flavor is available
- [ ] Network exists

### Tailscale Issues
- [ ] OAuth key has correct scope
- [ ] Auth key is reusable
- [ ] Auth key is pre-authorized
- [ ] ACLs allow CI tag
- [ ] Auth key not expired

### Bastion Issues
- [ ] Cloud-init completed
- [ ] Console logs reviewed
- [ ] SSH service running
- [ ] Tailscale installed

### Packer Issues
- [ ] Templates validated locally
- [ ] Variables defined correctly
- [ ] Bastion variable supported
- [ ] Provisioning scripts exist

### GitHub Issues
- [ ] All secrets configured
- [ ] Workflow YAML valid
- [ ] Branch has workflow file
- [ ] No permission issues

## Post-Setup Actions

### Documentation
- [ ] Team members informed
- [ ] Documentation shared
- [ ] Runbook created
- [ ] Secrets documented (securely)

### Monitoring
- [ ] Set up build notifications
- [ ] Monitor VexxHost costs
- [ ] Track workflow durations
- [ ] Review failed builds

### Maintenance
- [ ] Schedule credential rotation
- [ ] Update documentation as needed
- [ ] Keep Packer version current
- [ ] Review and optimize regularly

## Success Criteria

You've successfully completed setup when:

- ✅ Workflow runs without errors
- ✅ Bastion auto-creates and auto-deletes
- ✅ Packer builds complete successfully
- ✅ Images appear in VexxHost
- ✅ No manual intervention needed
- ✅ Costs within expected range
- ✅ Team can trigger builds easily

## Quick Reference

### Essential Commands
```bash
# Test OpenStack
openstack server list

# Validate templates
./test-templates.sh

# Run pre-commit
pre-commit run --all-files

# Setup help
./setup.sh
```

### Important Files
- Workflow: `.github/workflows/packer-vexxhost-bastion-build.yaml`
- Documentation: `docs/QUICK_START.md`, `docs/TROUBLESHOOTING.md`
- Examples: `examples/`

### Key Links
- [Tailscale Admin](https://login.tailscale.com/admin)
- [VexxHost Dashboard](https://console.vexxhost.net)
- [GitHub Actions](https://github.com/YOUR_ORG/YOUR_REPO/actions)

---

**Last Updated:** Use `git log -1 --format=%cd CHECKLIST.md` to see
**Version:** 1.0.0
