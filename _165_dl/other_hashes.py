import hashlib

targets = {'2d9d5942943a1323': 'admin', '79dca16741891333': 'admin999'}

# Try various hash formats on common passwords
pws = ['admin', 'admin999', 'password', '123456', 'test', 'admin123', 'bjhzsv', 'bjhzsv.com',
       'root', 'pass', 'admin9999', 'Admin', 'ADMIN']

print('=== Testing various hash algorithms on common passwords ===')
for pw in pws:
    # MD5
    md5h = hashlib.md5(pw.encode()).hexdigest()
    # SHA1
    sha1h = hashlib.sha1(pw.encode()).hexdigest()
    # SHA256
    sha256h = hashlib.sha256(pw.encode()).hexdigest()
    # CRC32
    import binascii
    crc32h = format(binascii.crc32(pw.encode()) & 0xffffffff, '08x')
    
    for name, h in [('MD5', md5h), ('SHA1', sha1h), ('SHA256', sha256h), ('CRC32', crc32h)]:
        if h[:16] in targets:
            print('MATCH: %s:%s -> %s (%s first-16)' % (targets[h[:16]], h[:16], pw, name))
        if h in targets.values():
            pass
    
    # Also check MD5 full
    if md5h[:16] in targets:
        print('MD5 MATCH: %s -> %s' % (pw, md5h[:16]))

print()
print('=== Trying direct hash of common passwords ===')
# Try first 16 of SHA256, SHA1, MD5
for pw in pws:
    for name, h in [('MD5', hashlib.md5(pw.encode()).hexdigest()[:16]),
                    ('SHA1', hashlib.sha1(pw.encode()).hexdigest()[:16]),
                    ('SHA256', hashlib.sha256(pw.encode()).hexdigest()[:16])]:
        if h in targets:
            print('FOUND: %s = %s (%s of %s)' % (targets[h], pw, name, pw))
