# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import pymongo


class Maoyantop100Pipeline(object):
    def __init__(self):
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
        sql = """create table if not exists maoyan(
            id int primary key auto_increment,
            title char(20),
            catogery char(30),
            content text(1000),
            comment text(2000),
            img_link char(100)
            );                      
        """
        self.excute(sql)

    def process_item(self, item, spider):
        sql = """insert into maoyan(title,catogery,content,comment,img_link) values 
            ("%s", "%s", "%s", "%s", "%s");
        """ % (''.join(item['title']), ''.join(item['catogery']), ''.join(item['content']), ''.join(item['comment'][0]), ''.join(item['img_link']))
        self.excute(sql)
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
