# -*- coding: UTF-8 -*-
import scrapy


class DoutuItem(scrapy.Item):
    # 定义抓取维度/字段
    img_url = scrapy.Field()
    name = scrapy.Field()
