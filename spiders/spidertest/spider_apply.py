# -*- coding: UTF-8 -*-
import sys
reload(sys)                      # reload 才能调用 setdefaultencoding 方法
sys.setdefaultencoding('utf-8')  # 设置 'utf-8'
import os
import requests
from scrapy.spiders import *
from scrapy.spiders.spidertest.spider_item_apply import DoutuItem

class DoutuSpider(Spider):
    name = "doutu"
    allowed_domains = ["doutula.com", "sinaimg.cn"]
    start_urls = ['https://www.doutula.com/photo/list/?page={}'.format(i) for i in range(1, 40)]

    # 重写父类parse方法，用于解析response对象的返回结果
    def parse(self, response):
        i = 0
        for content in response.xpath('//li[@class="list-group-item"]/div/div/a'):
            i += 1
            item = DoutuItem()
            url = content.xpath('//img/@data-original').extract()[i]
            arr = url.split('https://')
            len = arr.__len__()
            url = 'http:' + arr[0] if len == 1 else 'https://' + arr[1]

            item['img_url'] = url
            # item['img_url'] = content.xpath('//img/@data-original').extract()[i]
            item['name'] = content.xpath('//p/text()').extract()[i]
            try:
                # 创建存储爬虫结果的文件
                if not os.path.exists('doutu_download'):
                    os.makedirs('doutu_download')
                r = requests.get(item['img_url'])
                filename = 'doutu_download/'+item['name'] + item['img_url'][-4:]
                with open(filename, 'wb') as fo:
                    fo.write(r.content)
            except Exception as e:
                raise e

            yield item