import re
import time
import random

import requests
import pymysql


"""
抓取速度过快  账号会被限
需更新cookie信息
"""

headers = """Host: mp.weixin.qq.com
Accept-Encoding: br, gzip, deflate
Cookie: devicetype=iOS11.4.1; lang=zh_CN; pass_ticket=wbBCBKdO2l9nJeFADeamuMzMWFXgeixULeHMmeoMZpk=; version=16070227; wap_sid2=CKvk+TYSXF90RkZrZ0p1bHdPTnh1TllYbk51ZGw4ME5jQmNYb2RESTFNcW56V2gtMzczWjdZbks2ckIzRlIzU3hYY1ptajFNVFpFcGc0Ukc3bUJWNEprbC1xMnZNd0RBQUF+MKy3otwFOA1AlU4=; wxuin=115241515; RK=RCRBnFF1YT; pt2gguin=o0527439841; ptcz=6481a5818b1db6aff56ee2f0524dcc6716c68dd2ceb914c16c720fc3f8bac89f; pgv_pvid=4600968294; sd_cookie_crttime=1522933505177; sd_userid=7641522933505177
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15G77 MicroMessenger/6.7.2 NetType/WIFI Language/zh_CN
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA5OTE5NTI5Mw==&scene=126&devicetype=iOS11.4.1&version=16070227&lang=zh_CN&nettype=WIFI&a8scene=0&fontScale=100&pass_ticket=wbBCBKdO2l9nJeFADeamuMzMWFXgeixULeHMmeoMZpk%3D&wx_header=1
Accept-Language: zh-cn
X-Requested-With: XMLHttpRequest"""

headers = {each.split(':', 1)[0]: each.split(':', 1)[1].replace(' ', '', 1) for each in headers.split('\n')}

"""
河南交警公众号  offset 控制页数
url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzI1NDIzMDc3Mg==&f=json&offset=10&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=3qs3teMjvUrLPRZENHgssvM1e03UYDbmH1sR0825XQM%3D&wxtoken=&appmsg_token=971_Z6ytPbZPMZgZqEXGUpGRk_o3f0OvkGg-mnIE4w~~&x5=0&f=json'
# 微信读书公众号
url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA5OTE5NTI5Mw==&f=json&offset=30&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=3qs3teMjvUrLPRZENHgssvM1e03UYDbmH1sR0825XQM%3D&wxtoken=&appmsg_token=971_nNeS0vNGtOZZ2VyoK5wi4PTfX9lKL7dTu55ZoA~~&x5=0&f=json'
"""
# 微信读书公众号
start_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA5OTE5NTI5Mw==&f=json&offset={}&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=wbBCBKdO2l9nJeFADeamuMzMWFXgeixULeHMmeoMZpk%3D&wxtoken=&appmsg_token=972_W5Z7wV5rHdLQ6y%252FjH-3yvI5pB1tr3Ba_JWSSrg~~&x5=0&f=json'
num = 1
mysql_setting = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8',
    'db': 'spider'
}
conn = pymysql.connect(**mysql_setting)
cursor = conn.cursor()
execute = cursor.execute
sql = 'select ip, port, types from proxies limit 500'
execute(sql)
proxies = cursor.fetchall()


def get_proxy():
    proxy = random.choice(proxies)
    ip = proxy[0]
    port = proxy[1]
    types = proxy[2]
    proxy = '{}://{}:{}'.format(ip, port, types)
    proxy = {types: proxy}
    return (ip, port, types, proxy)


def get_link(url):
    global num
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1], verify=False)
    if response.status_code != 200:
        return False
    html = response.text
    # print(html)
    datas = re.sub(r'amp;', '', html)
    datas = re.sub(r'\\', '', datas)
    # print(datas)
    titles = re.findall(r'"title"\:(.*?),"digest"', datas)
    urls = re.findall(r'"content_url":(.*?),"source_url"', datas)
    if not(titles or urls):
        return False
    for title, url in zip(titles, urls):
        print(title)
        print(url)
        print('-' * 100)
    num += len(urls)
    time.sleep(random.uniform(2, 3))


def main():
    page_num = 0
    while True:
        url = start_url.format(page_num*10)
        headers['referer'] = url
        if get_link(url):
            break
        else:
            get_link(url)
            page_num += 1

    print('共抓取{}篇文章'.format(num))


if __name__ == '__main__':
    main()
