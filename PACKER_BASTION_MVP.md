MVP: Packer Image Build on OpenStack via Bastion

   Problem: GitHub Actions runners can't directly reach OpenStack VMs to provision
   Packer images because VMs are on private networks.

   Solution: Use a Tailscale-connected bastion host as SSH proxy.

   Architecture

     GitHub Runner (has Tailscale) 
         ↓ (Tailscale VPN)
     Bastion Host (OpenStack VM with Tailscale)
         ↓ (OpenStack private network)
     Target VM (being provisioned by Packer)

   Current Status

   Working on getting the GitHub runner and bastion to successfully connect via
   Tailscale so Packer can SSH through the bastion to provision images.

   Key Components

     - Tailscale OAuth: Runner + bastion join same tailnet with tag:ci and tag:bastion
     - Bastion VM: Cloud-init installs Tailscale, joins network, becomes SSH proxy
     - Packer: Uses ssh_bastion_host pointing to bastion's Tailscale IP
     - Workflow: Detects bastion IP, waits for ready marker, runs Packer build

   Blocking Issue

   Tailscale connection establishment between runner and bastion - fixing OAuth
   client config and ACL permissions to allow tagged devices to communicate.