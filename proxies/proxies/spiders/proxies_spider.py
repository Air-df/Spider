import scrapy
import logging

from bs4 import BeautifulSoup
from scrapy.cmdline import execute
from 爬虫.Spider.proxies.proxies.items import ProxiesItem
from 爬虫.Spider.proxies.proxies import settings


class Proxies(scrapy.Spider):
    name = 'proxy'
    start_urls = ['http://www.xicidaili.com/nn/{}'.format(page) for page in range(1, 100)]

    def __init__(self):
        super().__init__()
        self.headers = settings.DEFAULT_REQUEST_HEADERS

    def start_requests(self):
        for url in self.start_urls:
            self.headers['Referer'] = url
            yield scrapy.Request(url, headers=self.headers)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for info in soup.select(r'#ip_list tr'):
            item = ProxiesItem()
            try:
                item['ip'] = info.select(r'td')[1].text
                item['port'] = info.select(r'td')[2].text
                item['location'] = info.select(r'td a')[0].text
                item['types'] = info.select(r'td')[5].text
                item['life_time'] = info.select(r'td')[-2].text
                item['captcha_date'] = info.select(r'td')[-1].text
            except Exception as e:
                logging.warning(e)
                pass
            yield item


execute('scrapy crawl proxy'.split())