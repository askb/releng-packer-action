#!/bin/bash
# Test and validate Packer templates
# SPDX-License-Identifier: Apache-2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKER_DIR="${SCRIPT_DIR}/examples"
TEMPLATE_DIR="${PACKER_DIR}/templates"
VARS_DIR="${PACKER_DIR}/vars"

echo "========================================="
echo "Packer Template Validation"
echo "========================================="

# Check if packer is installed
if ! command -v packer &> /dev/null; then
    echo "❌ Packer is not installed"
    echo "Install from: https://www.packer.io/downloads"
    exit 1
fi

echo "✅ Packer version: $(packer version)"
echo ""

# Initialize plugins
echo "Initializing Packer plugins..."
for template in "${TEMPLATE_DIR}"/*.pkr.hcl; do
    if [[ "$template" == *"variables"* ]]; then
        continue
    fi
    
    echo "  Initializing $(basename "$template")..."
    packer init "$template" || {
        echo "❌ Failed to initialize $template"
        exit 1
    }
done
echo "✅ Plugins initialized"
echo ""

# Format check
echo "Checking template formatting..."
if packer fmt -check -recursive "${TEMPLATE_DIR}"; then
    echo "✅ Templates are properly formatted"
else
    echo "⚠️  Templates need formatting. Run: packer fmt -recursive ${TEMPLATE_DIR}"
fi
echo ""

# Validate templates
echo "Validating templates..."
validation_failed=0

for varfile in "${VARS_DIR}"/*.pkrvars.hcl; do
    echo ""
    echo "Testing with: $(basename "$varfile")"
    echo "---"
    
    for template in "${TEMPLATE_DIR}"/*.pkr.hcl; do
        if [[ "$template" == *"variables"* ]]; then
            continue
        fi
        
        template_name=$(basename "$template")
        echo -n "  $template_name ... "
        
        if packer validate \
            -var-file="$varfile" \
            -var="bastion_host=" \
            "$template" &> /dev/null; then
            echo "✅"
        else
            echo "❌"
            echo "    Running validation with output:"
            packer validate \
                -var-file="$varfile" \
                -var="bastion_host=" \
                "$template" || true
            validation_failed=1
        fi
    done
done

echo ""
echo "========================================="
if [ $validation_failed -eq 0 ]; then
    echo "✅ All validations passed!"
    exit 0
else
    echo "❌ Some validations failed"
    exit 1
fi
