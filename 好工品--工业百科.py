import re
import time
import random
import traceback

import requests
import pymysql
import pymongo
from bs4 import BeautifulSoup
from faker import Factory

# 入口网址
start_url = 'https://www.51hgp.com/Standard?page=1#good-style'
# 基础链接--用于生成详情页链接
base_url = 'https://www.51hgp.com/Standard/Specifications/'
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referrer': 'https://www.51hgp.com/Standard'
}


def get_proxies():
    mysql = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'spider',
        'charset': 'utf8'
    }
    conn = pymysql.connect(**mysql)
    cursor = conn.cursor()
    cursor.execute('select ip, port, types from proxies limit 500')
    proxies = cursor.fetchall()
    cursor.close()
    conn.close()
    return proxies


proxies = get_proxies()


def get_proxy():
    proxy = random.choice(proxies)
    ip = proxy[0]
    port = proxy[1]
    types = proxy[2]
    proxy = '{}://{}:{}'.format(ip, port, types)
    proxy = {types: proxy}
    return proxy


def get_links(url):
    res = requests.get(url, headers=headers, proxies=get_proxy())
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    headers['Referrer'] = url

    for item in soup.select('ul.catalogueResultList > li'):
        detail_url = base_url + item.get('data-lead-standardid')
        print(detail_url)
        # 生成表头
        table_head = get_table_head_from(detail_url)
        get_detail_from(detail_url)


def get_table_head_from(url):
    res = requests.get(url, headers=headers, proxies=get_proxy())
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    head_str = '标准、大类、小类、直径、材质、强度、材料、表面处理'
    table_head = head_str.split('、')
    # 表头
    for head in soup.select('thead.product-list-head th')[:-1:]:
        content = head.contents[0]
        table_head.append(content)
    # print(table_head)
    return table_head


def get_detail_from(url):
    base = 'https://www.51hgp.com'      # 用于生成下一页链接
    res = requests.get(url, headers=headers, proxies=get_proxy())
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    get_info(soup)
    next_page = soup.select('div#page a')[-2].get('href')

    # if 'Standard' in next_page:
    #     next_page_url = base + next_page
    #     print(next_page_url)
    #     get_detail_from(next_page_url)


def get_info(soup):
    standard = soup.select('div.crumbs a')[2].contents[0]
    big_catogery = ''.join(soup.select('div.crumbs a')[1].contents[0].split())
    small_catogery = soup.select('div.screening-top')[1].select('span')[0].contents[0]
    table = soup.select('table.screening tr')
    # 直径
    diameter = table[0].select('td')[1].select('div.overflow-box > a')[0].contents[0]
    # 材质
    texture = table[1].select('td')[1].select('div.overflow-box > a')[0].contents[0]
    # 强度
    intention = table[2].select('td')[1].select('div.overflow-box > a')[0].contents[0]
    # 材料
    material = table[3].select('td')[1].select('div.overflow-box > a')[0].contents[0]
    # 表面处理
    surface_treatment = table[4].select('td')[1].select('div.overflow-box > a')[0].contents[0]
    print(standard, big_catogery, small_catogery, diameter, texture, intention, material, surface_treatment, sep='\n')



def main():
    for i in range(1, 553):
        url = 'https://www.51hgp.com/Standard?page={}#good-style'.format(i)
        get_links(url)


if __name__ == '__main__':
    # get_links(start_url)
    # 详情页测试链接
    test_url = 'https://www.51hgp.com/Standard/Specifications/614'
    # get_detail_from(test_url)
    # get_table_head_from('https://www.51hgp.com/Standard/Specifications/30914')
    main()