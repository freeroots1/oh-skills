#!/usr/bin/env python3
"""搜狗/360/必应收录查询"""
import urllib.request, ssl, re, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check_sogou(d):
    try:
        req = urllib.request.Request(f"https://www.sogou.com/web?query=site%3A{d}", headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        h = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode("utf-8","ignore")
        if "没有找到" in h or "未找到" in h:
            return "未收录"
        if "验证码" in h or "请输入验证码" in h:
            return "验证码"
        nums = re.findall(r'约([\d,]+)条结果', h)
        return f"收录({nums[0] if nums else '?'})"
    except Exception as e:
        return f"ERR:{str(e)[:20]}"

def check_bing(d):
    try:
        req = urllib.request.Request(f"https://www.bing.com/search?q=site%3A{d}", headers={"User-Agent":"Mozilla/5.0"})
        h = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode("utf-8","ignore")
        if "没有与此相关的结果" in h or "No results" in h:
            return "未收录"
        nums = re.findall(r'([\d,]+)\s*(?:条|results)', h)
        return f"收录({nums[0] if nums else '?'})"
    except Exception as e:
        return f"ERR:{str(e)[:20]}"

for d in ["h2oiot.cn","whcome.com","51xyg.com","sonear.fit"]:
    s = check_sogou(d)
    b = check_bing(d)
    print(f"{d}: 搜狗={s} 必应={b}", flush=True)
    time.sleep(1.5)
