# VexxHost Packer Bastion - Setup and Testing Guide

Complete step-by-step instructions to set up and test the workflow.

---

## 🚀 Quick Setup Overview

**Time Required:** 20-30 minutes
**Prerequisites:** GitHub account, VexxHost account, Tailscale account

**Steps:**

1. Get Tailscale credentials (5 min)
2. Get VexxHost credentials (5 min)
3. Set up GitHub repository (5 min)
4. Configure GitHub secrets (5 min)
5. Run test workflow (5 min)
6. Verify and validate (5 min)

---

## Step 1: Get Tailscale Credentials (5 min)

### 1.1 Create Tailscale Account (if needed)

1. Go to https://login.tailscale.com/start
2. Sign up with Google, Microsoft, or GitHub
3. Verify your email
4. Complete onboarding

### 1.2 Generate OAuth Key for GitHub Runner

1. Go to https://login.tailscale.com/admin/settings/oauth
2. Click **"Generate OAuth client"**
3. Configure the OAuth client:
   - **Description:** `GitHub Actions Runner`
   - **Scopes:** Select `Devices: Write`
   - **Tags:** `tag:ci`
4. Click **Generate client**
5. **IMPORTANT:** Copy the OAuth client secret immediately
   - It starts with `tskey-client-`
   - Save it as: `TAILSCALE_OAUTH_KEY`
   - You won't be able to see it again!

### 1.3 Generate Auth Key for Bastion Host

1. Go to https://login.tailscale.com/admin/settings/keys
2. Click **"Generate auth key"**
3. Configure the auth key:
   - **Description:** `Ephemeral Bastion Hosts`
   - ✅ Check **Ephemeral** (auto-cleanup after disconnect)
   - ✅ Check **Reusable** (use for multiple builds)
   - ✅ Check **Pre-approved** (no manual approval)
   - **Tags:** `tag:bastion`
   - **Expiry:** 90 days (or longer)
4. Click **Generate key**
5. **IMPORTANT:** Copy the auth key immediately
   - It starts with `tskey-auth-`
   - Save it as: `TAILSCALE_AUTH_KEY`

**✅ Checkpoint:** You should now have:

- `TAILSCALE_OAUTH_KEY` (starts with `tskey-client-`)
- `TAILSCALE_AUTH_KEY` (starts with `tskey-auth-`)

---

## Step 2: Get VexxHost Credentials (5 min)

### 2.1 Access VexxHost Dashboard

1. Go to https://console.vexxhost.net
2. Log in with your credentials
3. Select your project/tenant

### 2.2 Get OpenStack Credentials

**Option A: Download OpenRC File (Recommended)**

1. Navigate to **Project → API Access**
2. Click **Download OpenStack RC File**
3. Select **OpenStack RC File (Identity API v3)**
4. Open the downloaded file to see your credentials

**Option B: Manual Collection**

1. Go to **Project → API Access**
2. Note down these values:

```bash
# Authentication URL
VEXXHOST_AUTH_URL=https://auth.vexxhost.net/v3

# Project Information
# Navigate to: Identity → Projects
VEXXHOST_PROJECT_ID=abc123...  # Copy from project list
VEXXHOST_PROJECT_NAME=your-project-name

# User Credentials
VEXXHOST_USERNAME=your-email@example.com
VEXXHOST_PASSWORD=your-password

# Region
# Navigate to: Compute → Instances
VEXXHOST_REGION=ca-ymq-1  # Shown in top-right corner
```

### 2.3 Test OpenStack Credentials (Optional but Recommended)

Install OpenStack CLI locally:

```bash
# On macOS
brew install openstackclient

# On Ubuntu/Debian
sudo apt-get install python3-openstackclient

# On any system with Python
pip3 install python-openstackclient
```

Test your credentials:

```bash
export OS_AUTH_URL="https://auth.vexxhost.net/v3"
export OS_PROJECT_NAME="your-project-name"
export OS_USERNAME="your-username"
export OS_PASSWORD="your-password"
export OS_REGION_NAME="ca-ymq-1"
export OS_IDENTITY_API_VERSION=3
export OS_USER_DOMAIN_NAME="Default"
export OS_PROJECT_DOMAIN_NAME="Default"

# Test connection
openstack server list
openstack flavor list
openstack image list | grep -i ubuntu
openstack network list
```

**Expected output:** List of servers, flavors, images, and networks (may be empty but should not error)

**✅ Checkpoint:** You should now have:

- `VEXXHOST_AUTH_URL`
- `VEXXHOST_PROJECT_ID`
- `VEXXHOST_PROJECT_NAME`
- `VEXXHOST_USERNAME`
- `VEXXHOST_PASSWORD`
- `VEXXHOST_REGION`

---

## Step 3: Set Up GitHub Repository (5 min)

