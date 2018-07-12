import time
import threading

from faker import Factory
import requests
from bs4 import BeautifulSoup

"""
本文件用于爬取豆瓣最受欢迎影评
    目标网址： https://movie.douban.com/review/best/
"""

header_str = """Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Connection:keep-alive
Cookie:bid=zUnnS0B0U9g; __utma=30149280.816511805.1531056340.1531056340.1531056340.1; __utmc=30149280; __utmz=30149280.1531056340.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); regpop=1; ll="108303"; dbcl2="58779916:xR1xY1FkYOg"; _ga=GA1.2.816511805.1531056340; _gid=GA1.2.1650676679.1531057970; ck=JfsN; push_noty_num=0; push_doumail_num=0; __utmv=30149280.5877; __utmt=1; __utmb=30149280.13.9.1531058600473; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1531058604%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=223695111.816511805.1531056340.1531058604.1531058604.1; __utmb=223695111.0.10.1531058604; __utmc=223695111; __utmz=223695111.1531058604.1.1.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_id.100001.4cf6=2148c6bfad0f7599.1531058604.1.1531058611.1531058604.
Host:movie.douban.com
Referer:https://movie.douban.com/
Upgrade-Insecure-Requests:1"""

UA = Factory().create().user_agent()
headers = {x.split(':', 1)[0]: x.split(':', 1)[1] for x in header_str.split('\n')}
headers['User-Agent'] = UA
# cookies = {
#     'cookie': """bid=zUnnS0B0U9g; _pk_ses.100001.8cb4=*; __yadk_uid=8LC6kAjG8bOXxJakLewkeX6SyeImnQ3y;
#     __utma=30149280.816511805.1531056340.1531056340.1531056340.1; __utmc=30149280;
#     __utmz=30149280.1531056340.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); regpop=1; ll="108303"; __utmt=1;
#     dbcl2="58779916:xR1xY1FkYOg"; _ga=GA1.2.816511805.1531056340; _gid=GA1.2.1650676679.1531057970;
#     _gat_UA-7019765-1=1; ck=JfsN; _pk_id.100001.8cb4=ee0e339e85c6b828.1531056332.1.1531057974.1531056332.;
#     push_noty_num=0; push_doumail_num=0; __utmv=30149280.5877; __utmb=30149280.7.9.1531057979861"""}

# 存放不规则页面网址

wrong_link_list = []

# 获取每页链接
def get_url(ur):
    global headers, cookies
    response = requests.get(ur, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.select(r'div.main-bd > h2 > a')
    for i in links:
        yield i.get('href')


# 获取影评内容
def get_coment(url):
    global header, wrong_link_list
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    name = soup.select('header.main-hd > a ')[1].contents[0]
    title = soup.select('div.article > h1 > span')[0].contents[0]

    try:
        content = ''.join([x.contents[0] for x in soup.select('p')[2::]])
        print(url, '电影名称:%s\n文章标题:%s\n评论内容:%s\n' % (name, title, content), sep='\n')
    except Exception:
        wrong_link_list.append(url)


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