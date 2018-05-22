# 爬虫管理器等同于爬虫加载器
"""
Backwards compatibility shim. Use scrapy.spiderloader instead.
"""
from spiderloader import SpiderLoader
from utils.deprecate import create_deprecated_class

SpiderManager = create_deprecated_class('SpiderManager', SpiderLoader)
