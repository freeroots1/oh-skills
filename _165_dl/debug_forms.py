#!/usr/bin/env python3
"""Debug: check login form field detection on target sites"""
import requests
import urllib3
import re

urllib3.disable_warnings()
s = requests.Session()
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

targets = [
    'http://chn-top.cn/admin/login',
    'http://sdmj.com.cn/login',
    'http://yurundianqi.com/admin.php?s=/Login/index',
    'http://chinanaisi.com/admin/login',
    'http://cn-hunters.com/admin.php',
    'http://joyalltire.com/login',
    'http://hebeihuajiu.com/admin/',
    'http://shimingchina.com/admin/',
    'http://fzmetal.com/admin/',
    'http://joyalltire.cn/login',
]

for url in targets:
    try:
        r = s.get(url, timeout=8, verify=False, headers=h, allow_redirects=True)
        html = r.text
        print(f"URL: {url}")
        print(f"  Status: {r.status_code} Final: {r.url} Size: {len(html)}")
        
        # Find password fields
        pw_matches = re.findall(r'type=["\']password["\']', html, re.I)
        print(f"  Password type fields: {len(pw_matches)}")
        
        # Find all input elements with name attrs
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*type=["\']([^"\']+)["\']', html, re.I)
        inputs2 = re.findall(r'<input[^>]*type=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\']', html, re.I)
        
        all_inputs = {}
        for name, typ in inputs:
            all_inputs[name] = typ
        for typ, name in inputs2:
            all_inputs[name] = typ
        
        print(f"  Form inputs: {all_inputs}")
        
        # Check for form element
        form_matches = re.findall(r'<form[^>]*action=["\']([^"\']+)["\']', html, re.I)
        print(f"  Form actions: {form_matches}")
        
        # Check for captcha
        has_captcha = bool(re.search(r'(captcha|verify|验证码|verification)', html, re.I))
        print(f"  Has captcha: {has_captcha}")
        print()
    except Exception as e:
        print(f"URL: {url} ERROR: {e}")
        print()
