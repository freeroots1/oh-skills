import requests

s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

# Bulk create Chinese SEO articles per category
seo_data = {
    '26': [
        ['菲律宾签证办理流程2026', '菲律宾签证,签证办理流程,菲律宾旅游签证', '2026年最新菲律宾签证办理流程详解', '第一步准备护照原件...第二步填写申请表...第三步递交大使馆...第四步等待出签...'],
        ['菲律宾商务签证所需材料', '菲律宾商务签,签证材料,商务签证办理', '菲律宾商务签证所需材料清单及办理周期', '1.护照原件2.两寸白底照片3.在职证明4.邀请函5.机票订单...'],
        ['菲律宾旅游签证可以停留多久', '菲律宾旅游签证,停留时间,签证延期', '菲律宾旅游签证停留期限及延期办理指南', '菲律宾旅游签一般为30天停留期，可延期至59天...'],
    ],
    '27': [
        ['菲律宾长滩岛必去景点推荐', '长滩岛,菲律宾旅游,海岛旅游', '2026年长滩岛最全旅游攻略及必玩景点推荐', '白沙滩是长滩岛最著名的景点...普卡海滩适合浮潜...'],
        ['菲律宾马尼拉自由行攻略', '马尼拉旅游,菲律宾自由行,马尼拉景点', '马尼拉三日自由行完整攻略含交通住宿', '市中市Intramuros是马尼拉最古老的城区...黎刹公园...'],
        ['菲律宾宿务薄荷岛旅游指南', '宿务旅游,薄荷岛,菲律宾海岛', '宿务+薄荷岛5天4晚旅游路线推荐', '第一天到达宿务市区游览...第二天乘船到薄荷岛...'],
    ],
    '28': [
        ['菲律宾SRRV退休移民签证详解', '菲律宾移民,SRRV签证,退休移民', '菲律宾SRRV退休移民签证申请条件及办理费用', 'SRRV微笑计划要求申请人年满35周岁...存款2万美元...'],
        ['菲律宾投资移民最新政策2026', '菲律宾投资移民,SIRV签证,移民政策', '2026年菲律宾投资移民SIRV签证新政策解读', 'SIRV投资移民签证需投资7.5万美元...可带配偶子女...'],
        ['菲律宾移民买房可以获得永居吗', '菲律宾移民,买房移民,永久居留', '在菲律宾买房可以移民吗？最新政策分析', '菲律宾目前没有买房直接移民政策...但可通过SRRV实现...'],
    ],
    '29': [
        ['马尼拉房产价格走势分析2026', '马尼拉房价,菲律宾房产,房产投资', '2026年马尼拉各区房产价格及投资回报率分析', 'Makati区均价3-5万/平米...BGC区4-6万/平米...'],
        ['外国人在菲律宾买房流程', '菲律宾买房,外国人购房,房产流程', '外国人购买菲律宾房产的完整流程及注意事项', '外国人只能购买公寓Condo...不能购买土地...'],
        ['菲律宾宿务房产投资分析', '宿务房产,菲律宾投资,房产升值', '宿务房产投资前景及租金回报率详解', '宿务作为菲律宾第二大城市...房产升值空间大...'],
    ],
    '30': [
        ['菲律宾大学排名及留学费用', '菲律宾留学,大学排名,留学费用', '2026年菲律宾Top10大学排名及各校留学费用一览', '菲律宾大学UP排名第一...德拉萨大学DLSU...'],
        ['菲律宾英语游学多少钱一个月', '菲律宾游学,英语培训,游学费用', '菲律宾英语游学一个月费用明细含学费住宿', '斯巴达式英语学校一个月学费约800-1200美元...'],
        ['中国学生去菲律宾留学需要什么条件', '菲律宾留学,留学条件,中国留学生', '中国学生申请菲律宾大学的条件和流程指南', '高中毕业即可申请...需要毕业证成绩单公证件...'],
    ],
}

count = 0
for cat_id, articles in seo_data.items():
    for title, kw, desc, info in articles:
        r = s.post(
            'http://bjhzsv.com/main/news_in.asp?action=add',
            data={
                'D1': cat_id, 'title': title, 'keywords': kw,
                'description': desc, 'info': info,
                'year': '2026', 'month': '7', 'day': '30',
                'recommand': '1', 'author': 'admin', 'source': '本站',
                'B1': 'add'
            },
            timeout=10
        )
        text = r.content.decode('gbk', errors='replace')
        ok = 'VBScript' not in text
        count += 1
        print('[%s/%s] %s: %s' % (cat_id, title[:30], 'OK' if ok else 'ERR', text[:60] if not ok else ''))

print('\n=== TOTAL: %d articles created ===' % count)
print('\n====== FINAL SEO PAGES ======')
for cid, articles in seo_data.items():
    r = requests.get('http://bjhzsv.com/class1_index.asp?id=' + cid, timeout=5)
    print('\nhttp://bjhzsv.com/class1_index.asp?id=%s (%dB)' % (cid, len(r.text)))
