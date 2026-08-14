def md5_hash(data):
    import hashlib
    return hashlib.md5(data.encode()).hexdigest()

tests = [('admin', '2d9d5942943a1323'), ('admin999', '79dca16741891333')]
for pw, expected in tests:
    # First 16 chars of MD5
    h = md5_hash(pw)[:16]
    match = 'MATCH' if h == expected else 'NO MATCH'
    print('MD5-first16('+ pw + '): ' + h + ' (expected ' + expected + ') -> ' + match)
    # Last 16 chars of MD5
    h = md5_hash(pw)[16:]
    match = 'MATCH' if h == expected else 'NO MATCH'
    print('MD5-last16('+ pw + '): ' + h + ' (expected ' + expected + ') -> ' + match)
    # MD5 dashes1
