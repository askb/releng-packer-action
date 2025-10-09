# Ubuntu 22.04 Builder Configuration

# Base image from OpenStack
base_image = "Ubuntu 22.04"

# Image naming
image_name = "ubuntu-2204-builder-{{isotime \"2006-01-02-1504\"}}"

# Instance configuration
flavor = "v3-standard-2"
ssh_user = "ubuntu"
distro = "ubuntu2204"

# Network configuration
cloud_network = "default"
cloud_region = "ca-ymq-1"

# Build timeouts
ssh_timeout = "30m"
ssh_handshake_attempts = 20
build_timeout = "60m"

# Bastion configuration
# These will be overridden by workflow, but can be set for local testing
# bastion_host = "100.64.1.100"
# bastion_user = "root"
