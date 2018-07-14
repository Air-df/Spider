import scrapy
# 调用 excute 在IDE 中执行终端命令
from scrapy.cmdline import execute
from 爬虫.Spider.maoYanTop100.maoYanTop100.items import Maoyantop100Item


class MaoYanSpider(scrapy.Spider):
    name = 'maoyan'

    # allowed_domains = ['maoyan.com']
    # start_urls = ['http://maoyan.com/board/4?offset={}'.format(i * 10) for i in range(10)]

    def __init__(self):
        super().__init__()
        self.allowed_domains = ['maoyan.com']
        self.start_urls = ['http://maoyan.com/board/4?offset={}'.format(i * 10) for i in range(10)]

    def start_requests(self):
        for i in self.start_urls:
            yield scrapy.Request(i)

    def parse(self, response):
        for i in response.xpath('//dl[@class="board-wrapper"]/dd/a/@href'):
            yield scrapy.Request(url='http://maoyan.com{}'.format(i.extract()), callback=self.parse_page,
                                 dont_filter=True)

    def parse_page(self, response):
        item = Maoyantop100Item()
        item['title'] = response.xpath('//div[@class="movie-brief-container"]/h3/text()').extract()
        item['catogery'] = response.xpath('//div[@class="movie-brief-container"]/ul/li[1]/text()').extract()
        item['score'] = response.xpath('/html/body/div[3]/div/div[2]/div[3]/div[1]/div/span/span/text()').extract()
        item['content'] = response.xpath('//div[@class="mod-content"]/span/text()').extract()
        item['comment'] = response.xpath('//div[@class="comment-content"]/text()')[:2:].extract()
        item['img_link'] = response.xpath('//div[@class="avatar-shadow"]/img/@src').extract()

        # print(item['title'], item['catogery'], item['score'], item['content'], item['comment'], item['img_link'],
        #       sep='\n')

        yield item


"""
pipeline 中存储到Mysql， MongoDB
存储为xml文件
"""
# execute(['scrapy', 'crawl', 'maoyan', '-o', 'maoyan.xml'])
execute(['scrapy', 'crawl', 'maoyan'])
