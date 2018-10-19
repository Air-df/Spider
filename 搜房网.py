import re
import logging
import random

import requests
import pymysql
from faker import Factory
from bs4 import BeautifulSoup

start_url = 'http://www.fang.com/SoufunFamily.htm'
headers = {
    'User-Agent': Factory().create().user_agent()
}

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


def write_to_mysql(city='null', title='null', detail='null', price='null'):
    sql = 'insert into soufang(city, title, detail, price) values ("{}", "{}", "{}", "{}")'.format(
        city, title, detail, price
    )
    execute(sql)
    conn.commit()


def get_proxy():
    proxy = random.choice(proxies)
    ip = proxy[0]
    port = proxy[1]
    types = proxy[2]
    proxy = '{}://{}:{}'.format(ip, port, types)
    proxy = {types: proxy}
    return (ip, port, types, proxy)


def start_request():
    response = requests.get(start_url, headers=headers, proxies=get_proxy()[-1])
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    for a in soup.select(r'table#senfe a')[46:-16:]:
        url = a.get('href')
        city = a.contents[0]
        try:
            parse_city(url, city)
        except Exception as e:
            logging.warning(e)
            print(city, url)


def parse_city(url, city):
    headers['referer'] = start_url
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    response.encoding = 'gbk'
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    try:
        link = soup.select(r'div#dsy_D01_04 a')[0].get('href')
        print(city)
    except:
        link = soup.select(r'div#dsy_H01_05 a')[0].get('href')
        print(city)
    parse_page(link, city)


def parse_page(url, city):
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    response.encoding = 'gbk'
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    for each in soup.select('div.houseList dd'):
        title = each.select('p')[0].select('a')[0].contents[0]
        link = url.split('/house', 1)[0] + each.select('p')[0].select('a')[0].get('href')
        detail = each.select('p')[1].text + ''.join([x.contents[0] for x in each.select('p')[1].select('span')])
        detail = ''.join(detail.replace('|', '-').split())
        price = each.select('p')[-1].select('span')[0].contents[0]
        write_to_mysql(city, title, detail, price)
    regex = re.compile(r'<a href="(/\w*/i\d{1,4}/)">下一页</a>')
    next_page = regex.findall(html)
    if next_page:
        next_page_url = url.split('/house', 1)[0] + next_page[0]
        headers['referer'] = url
        parse_page(next_page_url, city)
        print(next_page_url)


if __name__ == '__main__':
     start_request()
     cursor.close()
     conn.close()
     # parse_city('http://cq.fang.com/')
     #  parse_page('http://fz.zu.fang.com/house/i3100/')
