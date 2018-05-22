# -*- coding: UTF-8 -*-
# 给定一个url，通过下载器进行下载，并将页面输出
from __future__ import print_function
import sys, six
from w3lib.url import is_url

from . import ScrapyCommand
from scrapy.http import Request
from scrapy.exceptions import UsageError
from scrapy.utils.datatypes import SequenceExclude
from scrapy.utils.spider import spidercls_for_request, DefaultSpider

class Command(ScrapyCommand):

    requires_project = False

    def syntax(self):
        return "[options] <url>"

    def short_desc(self):
        return "Fetch a URL using the Scrapy downloader"

    def long_desc(self):
        return "Fetch a URL using the Scrapy downloader and print its content " \
            "to stdout. You may want to use --nolog to disable logging"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("--spider", dest="spider",
            help="use this spider")
        parser.add_option("--headers", dest="headers", action="store_true", \
            help="print response HTTP headers instead of body")
        parser.add_option("--no-redirect", dest="no_redirect", action="store_true", \
            default=False, help="do not handle HTTP 3xx status codes and print response as-is")

    def _print_headers(self, headers, prefix):
        for key, values in headers.items():
            for value in values:
                self._print_bytes(prefix + b' ' + key + b': ' + value)

    def _print_response(self, response, opts):
        if opts.headers:
            self._print_headers(response.request.headers, b'>')
            print('>')
            self._print_headers(response.headers, b'<')
        else:
            self._print_bytes(response.body)

    def _print_bytes(self, bytes_):
        bytes_writer = sys.stdout if six.PY2 else sys.stdout.buffer
        bytes_writer.write(bytes_ + b'\n')

    def run(self, args, opts):
        # 参数校验
        if len(args) != 1 or not is_url(args[0]):
            raise UsageError()
        # 定义输出回调函数
        cb = lambda x: self._print_response(x, opts)
        # 初始化一个request对象
        request = Request(args[0], callback=cb, dont_filter=True)
        # by default, let the framework handle redirects,
        # i.e. command handles all codes expect 3xx
        # 如果选项中没有no_redirect，即不进行转发，则可处理的状态列表中包含除了300到400之间的所有状态码
        if not opts.no_redirect:
            request.meta['handle_httpstatus_list'] = SequenceExclude(range(300, 400))
        else:
            # 否则全部够可以处理，转发有请求库自动处理
            request.meta['handle_httpstatus_all'] = True
        # 初始化赋值为自带简易爬虫
        spidercls = DefaultSpider
        # 初始化爬虫加载器
        spider_loader = self.crawler_process.spider_loader
        # 如果给定了爬虫选项，则根据给定的爬虫来进行爬取，否则根据request url来查找匹配爬虫
        if opts.spider:
            spidercls = spider_loader.load(opts.spider)
        else:
            spidercls = spidercls_for_request(spider_loader, request, spidercls)
        # 默认使用自带的简易爬虫（scrapy.utils.spider.DefaultSpider）来进行给定url的数据抓取,只需要传递start_requests
        self.crawler_process.crawl(spidercls, start_requests=lambda: [request])
        # 爬虫开启
        self.crawler_process.start()
