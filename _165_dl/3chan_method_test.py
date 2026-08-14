#!/usr/bin/env python3
"""3chan api.php - test GET param action + POST JSON"""
import urllib.request, urllib.parse, json, uuid

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(5000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:80]

def post_json(url, data, timeout=12):
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                     headers={**UA, "Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(5000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:80]

def post_form(url, data, timeout=12):
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(5000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(3000).decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:80]

# GET with action
print("GET ?action=post_thread:", get("http://3chan.net/api.php?action=post_thread"), flush=True)
# GET ?action=post
print("GET ?action=post:", get("http://3chan.net/api.php?action=post"), flush=True)
# POST form-encoded with action
print("POST form action=post_thread:", post_form("http://3chan.net/api.php", {"action": "post_thread", "board": "b"}), flush=True)
# POST JSON
print("POST json:", post_json("http://3chan.net/api.php", {"action": "post_thread", "board": "b"}), flush=True)
# GET root api.php
print("GET api.php:", get("http://3chan.net/api.php"), flush=True)
