gb = "密码错误".encode("gb2312")
hex_str = " ".join(f"\x{b:02x}" for b in gb)
print("GB2312 bytes:", hex_str)
print("As string:", gb)
