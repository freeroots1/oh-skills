import requests
s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

articles = [
    ['26','2026菲律宾签证办理流程详解','菲律宾签证,签证办理','2026最新菲律宾签证办理全攻略','护照原件准备-填写申请表-递交大使馆-出签-300至1500元'],
    ['27','菲律宾长滩岛旅游攻略2026','长滩岛,菲律宾旅游','2026长滩岛最全旅游攻略','白沙滩-普卡海滩-潜水-日落帆船-海鲜市场'],
    ['28','菲律宾SRRV退休移民签证申请','菲律宾移民,SRRV','菲律宾SRRV退休移民签证全解析','年满35岁-存款2万美元-微笑计划-可带配偶子女'],
    ['29','2026马尼拉房产价格走势','马尼拉房价,菲律宾房产','2026马尼拉房产市场分析','Makati均价3至5万-BGC4至6万-帕赛2至3万-年租金回报率百分之六至八'],
    ['30','菲律宾留学费用一览表2026','菲律宾留学,大学排名','2026菲律宾大学留学费用明细','菲律宾大学UP-德拉萨DLSU-雅典耀ADMU-学费2至5万每年-生活费2000每月'],
]

for art in articles:
    cat,title,kw,desc,info = art
    r = s.post('http://bjhzsv.com/main/news_in.asp?action=add',
        data={'D1':cat,'title':title,'keywords':kw,'description':desc,'info':info,
              'year':'2026','month':'7','day':'30','recommand':'1',
              'author':'admin','source':'web','B1':'add'}, timeout=10)
    ok = 'VBScript' not in r.content.decode('gbk',errors='replace')
    print(cat, title[:30], 'OK' if ok else 'ERR')

print('Done! Check: http://bjhzsv.com/class1_index.asp?id=26')
