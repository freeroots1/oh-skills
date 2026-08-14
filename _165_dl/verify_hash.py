def mysql_old_password(password):
    nr = 1345345333
    add = 7
    nr2 = 0x12345671
    for c in password:
        if c == " " or c == "\t":
            continue
        byte = ord(c)
        nr ^= (((nr & 63) + add) * byte) + (nr << 8)
        nr2 += (nr2 << 8) ^ nr
        add += byte
    nr &= 0x7fffffff
    nr2 &= 0x7fffffff
    return "%08lx%08lx" % (nr, nr2)

# Test with known strings
tests = ["test", "password", "admin", "admin123", "abc", "123456"]
for t in tests:
    print("%s -> %s" % (t, mysql_old_password(t)))