### 3.1 Initialize Repository

**Option A: New Repository**

```bash
# Create new directory
mkdir packer-jobs
cd packer-jobs

# Initialize git
git init

# Copy files from this repository
# (assuming you have the files in /home/abelur/git/github/packer-jobs)
cp -r /home/abelur/git/github/packer-jobs/* .
cp -r /home/abelur/git/github/packer-jobs/.* . 2>/dev/null

# Create initial commit
git add .
git commit -m "Initial commit: VexxHost Packer workflow"
```

**Option B: Existing Repository**

```bash
cd your-existing-repo

# Copy workflow files
mkdir -p .github/workflows
cp /path/to/packer-jobs/.github/workflows/packer-vexxhost-bastion-build.yaml .github/workflows/

# Copy templates and examples
cp -r /path/to/packer-jobs/templates .
cp -r /path/to/packer-jobs/examples .
cp -r /path/to/packer-jobs/docs .

# Commit changes
git add .
git commit -m "Add VexxHost Packer bastion workflow"
```

### 3.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `packer-jobs` (or your preferred name)
3. Description: `Automated Packer builds on VexxHost with Tailscale bastion`
4. Visibility: Choose Public or Private
5. Click **Create repository**

### 3.3 Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/packer-jobs.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**✅ Checkpoint:** Repository should be visible on GitHub with all files

---

## Step 4: Configure GitHub Secrets (5 min)

### 4.1 Navigate to Secrets Settings

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. In left sidebar: **Secrets and variables → Actions**
4. Click **New repository secret**

### 4.2 Add Tailscale Secrets

**Secret 1: TAILSCALE_OAUTH_KEY**

- Name: `TAILSCALE_OAUTH_KEY`
- Value: Paste your OAuth client secret (starts with `tskey-client-`)
- Click **Add secret**

**Secret 2: TAILSCALE_AUTH_KEY**

- Name: `TAILSCALE_AUTH_KEY`
- Value: Paste your auth key (starts with `tskey-auth-`)
- Click **Add secret**

### 4.3 Add VexxHost Secrets

**Secret 3: VEXXHOST_AUTH_URL**

- Name: `VEXXHOST_AUTH_URL`
- Value: `https://auth.vexxhost.net/v3`
- Click **Add secret**

**Secret 4: VEXXHOST_PROJECT_ID**

- Name: `VEXXHOST_PROJECT_ID`
- Value: Your project ID (from Step 2)
- Click **Add secret**

**Secret 5: VEXXHOST_PROJECT_NAME**

- Name: `VEXXHOST_PROJECT_NAME`
- Value: Your project name (from Step 2)
- Click **Add secret**

**Secret 6: VEXXHOST_USERNAME**

- Name: `VEXXHOST_USERNAME`
- Value: Your VexxHost username/email
- Click **Add secret**

**Secret 7: VEXXHOST_PASSWORD**

- Name: `VEXXHOST_PASSWORD`
- Value: Your VexxHost password
- Click **Add secret**

**Secret 8: VEXXHOST_REGION**

- Name: `VEXXHOST_REGION`
- Value: `ca-ymq-1` (or your region)
- Click **Add secret**

### 4.4 Verify Secrets

Go to **Settings → Secrets and variables → Actions**

You should see all 8 secrets listed:

- ✅ TAILSCALE_AUTH_KEY
- ✅ TAILSCALE_OAUTH_KEY
- ✅ VEXXHOST_AUTH_URL
- ✅ VEXXHOST_PASSWORD
- ✅ VEXXHOST_PROJECT_ID
- ✅ VEXXHOST_PROJECT_NAME
- ✅ VEXXHOST_REGION
- ✅ VEXXHOST_USERNAME

**✅ Checkpoint:** All 8 secrets should be visible (values hidden)

---

## Step 5: Run Test Workflow (5 min)

### 5.1 Navigate to Actions

1. In your GitHub repository, click **Actions** tab
2. You should see the workflow: **"Packer Build with VexxHost Tailscale Bastion"**
3. If you see "Get started with GitHub Actions", click on the workflow on the left sidebar

### 5.2 Run the Workflow

1. Click on **"Packer Build with VexxHost Tailscale Bastion"** workflow
2. Click **"Run workflow"** button (right side)
3. A dialog appears with workflow inputs:

**Configure Test Run:**

```
Branch: main
packer_template: builder.pkr.hcl
packer_vars: ubuntu-22.04
bastion_flavor: v3-standard-2
bastion_image: Ubuntu 22.04
debug_mode: false
```

4. Click **"Run workflow"** (green button)

### 5.3 Monitor the Workflow

The workflow will start running. You should see:

**Initial Status:**

- Yellow dot = Running
- Progress through stages visible

**Expected Timeline:**

