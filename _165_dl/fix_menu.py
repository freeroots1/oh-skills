import requests

s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

# Delete old garbled categories first - look for them in menu list
r = s.get('http://bjhzsv.com/main/menu_add2.asp', timeout=10)
t = r.content.decode('gbk', errors='replace')

# Find garbled categories by looking for "paixu=1" pattern
import re
# menu_edit2.asp?id=XX links
ids = re.findall(r"menu_edit2\.asp\?id=(\d+)", t)
print("Existing menu IDs:", ids)

# Try to delete garbled ones by finding the right IDs
# Then re-create with proper GB2312 encoding
# Use explicit GB2312 form encoding
categories = [
    '菲律宾签证办理',
    '菲律宾旅游攻略',
    '菲律宾投资移民',
    '菲律宾房产价格', 
    '菲律宾留学费用',
]

for name in categories:
    # Post with GB2312 encoded data and correct charset header
    r = s.post('http://bjhzsv.com/main/menu_in.asp?action=add',
        data={
            'classname': name.encode('gb2312'),
            'paixu': '1',
            'upid': '0',
            'auct': '1',
            'B1': 'add'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=gb2312'},
        timeout=10)
    ok = '成功' in r.content.decode('gbk', errors='replace')
    print(name + ': ' + ('OK' if ok else r.content.decode('gbk',errors='replace')[:60]))

print('Done')
