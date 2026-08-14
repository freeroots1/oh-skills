import sys
content = open("/tmp/cn_urllib.py", "r").read()
content = content.replace('PASSWORDS_FILE="***"', 'PASSWORDS_FILE = "/tmp/pwds.txt"')
open("/tmp/cn_urllib.py", "w").write(content)
print("Fixed")