```
00:00 - Workflow started
00:30 - Prepare job complete
01:00 - Tailscale connected
02:00 - Bastion launching
03:30 - Bastion joined Tailscale
04:00 - Packer initialization
04:30 - Template validation
05:00 - Build starts (or test completes)
```

### 5.4 Watch Live Logs

1. Click on the running workflow
2. Click on **"packer-build-vexxhost"** job
3. Expand each step to see detailed logs:
   - ✅ Checkout code
   - ✅ Setup Tailscale VPN
   - ✅ Setup Python and OpenStack CLI
   - ✅ Create cloud-init script
   - ✅ Launch bastion instance
   - ✅ Wait for bastion
   - ✅ Setup Packer
   - ✅ Validate templates

**✅ Checkpoint:** Workflow should progress through all steps

---

## Step 6: Verify and Validate (5 min)

### 6.1 Check Tailscale Admin Console

**During Workflow Run:**

1. Go to https://login.tailscale.com/admin/machines
2. You should see TWO new devices:
   - `github-runner-<run-id>` (GitHub Actions runner)
   - `bastion-gh-<run-id>` (Bastion host)
3. Both should show as "Connected"

**After Workflow Completes:**

- Devices should auto-disconnect (if ephemeral keys used)
- They may disappear from the list

### 6.2 Check VexxHost Console

**During Workflow Run:**

1. Go to https://console.vexxhost.net
2. Navigate to **Compute → Instances**
3. You should see: `bastion-gh-<run-id>`
4. Status should be: `Active` or `Build`

**After Workflow Completes:**

- Instance should be deleted automatically
- List should be empty (or not show the bastion)

### 6.3 Check Workflow Results

1. Go back to GitHub Actions
2. Workflow should show: ✅ (green checkmark) or ❌ (red X)

**For Successful Run:**

- All steps show green checkmarks
- Total time: ~5-10 minutes
- Artifacts available for download

**Download Artifacts:**

1. Scroll to bottom of workflow run page
2. Under "Artifacts" section
3. Download `packer-logs-<run-id>` (if available)

### 6.4 Review Logs

Click through each step to verify:

**Step: Setup Tailscale VPN**

```
✅ Tailscale status:
   Connected to Tailscale network
```

**Step: Launch bastion instance on VexxHost**

```
✅ Bastion instance created
   ID: abc-123-def
```

**Step: Wait for bastion to join Tailscale network**

```
⏳ Waiting for bastion to join Tailscale network...
✅ Bastion joined Tailscale at IP: 100.64.x.x
✅ Bastion initialization complete (ready marker found)
```

**Step: Initialize Packer templates**

```
✅ Initializing templates...
   Installed plugin...
```

**Step: Validate Packer templates**

```
✅ ubuntu-2204-builder-... validated with ubuntu-22.04
```

**Step: Cleanup bastion instance**

```
✅ Bastion instance deleted
✅ Bastion instance cleanup verified
```

### 6.5 Common First-Run Issues

**Issue 1: Tailscale Connection Timeout**

- **Symptom:** "Timeout waiting for bastion to join Tailscale"
- **Solution:** Check auth key settings (ephemeral, reusable, pre-approved)
- **Fix:** Regenerate auth key with correct settings

**Issue 2: OpenStack Authentication Failed**

- **Symptom:** "Authentication failed" or "Invalid credentials"
- **Solution:** Verify all VexxHost secrets are correct
- **Fix:** Double-check project ID, username, password in secrets

**Issue 3: Image Not Found**

- **Symptom:** "Image 'Ubuntu 22.04' not found"
- **Solution:** Check exact image name in VexxHost
- **Fix:** Run `openstack image list | grep -i ubuntu` and use exact name

**Issue 4: Insufficient Quota**

- **Symptom:** "Quota exceeded for instances"
- **Solution:** Delete unused instances or request quota increase
- **Fix:** Contact VexxHost support for quota increase

### 6.6 Successful Run Checklist

After a successful test run, verify:

- [ ] Workflow completed with green checkmark
- [ ] All steps passed (no red X marks)
- [ ] Bastion appeared in Tailscale admin console
- [ ] Bastion instance created in VexxHost
- [ ] Bastion instance deleted automatically
- [ ] No lingering resources in VexxHost
- [ ] Tailscale devices removed (if ephemeral)
- [ ] Logs show successful validation
- [ ] No error messages in any step

**✅ Checkpoint:** If all items checked, setup is successful!

---

## Step 7: Testing with Actual Packer Build (Optional)

### 7.1 Prepare Packer Templates

If you want to test an actual image build (not just validation):

**Option 1: Use Example Templates**

```bash
# Copy examples to packer directory
mkdir -p packer
cp -r examples/templates packer/
cp -r examples/vars packer/
cp -r examples/provision packer/

git add packer/
git commit -m "Add Packer templates for testing"
git push
```

