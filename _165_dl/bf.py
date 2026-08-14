import hashlib
target = '2d9d5942943a1323'
for i in range(1000000):
    pwd = str(i).zfill(6)
    h = hashlib.md5(pwd.encode()).hexdigest()[:16]
    if h == target:
        print(f'CRACKED admin: {pwd}')
        exit(0)
print('Not found in 0-999999')
