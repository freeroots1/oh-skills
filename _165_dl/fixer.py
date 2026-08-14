import sys
f = open("/tmp/cn_urllib.py", "r")
c = f.read()
f.close()
c = c.replace('PASSWORDS_FILE="***"', 'PASSWORDS_FILE="/tmp/pwds.txt"')
f = open("/tmp/cn_urllib.py", "w")
f.write(c)
f.close()
print("Fixed")
