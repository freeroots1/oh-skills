import subprocess, json, time

ALL = "/tmp/all_4719_domains.txt"
OUT = "/tmp/phase2_scan_results.json"
LOG = "/tmp/phase2_scan.log"

def log(msg):
    t = time.strftime("%H:%M:%S")
    with open(LOG, "a") as f: f.write(f"[{t}] {msg}\n")

def curl(url, timeout=8):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", str(timeout),
           "-o", "/tmp/bt.tmp", "-D", "/tmp/hd.tmp", "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        code = r.stdout.strip()
        try:
            with open("/tmp/hd.tmp") as f: hdrs = f.read()
        except: hdrs = ""
        return code, hdrs
    except:
        return "000", ""

# Load existing results (merge all sources)
done = set()

# 1. overnight results
try:
    with open("/tmp/overnight_scan_results.json") as f:
        ov = json.load(f)
    for d in ov.get("targets", {}):
        done.add(d)
    log(f"Loaded {len(ov.get(targets,{}))} overnight targets")
except: pass

# 2. old phase2 results (nested format)
try:
    with open("/tmp/phase2_scan_results.json") as f:
        old = json.load(f)
    for d in old.get("targets", {}):
        done.add(d)
    log(f"Loaded {len(old.get(targets,{}))} old phase2 targets")
except: pass

# 3. scanned_domains.txt
try:
    with open("/tmp/scanned_domains.txt") as f:
        for line in f:
            d = line.strip()
            if d: done.add(d)
except: pass

log(f"Total already done: {len(done)}")

# Load all domains
with open(ALL) as f:
    all_d = [l.strip() for l in f if l.strip()]

remaining = [d for d in all_d if d not in done]
log(f"Remaining to scan: {len(remaining)}")

# Load/write results in simple flat format
results = {}
try:
    with open(OUT) as f:
        results = json.load(f)
except:
    results = {}

count = 0
for domain in remaining[:4000]:
    count += 1
    info = {"alive": False}
    code, hdrs = curl(f"http://{domain}/")
    if code in ["000", ""]:
        results[domain] = info
        continue
    info["alive"] = True
    
    for line in hdrs.split("\n"):
        l = line.strip().lower()
        if l.startswith("server:"): info["server"] = l[7:].strip()[:100]
        if l.startswith("x-powered-by:"):
            pw = l[14:].strip()[:100]
            info["powered"] = pw
            if "thinkphp" in pw.lower():
                info["cms"] = "ThinkPHP"
                log(f"[*] ThinkPHP: {domain}")
            elif "pboot" in pw.lower():
                info["cms"] = "PbootCMS"
                log(f"[*] PbootCMS: {domain}")
    
    # .env check
    code2, _ = curl(f"http://{domain}/.env", 5)
    if code2 == "200":
        info["env_200"] = True
        log(f"[*] .ENV 200: {domain}")
    
    results[domain] = info
    
    if count % 200 == 0:
        log(f"Progress: {len(results)} results | {count}/{len(remaining[:4000])} scanned")
        with open(OUT, "w") as f: json.dump(results, f)

with open(OUT, "w") as f: json.dump(results, f)
alive = sum(1 for v in results.values() if v.get("alive"))
log(f"DONE: {len(results)} total | Alive: {alive}")
log(f"Output: {OUT}")
