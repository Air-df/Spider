import time
import json
import random
import threading

import pymysql
import requests
from faker import Factory
from bs4 import BeautifulSoup

# 必须附带cookie，没有cookie返回的数据为重复数据
HEADERS = {
    'Cookie': '_T_WM=5d1bd420e8679cba48cfbe5d39e885cd; WEIBOCN_FROM=1110006030; MLOGIN=0; '
              'M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803_ctg1_4288_-_ctg1_4288%26fid%3D102803_ctg1_4288_'
              '-_ctg1_4288%26uicode%3D10000011',
    'User-Agent': Factory().create().user_agent(),
}

MYSQL = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'spider',
        'charset': 'utf8'
    }

# 入口链接
START_STR = """新闻
https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0&page=
搞笑
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_4388_-_ctg1_4388&openApp=0&since_id=
情感
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_1988_-_ctg1_1988&openApp=0&since_id=
明星
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_4288_-_ctg1_4288&openApp=0&since_id=
社会
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_4188_-_ctg1_4188&openApp=0&since_id=
数码
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_5088_-_ctg1_5088&openApp=0&since_id=
体育
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_1388_-_ctg1_1388&openApp=0&since_id=
汽车
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_5188_-_ctg1_5188&openApp=0&since_id=
电影
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_3288_-_ctg1_3288&openApp=0&since_id=
游戏
https://m.weibo.cn/api/container/getIndex?containerid=102803_ctg1_4888_-_ctg1_4888&openApp=0&since_id="""

lst = START_STR.split('\n')
START_DICT = {lst[x]: lst[x+1] for x in range(len(lst)) if x % 2 == 0}

COUNT = 0


# 从数据库中随机抽取代理
def get_proxies():
    conn = pymysql.connect(**MYSQL)
    cursor = conn.cursor()
    excute = cursor.execute
    excute('select ip, port, types from proxies limit {},1'.format(random.randint(1, 850)))
    conn.commit()
    result = cursor.fetchall()
    return result


def get_info(url):
    global COUNT
    proxy = random.choice(get_proxies())
    proxy_ip = proxy[0]
    proxy_port = proxy[1]
    proxy_type = proxy[2]
    response = requests.get(url, headers=HEADERS, proxies={proxy_type: proxy_ip + ':' + proxy_port})
    response.encoding = 'utf-8'
    data = json.loads(response.text)
    blogs = data['data']['cards']

    # 解析json数据
    for blog in blogs:
        try:
            title_html = blog['mblog']['text']
            soup = BeautifulSoup(title_html, 'lxml')
            title = soup.text                                           # 微博名称
            pic_link = blog['mblog']['bmiddle_pic']                     # 微博图片链接
            user_name = blog['mblog']['user']['screen_name']            # 博主名称
            user_link = blog['mblog']['user']['profile_url']            # 博主链接
            followers_count = blog['mblog']['user']['followers_count']  # 博主粉丝数量
            comment_counts = blog['mblog']['comments_count']            # 评论数量
            print(title, user_name, followers_count, comment_counts, pic_link, user_link, sep='\n')
            # 统计抓取数量
            COUNT += 1
        except Exception as e:
            print(e)
            continue
        print('我是分割线'.center(150, '*'))


def go(url):
    urls = [url + str(page) for page in range(1, 40)]
    for link in urls:
        time.sleep(random.uniform(3, 5))
        get_info(link)


def main():
    th_list = []

    for type in START_DICT:
        th = threading.Thread(target=go, args=(START_DICT[type],))
        th_list.append(th)
        th.start()

    for th in th_list:
        th.join()

    print(COUNT)

if __name__ == '__main__':
    main()
