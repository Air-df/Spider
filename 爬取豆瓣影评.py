import time
import random
import threading

import requests
import pymongo
from faker import Factory
from bs4 import BeautifulSoup

"""
本文件用于爬取豆瓣最受欢迎影评
    目标网址： https://movie.douban.com/review/best/
"""

header_str = """Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Connection:keep-alive
Host:movie.douban.com
Referer:https://movie.douban.com/
Upgrade-Insecure-Requests:1"""

UA = Factory().create().user_agent()
headers = {x.split(':', 1)[0]: x.split(':', 1)[1] for x in header_str.split('\n')}
headers['User-Agent'] = UA

# 存放不规则页面网址
WRONG_LINK_LIST = []

# 创建连接到MongoDB
HOST = 'localhost'
PORT = 27017
CONN = pymongo.MongoClient(HOST, PORT)
DB = CONN['spider']
COLLECTION_NAME = 'doubanmovie'
COLLECTION = DB[COLLECTION_NAME]


# 获取每页链接
def get_url(ur):
    response = requests.get(ur, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.select(r'div.main-bd > h2 > a')
    for i in links:
        yield i.get('href')


# 获取影评内容
def get_coment(url):
    time.sleep(random.uniform(0.5, 3))
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    name = soup.select('header.main-hd > a ')[1].contents[0]
    title = soup.select('div.article > h1 > span')[0].contents[0]

    try:
        content = ''.join([x.contents[0] for x in soup.select('p')[2::]])
        # 查看数据库中是否已存在
        isexists = COLLECTION.find({'name': name}, {'_id': 0}).count()
        if not isexists:
            dct = {
                'name': name,
                'title': title,
                'content': content
            }
            COLLECTION.insert(dct)
    except Exception as e:
        WRONG_LINK_LIST.append(url)


# 主事件循环
def main():
    a = time.time()
    link_list = []
    for i in range(5):
        url = 'https://movie.douban.com/review/best/?start=' + str(20 * i)
        for i in get_url(url):
            link_list.append(i)

    # 线程池
    th_list = []
    for i in link_list:
        th = threading.Thread(target=get_coment, args=(i,))
        th_list.append(th)

    sem = threading.Semaphore(80)
    for i in th_list:
        with sem:
            i.start()

    for i in th_list:
        i.join()
    b = time.time()
    CONN.close()


if __name__ == '__main__':
    main()
    for i in WRONG_LINK_LIST:
        print('出错网址:', i)