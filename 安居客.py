import re
import logging
import random
import traceback

import requests
import pymysql
from faker import Factory
from bs4 import BeautifulSoup

start_url = 'https://www.anjuke.com/sy-city.html'
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


def write_to_mysql(city, name, address, huxing, price, price_around,  link):
    sql = 'insert into anjuke(city,  name, address, huxing, price, price_around,  link) values ("{}", "{}", "{}", "{}",\
     "{}", "{}", "{}")'.format(city, name, address, huxing, price, price_around,  link)
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


def start_request(url):
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    headers['referer'] = start_url
    for div in soup.select(r'div.city_list')[:-1:]:
        for a in div.select('a'):
            city = a.text
            href = a.get('href')
            try:
                parse_city(city, href)
            except Exception as e:
                traceback.print_exc()
                logging.warning(e)
                print('出错城市', city, href)


def parse_city(city, url):
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    li = soup.select(r'ul.L_tabsnew li')
    if li:
        link = li[1].select('a')[0].get('href')
    else:
        link = soup.select(r'ul.lp-navtabs.clearfix > li')[0].select('a')[0].get('href')
    print(city, link)
    parse_page(city, link)


def parse_page(city, url):
    response = requests.get(url, headers=headers, proxies=get_proxy()[-1])
    html = response.text
    soup = BeautifulSoup(html, 'lxml')

    for each in soup.select('div.key-list > div'):
        try:
            name = each.select('a.lp-name > h3 > span')[0].text
            link = each.select('a.lp-name')[0].get('href')
            address = each.select('a.address > span')[0].text
            huxing = '-'.join([x.text for x in each.select('a.huxing > span')])
            price = each.select('a.favor-pos > p')[0].text
        except Exception as e:
            logging.warning(e)
            print(each, url)
        try:
            price_around = each.select('a.favor-pos > p.favor-tag.around-price > span')[0].text
        except:
            price_around = 'null'
        write_to_mysql(city, name, address, huxing, price, price_around, link)
        # print(name, address, huxing, price, price_around, link, sep='\n', end='\n' + '*' * 100 + '\n')

    regex = re.compile(r'<a href="(.{1,100})" class="next-page next-link">下一页</a>')
    next_page = regex.findall(html)
    if next_page:
        headers['referer'] = url
        next_page_url = next_page[0]
        print('解析下一页：', next_page_url)
        parse_page(city, next_page_url)


if __name__ == '__main__':
    start_request(start_url)
    # parse_city('鞍山', 'https://anshan.anjuke.com/')
    # parse_city('北流', 'https://beil.fang.anjuke.com/')
    # parse_page('北京', 'https://bj.fang.anjuke.com')