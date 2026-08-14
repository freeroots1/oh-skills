def crc64_ecma(data):
    crc = 0
    poly = 0xC96C5795D7870F42
    for byte in data:
        crc ^= (byte << 56)
        for _ in range(8):
            if crc & (1 << 63):
                crc = ((crc << 1) ^ poly) & 0xFFFFFFFFFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFFFFFFFFFF
    return '{:016x}'.format(crc)

tests = [('admin', '2d9d5942943a1323'), ('admin999', '79dca16741891333')]
for pw, expected in tests:
    h = crc64_ecma(pw.encode())
    match = 'MATCH' if h == expected else 'NO MATCH'
    print('CRC64-ECMA({}): {} (expected {}) -> {}'.format(pw, h, expected, match))
