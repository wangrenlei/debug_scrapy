# -*- coding: utf-8 -*-
import scrapy


class AaaSpider(scrapy.Spider):
    name = 'AAA'
    allowed_domains = ['aaa.com']
    start_urls = ['http://aaa.com/']

    def parse(self, response):
        pass
