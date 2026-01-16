#!/bin/bash
# Tailscale setup script for bus display Pi
# Run this once to enable SSH access from anywhere

echo "========================================="
echo "   TAILSCALE SETUP FOR BUS DISPLAY"
echo "========================================="
echo

# Check if already installed
if command -v tailscale &> /dev/null; then
    echo "Tailscale is already installed."
    echo
    echo "Current status:"
    tailscale status
    echo
    echo "Your Tailscale IP: $(tailscale ip -4 2>/dev/null || echo 'not connected')"
    echo
    read -p "Reinstall? (y/N): " reinstall
    if [[ ! "$reinstall" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "1/3 - Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

if [ $? -ne 0 ]; then
    echo "Error: Failed to install Tailscale"
    exit 1
fi

echo
echo "2/3 - Starting Tailscale..."
echo
echo "A URL will appear below - open it in your browser to authenticate."
echo "Make sure to sign in with the same account you'll use on your Mac/phone."
echo
sudo tailscale up

echo
echo "3/3 - Setup complete!"
echo
echo "========================================="
echo "   YOUR TAILSCALE IP"
echo "========================================="
tailscale ip -4
echo "========================================="
echo
echo "NEXT STEPS:"
echo
echo "1. Install Tailscale on your Mac:"
echo "   brew install --cask tailscale"
echo "   Or download from: https://tailscale.com/download/mac"
echo
echo "2. Sign in with the same account"
echo
echo "3. Connect from anywhere:"
echo "   ssh pi@$(tailscale ip -4)"
echo
echo "Or using MagicDNS hostname:"
echo "   ssh pi@$(hostname)"
echo
echo "Then run the remote control:"
echo "   python3 bus_remote.py"
echo
