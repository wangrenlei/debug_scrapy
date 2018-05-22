# -*- coding: UTF-8 -*-
from zope.interface import Interface
# 爬虫加载器接口定义
class ISpiderLoader(Interface):
    # 根据配置信息返回实例化对象
    def from_settings(settings):
        """Return an instance of the class for the given settings"""
    # 根据给定的爬虫名key返回对应的爬虫类，如果爬虫名不存在，则抛出keyerror异常
    def load(spider_name):
        """Return the Spider class for the given spider name. If the spider
        name is not found, it must raise a KeyError."""
    # 返回所有可用爬虫列表
    def list():
        """Return a list with the names of all spiders available in the
        project"""
    #
    # 返回能够处理给定请求的可用爬虫列表
    def find_by_request(request):
        """Return the list of spiders names that can handle the given request"""

# ISpiderLoder替代ISpiderManager
# ISpiderManager is deprecated, don't use it!
# An alias is kept for backwards compatibility.
ISpiderManager = ISpiderLoader
