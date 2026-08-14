import requests

s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

# Delete old garbled categories first via menu_in.asp?action=del
# Category IDs for the garbled ones: menu system IDs from the sidebar
# Actually we need to find and delete them first

# Re-create with proper encoding - use requests with GB2312
categories = [
    ('26','菲律宾签证办理','菲律宾签证,签证办理,旅游签证'),
    ('27','菲律宾旅游攻略','长滩岛,菲律宾旅游,海岛游'),
    ('28','菲律宾投资移民','菲律宾移民,SRRV,退休签证'),
    ('29','菲律宾房产价格','马尼拉房价,菲律宾房产,投资'),
    ('30','菲律宾留学费用','菲律宾留学,大学排名,留学费用'),
]

articles = [
    ['26','菲律宾签证办理流程详解','菲律宾签证,签证办理,旅游签证',
     '2026最新菲律宾签证办理全攻略',
     '第一步准备护照原件，第二步填写签证申请表，第三步递交大使馆审核，第四步等待出签通知。旅游签证费用约300-800元，商务签证约800-1500元。加急办理3-5个工作日出签，普通办理7-10个工作日。'],
    ['27','菲律宾长滩岛旅游攻略2026','长滩岛,菲律宾旅游,海岛游',
     '2026年长滩岛最全旅游攻略',
     '长滩岛拥有世界闻名的白沙滩，全长4公里。推荐景点：星期五海滩、普卡海滩、卢霍山观景台。必体验项目：日落帆船、潜水、跳岛游、海鲜市场。旺季11月到次年5月，淡季6月到10月。'],
    ['28','菲律宾SRRV退休移民签证申请指南','菲律宾移民,SRRV签证,退休签证',
     '菲律宾SRRV退休移民签证全解析',
     'SRRV微笑计划要求申请人年满35周岁，在菲律宾银行存入2万美元。经典计划要求存款5万美元，可用于购买房产。两种计划均可携带配偶和21岁以下未婚子女，享受多次往返签证待遇。'],
    ['29','马尼拉房产投资分析2026','马尼拉房价,菲律宾房产,投资回报',
     '2026年马尼拉各区房产价格与投资分析',
     '马尼拉Makati金融区均价3-5万/平米，BGC国际城4-6万/平米，帕赛湾区2-3万/平米。公寓年租金回报率约6%-8%，相比国内一二线城市有明显优势。外国人可购买公寓，永久产权。'],
    ['30','菲律宾大学留学费用一览2026','菲律宾留学,大学排名,留学费用,英语游学',
     '2026年菲律宾大学排名及留学费用明细',
     '菲律宾大学UP综合排名第一，德拉萨大学DLSU商科强，雅典耀大学ADMU文科著名。本科年学费约2-4万人民币，硕士约3-5万。生活费每月约2000-3000元含住宿饮食。英语游学一个月约8000-12000元。'],
]

for art in articles:
    cat,title,kw,desc,info = art
    # Encode data in GB2312
    data_gbk = {
        'D1': cat.encode('gbk'),
        'title': title.encode('gbk'),
        'keywords': kw.encode('gbk'),
        'description': desc.encode('gbk'),
        'info': info.encode('gbk'),
        'year': b'2026', 'month': b'7', 'day': b'30',
        'recommand': b'1', 'author': 'admin'.encode('gbk'),
        'source': b'web', 'B1': b'add'
    }
    r = s.post('http://bjhzsv.com/main/news_in.asp?action=add',
        data=data_gbk, timeout=10)
    ok = 'VBScript' not in r.content.decode('gbk',errors='replace')
    print(title + ': ' + ('OK' if ok else 'ERR'))

# Now fix the category names via menu_in.asp
# First need to find correct category IDs in the menu system
r = s.get('http://bjhzsv.com/main/menu_add2.asp', timeout=10)
print('\nMenu IDs found - check page')
