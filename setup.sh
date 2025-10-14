#!/bin/bash
# Setup script for VexxHost Packer workflow
# SPDX-License-Identifier: Apache-2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "VexxHost Packer Workflow Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo "ℹ️  $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check if git is installed
if command -v git &> /dev/null; then
    success "Git is installed: $(git --version)"
else
    error "Git is not installed"
    exit 1
fi

# Check if Python is installed
if command -v python3 &> /dev/null; then
    success "Python is installed: $(python3 --version)"
else
    warning "Python is not installed (recommended for validation)"
fi

# Check if Packer is installed
if command -v packer &> /dev/null; then
    success "Packer is installed: $(packer version | head -1)"
else
    warning "Packer is not installed (optional for local testing)"
    info "Install from: https://www.packer.io/downloads"
fi

# Check if OpenStack CLI is installed
if command -v openstack &> /dev/null; then
    success "OpenStack CLI is installed"
else
    warning "OpenStack CLI is not installed (optional for local testing)"
    info "Install with: pip install python-openstackclient"
fi

echo ""
echo "========================================="
echo "Repository Structure"
echo "========================================="
echo ""

# Show current structure
if command -v tree &> /dev/null; then
    tree -L 2 -I '.git' "$SCRIPT_DIR"
else
    find "$SCRIPT_DIR" -maxdepth 2 -type d | grep -v ".git" | sort
fi

echo ""
echo "========================================="
echo "Setup Options"
echo "========================================="
echo ""
echo "1. Initialize Git repository (if not already)"
echo "2. Setup packer directory from examples"
echo "3. Install pre-commit hooks"
echo "4. Validate workflow files"
echo "5. Run template tests"
echo "6. Show secret configuration guide"
echo "7. Exit"
echo ""

read -r -p "Select option (1-7): " option

case $option in
    1)
        echo ""
        info "Initializing Git repository..."
        if [ -d "$SCRIPT_DIR/.git" ]; then
            warning "Git repository already exists"
        else
            git init "$SCRIPT_DIR"
            success "Git repository initialized"

            # Create initial commit
            git -C "$SCRIPT_DIR" add .
            git -C "$SCRIPT_DIR" commit -m "Initial commit: VexxHost Packer workflow" || true
            success "Initial commit created"
        fi
        ;;

    2)
        echo ""
        info "Setting up packer directory..."

        if [ -d "$SCRIPT_DIR/packer" ]; then
            warning "packer directory already exists"
            read -r -p "Overwrite? (y/N): " overwrite
            if [[ ! $overwrite =~ ^[Yy]$ ]]; then
                info "Skipping packer setup"
                exit 0
            fi
        fi

        mkdir -p "$SCRIPT_DIR/packer"
        cp -r "$SCRIPT_DIR/examples/templates" "$SCRIPT_DIR/packer/"
        cp -r "$SCRIPT_DIR/examples/vars" "$SCRIPT_DIR/packer/"
        cp -r "$SCRIPT_DIR/examples/provision" "$SCRIPT_DIR/packer/"

        success "Packer directory created with example templates"
        info "Location: $SCRIPT_DIR/packer"
        ;;

    3)
        echo ""
        info "Installing pre-commit hooks..."

        if ! command -v pre-commit &> /dev/null; then
            warning "pre-commit is not installed"
            info "Installing via pip..."
            pip install pre-commit || pip3 install pre-commit || {
                error "Failed to install pre-commit"
                info "Install manually: pip install pre-commit"
                exit 1
            }
        fi

        cd "$SCRIPT_DIR"
        pre-commit install
        success "Pre-commit hooks installed"

        info "Running pre-commit on all files..."
        if pre-commit run --all-files; then
            success "All pre-commit checks passed"
        else
            warning "Some pre-commit checks failed (this is normal for first run)"
            info "Files have been auto-formatted. Review changes with: git diff"
        fi
        ;;

    4)
        echo ""
        info "Validating workflow files..."

        if ! command -v python3 &> /dev/null; then
            error "Python3 is required for validation"
            exit 1
        fi

        # Validate workflow YAML
        if python3 -c "import yaml; yaml.safe_load(open('$SCRIPT_DIR/.github/workflows/packer-vexxhost-bastion-build.yaml'))"; then
            success "Workflow YAML is valid"
        else
            error "Workflow YAML validation failed"
        fi

        # Validate pre-commit config
        if python3 -c "import yaml; yaml.safe_load(open('$SCRIPT_DIR/.pre-commit-config.yaml'))"; then
            success "Pre-commit config is valid"
        else
            error "Pre-commit config validation failed"
        fi

        # Validate yamllint config
        if python3 -c "import yaml; yaml.safe_load(open('$SCRIPT_DIR/.yamllint.conf'))"; then
            success "Yamllint config is valid"
        else
            error "Yamllint config validation failed"
        fi
        ;;

    5)
        echo ""
        info "Running template tests..."

        if [ ! -f "$SCRIPT_DIR/test-templates.sh" ]; then
            error "test-templates.sh not found"
            exit 1
        fi

        bash "$SCRIPT_DIR/test-templates.sh"
        ;;

    6)
        echo ""
        echo "========================================="
        echo "GitHub Secrets Configuration Guide"
        echo "========================================="
        echo ""
        echo "Go to: GitHub → Settings → Secrets and variables → Actions"
        echo ""
        echo "Required secrets (8 total):"
        echo ""
        echo "Tailscale (2):"
        echo "  TAILSCALE_OAUTH_KEY      - OAuth client secret"
        echo "  TAILSCALE_AUTH_KEY       - Auth key for bastion"
        echo ""
        echo "VexxHost (6):"
        echo "  VEXXHOST_AUTH_URL        - https://auth.vexxhost.net/v3"
        echo "  VEXXHOST_PROJECT_ID      - Your project ID"
        echo "  VEXXHOST_PROJECT_NAME    - Your project name"
        echo "  VEXXHOST_USERNAME        - Your username"
        echo "  VEXXHOST_PASSWORD        - Your password"
        echo "  VEXXHOST_REGION          - ca-ymq-1 (or your region)"
        echo ""
        echo "Optional (2):"
        echo "  CLOUD_ENV_B64            - Base64 encoded cloud-env.pkrvars.hcl"
        echo "  CLOUDS_YAML_B64          - Base64 encoded clouds.yaml"
        echo ""
        echo "For detailed setup instructions, see:"
        echo "  - docs/QUICK_START.md"
        echo "  - README.md"
        echo ""
        ;;

    7)
        echo ""
        info "Exiting setup"
        exit 0
        ;;

    *)
        error "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Next Steps"
echo "========================================="
echo ""
echo "1. Configure GitHub secrets (option 6 for guide)"
echo "2. Review documentation:"
echo "   - README.md"
echo "   - docs/QUICK_START.md"
echo "   - docs/TROUBLESHOOTING.md"
echo "3. Customize Packer templates in packer/ directory"
echo "4. Run workflow in GitHub Actions"
echo ""
success "Setup complete!"
echo ""
