#!/usr/bin/env python3
"""批量查百度收录"""
import urllib.request, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check_baidu(domain):
    url = f"https://www.baidu.com/s?wd=site%3A{domain}&rn=10"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "BAIDUID=1234567890:FG=1"
    })
    try:
        r = urllib.request.urlopen(req, timeout=12, context=ctx)
        html = r.read().decode("utf-8","ignore")
        # 判断: 无结果 / 有结果
        if "没有找到该URL" in html or "没有找到相关结果" in html or "很抱歉，没有找到" in html:
            return "未收录"
        if "验证" in html and ("安全验证" in html or "百度安全验证" in html):
            return "验证码拦截"
        # 统计结果数
        nums = re.findall(r'百度为您找到相关结果约([\d,]+)个', html)
        if nums:
            return f"收录! 约{nums[0]}条"
        if "site:" in html and "结果" in html:
            return "有结果(数量未知)"
        if "百度快照" in html or "百度权重" in html:
            return "收录!(快照)"
        return f"未知(len={len(html)})"
    except Exception as e:
        return f"ERR:{str(e)[:30]}"

for d in ["h2oiot.cn", "whcome.com", "51xyg.com", "sonear.fit", "bldfw.com", "zoweunion.com", "holy58.com", "yoogakj.com", "wondfohealth.cn"]:
    r = check_baidu(d)
    print(f"{d}: {r}", flush=True)
    time.sleep(2)
