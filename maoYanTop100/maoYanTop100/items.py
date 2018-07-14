# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Maoyantop100Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    catogery = scrapy.Field()
    score = scrapy.Field()
    content = scrapy.Field()
    comment = scrapy.Field()
    img_link = scrapy.Field()