**Option 2: Use Your Own Templates**

Ensure your templates support bastion:

```hcl
variable "bastion_host" {
  type    = string
  default = ""
}

source "openstack" "image" {
  ssh_bastion_host     = var.bastion_host != "" ? var.bastion_host : null
  ssh_bastion_username = "root"
  # ... rest of config
}
```

### 7.2 Run Build Workflow

1. Go to **Actions** → **Packer Build with VexxHost Tailscale Bastion**
2. Click **Run workflow**
3. Configure:
   ```
   packer_template: builder.pkr.hcl
   packer_vars: ubuntu-22.04
   bastion_flavor: v3-standard-2
   bastion_image: Ubuntu 22.04
   debug_mode: true  # Enable for first build
   ```
4. Click **Run workflow**

### 7.3 Monitor Build Progress

This will take longer (10-20 minutes):

```
00:00 - Setup and bastion launch
05:00 - Packer validation complete
06:00 - Packer build starts
10:00 - Provisioning scripts running
15:00 - Image snapshot creation
18:00 - Build complete
20:00 - Cleanup and workflow finish
```

### 7.4 Verify Built Image

1. Go to VexxHost Console
2. Navigate to **Compute → Images**
3. Look for your newly created image
4. Name format: `ubuntu-2204-builder-YYYY-MM-DD-HHMM`

---

## Troubleshooting Test Runs

### Enable Debug Mode

For any issues, rerun with debug enabled:

1. **Actions** → **Run workflow**
2. Set `debug_mode: true`
3. Click **Run workflow**

This enables:

- `PACKER_LOG=1` (verbose Packer output)
- Extended logging
- Additional diagnostic information

### View Detailed Logs

**Bastion Console Log:**

```bash
# In workflow, check step output for:
openstack console log show bastion-gh-12345 --lines 100
```

**Bastion Init Log:**

```bash
# If SSH accessible:
ssh root@<bastion-tailscale-ip> cat /var/log/bastion-init.log
```

### Manual Cleanup

If workflow fails and leaves resources:

```bash
# List all instances
openstack server list

# Delete stuck bastion
openstack server delete bastion-gh-12345

# Force delete if needed
openstack server delete --force bastion-gh-12345
```

### Tailscale Device Cleanup

If devices remain after workflow:

1. Go to https://login.tailscale.com/admin/machines
2. Find orphaned devices
3. Click **Delete** for each
4. Or use CLI: `tailscale logout` on device

---

## Next Steps After Successful Test

### 1. Automate Builds

Enable automatic triggers:

```yaml
# Edit .github/workflows/packer-vexxhost-bastion-build.yaml
on:
  push:
    branches: [main]
    paths:
      - "packer/**"
  schedule:
    - cron: "0 2 * * 1" # Weekly Monday 2 AM
```

### 2. Add Notifications

Get notified of build results:

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 3. Optimize Costs

- Use smaller flavor for testing: `v3-starter-1`
- Review build frequency
- Monitor VexxHost billing

### 4. Scale Up

Add parallel builds:

```yaml
strategy:
  matrix:
    os: [ubuntu-22, ubuntu-24, debian-12]
```

### 5. Add More Templates

Create templates for different purposes:

- Development images
- Production images
- CI/CD images
- Custom applications

---

## Quick Reference Commands

### Local Testing Commands

```bash
# Test OpenStack connection
openstack server list

# Test Packer template
cd packer
packer init templates/builder.pkr.hcl
packer validate -var-file=vars/ubuntu-22.04.pkrvars.hcl templates/builder.pkr.hcl

# Test cloud-init syntax
cloud-init schema --config-file templates/bastion-cloud-init.yaml

# Run pre-commit checks
pre-commit run --all-files
```

### GitHub Actions Commands

```bash
# Trigger workflow via GitHub CLI
gh workflow run "Packer Build with VexxHost Tailscale Bastion"

# Watch workflow run
gh run watch

# View logs
gh run view --log
```

### VexxHost Commands

```bash
# List instances
openstack server list

# Show instance details
openstack server show bastion-gh-12345

# Get console log
openstack console log show bastion-gh-12345

# Delete instance
openstack server delete bastion-gh-12345
```

---

## Success Criteria

Your setup is successful when:

✅ Workflow completes without errors
✅ Bastion appears and disappears in Tailscale
✅ Bastion creates and deletes in VexxHost
✅ Packer templates validate successfully
✅ No manual cleanup needed
✅ Total time < 10 minutes (for validation)
✅ Costs within expected range (~$0.02/build)

---

## Support

- **Documentation:** See `docs/` directory
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Issues:** Open GitHub issue in your repository

**Happy building! 🚀**
