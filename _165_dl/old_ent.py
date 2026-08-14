import socket, subprocess

domains = [
    'shanghaijichuang.com.cn','beijingjixie.com.cn','hubeijidian.com.cn',
    'jiangsuqizhong.com.cn','zhejiangzhoucheng.com.cn','guangdongdianji.com.cn',
    'sichuandianqi.com.cn','shandonggangtie.com.cn','henandianlan.com.cn',
    'tianjinjiancai.com.cn','chongqinggongcheng.com.cn','hunanjichuang.com.cn',
    'fujianyeya.com.cn','anhuijingmi.com.cn','hebeizhugang.com.cn',
    'shanxizhoucheng.com.cn','liaoningjixie.com.cn','hubeigangjiegou.com.cn',
    'shanghaidiangong.com','beijingjidian.com','guangzhoujixie.com',
    'hangzhoutool.com','wuhanmach.com','tianjinmotor.cn',
    'beijingzhugang.com','shanghaigangtie.com','guangzhouzhoucheng.com',
    'jiaxingjixie.com','nantongjidian.com','tangshanjichuang.com',
    'dongguandianji.com','zhongshanjidian.com','quanzhouqizhong.com',
]

found = []
for dom in domains:
    try:
        ip = socket.gethostbyname(dom)
        if ip:
            r = subprocess.run(['curl','-sk','--connect-timeout','3','--max-time','4',
                'http://'+dom,'-o','/dev/null','-w','%{http_code}:%{size_download}'],
                capture_output=True,text=True,timeout=5)
            code_size = r.stdout.strip()
            print(dom + ' [' + ip + '] ' + code_size)
            found.append(dom)
    except:
        pass

print('Found:', len(found))
