#!/usr/bin/env python3
"""fv_domain_hunt2.py - 4类向量用具体模板目录扫描(精确)
文件上传/SSRF/身份认证失效/SQL注入 - 用nuclei的通用+泛化模板
"""
import subprocess, os, sys, time

TARGETS = "/tmp/fv_domain_targets.txt"
HITS = "/tmp/fv_domain_hits.txt"

def build_targets():
    doms = set()
    for f in ['/opt/msray/usable_pool.txt', '/opt/msray/alive_pool.txt']:
        try:
            doms |= set(open(f).read().split())
        except: pass
    with open(TARGETS, 'w') as f:
        for d in sorted(doms):
            if d.strip():
                f.write(d.strip() + '\n')
    return len(doms)

def run(category, template_paths, severity='critical,high,medium'):
    print('\n=== [%s] ===' % category, flush=True)
    outfile = '/tmp/fv_%s.txt' % category
    cmd = ['nuclei', '-l', TARGETS, '-t'] + template_paths + [
        '-c', '12', '-silent', '-o', outfile,
        '-severity', severity, '-timeout', '12']
    print('templates:', template_paths, flush=True)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
        hits = open(outfile).read().strip().split('\n') if os.path.exists(outfile) else []
        hits = [h for h in hits if h.strip()]
        print('[%s] %d hits' % (category, len(hits)), flush=True)
        for h in hits[:40]:
            print('  ' + h, flush=True)
            with open(HITS, 'a') as f:
                f.write('%s|%s\n' % (category, h))
    except subprocess.TimeoutExpired:
        print('[%s] TIMEOUT' % category, flush=True)
    except Exception as e:
        print('[%s] ERROR: %s' % (category, e), flush=True)

def main():
    n = build_targets()
    print('targets: %d' % n, flush=True)

    # 4类漏洞的具体模板(通用+泛化)
    V = '/root/nuclei-templates/http/vulnerabilities'
    run('upload', [V + '/generic/generic-file-upload.yaml'] if os.path.exists(V+'/generic/generic-file-upload.yaml') else [V+'/codimd-file-upload.yaml', V+'/ueditor-arbitrary-file-upload.yaml'])
    run('ssrf', [V + '/generic/xmlrpc-pingback-ssrf.yaml', V + '/generic/request-based-interaction.yaml', V + '/bentoml-ssrf.yaml'])
    run('sqli', [V + '/generic/error-based-sql-injection.yaml'])
    # 国产OA SQLi模板(泛微/蓝凌等)
    run('sqli-oa', [V + '/weaver/ecology/ecology-syncuserinfo-sqli.yaml',
                    V + '/weaver/weaver-checkserver-sqli.yaml',
                    V + '/weaver/weaver-e-cology-validate-sqli.yaml',
                    V + '/landray/landray-eis-sqli.yaml'])
    # auth用tag(模板分散)
    outfile = '/tmp/fv_auth-bypass.txt'
    cmd = ['nuclei', '-l', TARGETS, '-tags', 'auth-bypass,broken-auth,unauth,default-login',
           '-c', '12', '-silent', '-o', outfile, '-severity', 'critical,high,medium', '-timeout', '12']
    print('\n=== [auth-bypass] ===', flush=True)
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
        hits = open(outfile).read().strip().split('\n') if os.path.exists(outfile) else []
        hits = [h for h in hits if h.strip()]
        print('[auth-bypass] %d hits' % len(hits), flush=True)
        for h in hits[:40]:
            print('  ' + h, flush=True)
            with open(HITS, 'a') as f:
                f.write('auth-bypass|%s\n' % h)
    except Exception as e:
        print('ERROR', e, flush=True)

    print('\n=== ALL DONE ===', flush=True)

if __name__ == '__main__':
    main()
