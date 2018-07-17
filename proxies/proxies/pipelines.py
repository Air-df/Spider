# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import random
import pymysql
import requests

from 爬虫.Spider.proxies.proxies import settings


class ProxiesPipeline(object):
    def __init__(self):
        self.headers = settings.DEFAULT_REQUEST_HEADERS

        dct = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '123456',
            'port': 3306,
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**dct)
        self.cursor = self.conn.cursor()
        self.excute = self.cursor.execute
        # 创建数据库
        self.excute('create database if not exists spider;')
        self.excute('use spider;')
        # 创建表
        sql = """create table if not exists proxies(
                    id int primary key auto_increment,
                    ip char(20),
                    port char(10),
                    location char(20),
                    types char(10),
                    life_time char(20),
                    captcha_date char(20)
                    );                      
                """
        self.excute(sql)

    # 检查ip是否有效
    def check_proxy(self, proxy, types):
        url_list = [
            'https://www.baidu.com',
            'http://tool.chinaz.com/pagestatus/',
            'https://www.douban.com/',
            'http://www.mtime.com/',
            'http://www.mtime.com/',
            'http://www.csdn.net',
            'http://www.163.com'
        ]
        # 从url列表中随机选取地址用于检测代理， 防止 集中访问被ban 导致检测失真
        url = random.choice(url_list)
        if types.lower() == 'http':
            response = requests.get(url, proxies={'http': proxy}, headers=self.headers, timeout=3)
        if types.lower() == 'https':
            response = requests.get(url, proxies={'https': proxy}, timeout=3)
        else:
            return None
        return response.status_code

    # 检查ip是否已入库
    def isexits(self, ip):
        self.excute('select ip from proxies where ip="{}"'.format(ip))
        result = self.cursor.fetchall()
        if result:
            return False
        else:
            return True

    def process_item(self, item, spider):
        ip = item['ip']
        port = item['port']
        types = item['types']
        life_time = item['life_time']
        proxy = types + '://' + ip + ':' + port
        if self.isexits(ip):
            # 注意条件 and 顺序
            if '天' in life_time and self.check_proxy(proxy, types) == 200:
                sql = """insert into proxies(ip, port, location, types, life_time, captcha_date) values 
                ("{}","{}","{}","{}","{}","{}");
                """.format(
                        item['ip'],
                        item['port'],
                        item['location'],
                        item['types'],
                        item['life_time'],
                        str(item['captcha_date'])
                    )
                print(sql)
                self.excute(sql)
                self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

