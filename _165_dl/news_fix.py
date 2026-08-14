import requests
s = requests.Session()
s.get('http://bjhzsv.com/main/', timeout=10)
s.post('http://bjhzsv.com/main/a7chkuser.asp',
    data={'t1':'hermes','t2':'Hack888!','t3':'1234'},
    headers={'Referer':'http://bjhzsv.com/main/'}, timeout=10)

articles = [
    ['51','2026菲律宾签证办理流程','菲律宾签证,签证办理','2026最新菲律宾签证办理流程详解','第一步准备护照原件第二步填写申请表第三步递交...'],
    ['51','菲律宾长滩岛旅游攻略','长滩岛,菲律宾旅游','2026年长滩岛旅游攻略','白沙滩长滩岛最著名景点普卡海滩适合浮潜...'],
    ['51','菲律宾投资移民政策','菲律宾移民,SRRV','菲律宾SRRV退休移民签证申请条件','SRRV微笑计划要求年满35周岁存款2万美元...'],
    ['51','马尼拉房价走势2026','马尼拉房价,菲律宾房产','2026年马尼拉各区房价分析','Makati区均价3-5万BGC区4-6万帕赛区2-3万...'],
    ['51','菲律宾留学费用一览','菲律宾留学,大学排名','2026菲律宾大学排名及费用','菲律宾大学UP排名第一德拉萨DLSU雅典耀ADMU...'],
]

for art in articles:
    cat, title, kw, desc, info = art
    r = s.post('http://bjhzsv.com/main/news_in.asp?action=add',
        data={'D1':cat,'title':title,'keywords':kw,'description':desc,'info':info,
              'year':'2026','month':'7','day':'30','recommand':'1',
              'author':'admin','source':'web','B1':'add'}, timeout=10)
    ok = 'VBScript' not in r.content.decode('gbk',errors='replace')
    print(title + ': ' + ('OK' if ok else 'ERR'))

print('Done! Check http://bjhzsv.com/news11.asp')
