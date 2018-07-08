import time
import requests
import threading
from bs4 import BeautifulSoup

"""
本文件用于爬取豆瓣最受欢迎影评
    目标网址： https://movie.douban.com/review/best/
"""

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 '
                  'Safari/537.36 Core/1.53.5048.400 QQBrowser/9.7.13114.400'
}

# 存放不规则页面网址
wrong_link_list = []


# 获取每页链接
def get_url(ur):
    global header
    response = requests.get(ur, headers=header)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.select(r'div.main-bd > h2 > a')
    for i in links:
        yield i.get('href')


# 获取影评内容
def get_coment(url):
    global header, wrong_link_list
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'lxml')

    name = soup.select('header.main-hd > a ')[1].contents[0]
    title = soup.select('div.article > h1 > span')[0].contents[0]

    try:
        content = ''.join([x.contents[0] for x in soup.select('p')[2::]])
        print(url, '电影名称:%s\n文章标题:%s\n评论内容:%s\n' % (name, title, content), sep='\n')
    except Exception:
        wrong_link_list.append(url)
        raise


# 主事件循环
def main():
    a = time.time()
    print('开始。。。')
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
    print('结束.....')
    print('用时：', b - a)


if __name__ == '__main__':
    main()
    for i in wrong_link_list:
        print('出错网址:', i)
