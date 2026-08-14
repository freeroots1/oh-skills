#!/usr/bin/env python3
"""爱站批量查百度收录"""
import urllib.request, ssl, re, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def check(domain):
    try:
        req = urllib.request.Request(f"https://www.aizhan.com/cha/{domain}/", headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        r = urllib.request.urlopen(req, timeout=12, context=ctx)
        html = r.read().decode("utf-8","ignore")
        # 找"百度收录"最近值 - 表格行: 日期 百度收录 百度反链...
        rows = re.findall(r'<td>(\d{4}-\d{2}-\d{2})</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td>', html)
        if rows:
            latest = rows[0]
            return f"收录={latest[1]} 反链={latest[2]} ({latest[0]})"
        # 权重表
        w = re.findall(r'百度：<a[^>]*>(\d+)</a>', html)
        if w:
            return f"百度权重={w[0]} (无收录明细)"
        return "无数据"
    except Exception as e:
        return f"ERR:{str(e)[:25]}"

for d in ["h2oiot.cn","whcome.com","51xyg.com","sonear.fit","bldfw.com","zoweunion.com","holy58.com","yoogakj.com","wondfohealth.cn"]:
    print(f"{d}: {check(d)}", flush=True)
    time.sleep(1.5)
