# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProxiesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    location = scrapy.Field()
    types = scrapy.Field()
    life_time = scrapy.Field()
    captcha_date = scrapy.Field()