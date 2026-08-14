import hashlib
targets = {'2d9d5942943a1323': 'admin', '79dca16741891333': 'admin999'}
# Try numeric passwords from 10000 to 99999
for i in range(10000, 100000):
    pwd = str(i)
    h = hashlib.md5(pwd.encode()).hexdigest()[:16]
    for target, user in targets.items():
        if h == target:
            print(f'CRACKED! {user}: password={pwd}')
            exit(0)
# Try 5-digit with prefixes
for prefix in ['a', 'A', 'p', 'P', 'u', 'U']:
    for i in range(1000, 10000):
        pwd = prefix + str(i)
        h = hashlib.md5(pwd.encode()).hexdigest()[:16]
        for target, user in targets.items():
            if h == target:
                print(f'CRACKED! {user}: password={pwd}')
                exit(0)
print('Not found')
