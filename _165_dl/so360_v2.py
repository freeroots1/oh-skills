#!/usr/bin/env python3
"""批量360收录查询v2(带cookie处理302)"""
import urllib.request, ssl, re, time, sys, http.cookiejar

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check(domain):
    try:
        cj = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
        op.addheaders = [("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                         ("Accept","text/html,application/xhtml+xml"),
                         ("Accept-Language","zh-CN,zh;q=0.9"),
                         ("Referer","https://www.so.com/")]
        # 先访问首页拿cookie
        try:
            op.open("https://www.so.com/", timeout=6).read()
        except Exception:
            pass
        h = op.open(f"https://www.so.com/s?q=site%3A{domain}", timeout=8).read().decode("utf-8","ignore")
        m = re.search(r'约(\d+)个网页被360搜索收录', h)
        if m:
            return f"收录{m.group(1)}页"
        if "未找到相关搜索结果" in h:
            return "未收录"
        if "的站点信息" in h:
            m2 = re.search(r'约(\d+)个网页', h)
            return f"收录{m2.group(1) if m2 else '?'}页"
        if "验证" in h and len(h) < 3000:
            return "验证码"
        return f"无数据({len(h)})"
    except Exception as e:
        return f"ERR:{str(e)[:25]}"

domains = sys.argv[1:]
for d in domains:
    print(f"{d}: {check(d)}", flush=True)
    time.sleep(1)
