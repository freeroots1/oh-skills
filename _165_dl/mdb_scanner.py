#!/usr/bin/env python3
"""Scan all domains for exposed Access databases (.mdb)"""
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Known paths where .mdb files are commonly found
MDB_PATHS = [
    "/data/db.mdb", "/database/db.mdb", "/db/db.mdb", "/data/data.mdb",
    "/main/data/db.mdb", "/admin/data/db.mdb", "/databackup/db.mdb",
    "/data/%23db.mdb", "/data/database.mdb", "/inc/db.mdb",
    "/db.mdb", "/data.mdb", "/wwwroot/data/db.mdb"
]

# Also check for other common leaks
OTHER_LEAKS = [
    "/web.config", "/.env", "/phpinfo.php", "/info.php", "/test.php",
    "/1.php", "/x.php", "/shell.php", "/cmd.php"
]

# Load domains
with open("/root/tools/old_sites_db.json") as f:
    sites = json.load(f)

domains = [s["domain"] for s in sites["sites"]]

print(f"Scanning {len(domains)} domains for exposed files...", flush=True)

found_mdb = []
found_other = []

for i, domain in enumerate(domains):
    # Check .mdb files
    for path in MDB_PATHS:
        try:
            req = urllib.request.Request(f"http://{domain}{path}")
            req.add_header("User-Agent", "Mozilla/5.0")
            r = urllib.request.urlopen(req, timeout=4, context=ctx)
            size = int(r.headers.get("Content-Length", 0))
            content_type = r.headers.get("Content-Type", "")
            if size > 50000 or "application/x-msaccess" in content_type.lower():
                found_mdb.append((domain, path, size))
                print(f"!!! MDB: {domain}{path} ({size}B)", flush=True)
        except:
            pass
    
    # Quick check for other leaks (just check existence)
    for path in OTHER_LEAKS[:5]:
        try:
            req = urllib.request.Request(f"http://{domain}{path}")
            r = urllib.request.urlopen(req, timeout=3, context=ctx)
            if r.status == 200:
                found_other.append((domain, path))
                print(f"  LEAK: {domain}{path}", flush=True)
        except:
            pass
    
    if i % 10 == 0:
        print(f"[{i}/{len(domains)}]", flush=True)

print(f"\n=== Results ===", flush=True)
print(f"MDB databases: {len(found_mdb)}", flush=True)
for d, p, s in found_mdb:
    print(f"  {d}{p} ({s}B)", flush=True)
print(f"Other leaks: {len(found_other)}", flush=True)
for d, p in found_other:
    print(f"  {d}{p}", flush=True)
