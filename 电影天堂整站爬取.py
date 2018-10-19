import re
import logging
import random
import threading
import multiprocessing as mul

import pymysql
import requests
from multiprocessing import Process,Pool
from selenium import webdriver
from faker import Factory
from bs4 import BeautifulSoup

"""
下载链接只有在浏览器中才显示，通过代码获取不到
考虑抓取效率，采用对phantomjs添加代理 多线程的方式，对详情页进行抓取
"""
# 初始请求头设置
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'http://www.dytt8.net',
    'Host': 'www.ygdy8.net',
    'Cookie': 'XLA_CI=3b136071541bcc977f724e408c6a426e'
}
# mysql设置
mysql_setting = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8',
    'db': 'spider'
}
# 存放详情页链接
link_dct = {}
num = 1

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


def get_links_selenium(url):
    global num
    service_args = [
        '--proxy={}'.format(get_proxy()[-1]),
        '--proxy-type={}'.format(get_proxy()[2]),
        '--load-images=no',
        '--disk-cache=yes',
        '--ignore-ssl-errors=true'
    ]
    driver = webdriver.PhantomJS(service_args=service_args)
    driver.get(url)
    html = driver.page_source
    # print(html)
    regex = re.compile(r'\"(thunder://.*)\"')
    links = regex.findall(html)
    soup = BeautifulSoup(html, 'lxml')
    names = [a.contents[0] for a in soup.select(r'table > tbody > tr > td > a')]
    for link, name in zip(links, names):
        write_to_mysql(types, name, link)
        print('第{}个链接：'.format(num), types, name, link, sep='\n')
        num += 1


def get_details(url):
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    html = response.text
    regex_link = re.compile('(ftp://.*)?')
    link = re

def write_to_mysql(types, names, link):
    sql = 'insert into dytt(types, name, url) values ("{}","{}","{}")'.format(types, names, link)
    execute(sql)
    conn.commit()


def parse_home():
    url = 'http://www.dytt8.net/'
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    response.encoding = 'gbk'
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    for a in soup.select('div.contain li a')[2:8:]:
        href = a.get('href')
        name = a.contents[0]
        if 'http' in href:
            link = href
        else:
            link = 'http://www.dytt8.net{}'.format(href)
        data[name] = link
    return data


def parse_movie(types, url):
    if types in link_dct:
        pass
    else:
        link_dct[types] = []
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    response.encoding = 'gbk'
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    for i in soup.select('table.tbspan b > a')[1::2]:
        href = i.get('href')
        link = 'http://www.ygdy8.net{}'.format(href)
        link_dct[types].append(link)
    # 找下一页链接
    regex = re.compile(r'<a href=\'(.*)\'>下一页</a>')
    try:
        next_page = regex.findall(html)[0]
        next_page_url = url.split('/')
        next_page_url[-1] = next_page
        next_page_url = '/'.join(next_page_url)
        print('查找下一页链接', next_page_url)
        headers['Referer'] = url
        parse_movie(types, next_page_url)
    except Exception as e:
        logging.warning(e)


if __name__ == '__main__':
    start_urls = parse_home()
    th_list_home = []
    for types, url in zip(start_urls, start_urls.values()):
        th = threading.Thread(target=parse_movie, args=(types, url))
        th_list_home.append(th)
    for th in th_list_home:
        th.start()
    for th in th_list_home:
        th.join()

    print(link_dct)

