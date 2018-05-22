# -*- coding: UTF-8 -*-
from __future__ import print_function
import json
import logging

from w3lib.url import is_url

from . import ScrapyCommand
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils import display
from scrapy.utils.conf import arglist_to_dict
from scrapy.utils.spider import iterate_spider_output, spidercls_for_request
from scrapy.exceptions import UsageError

logger = logging.getLogger(__name__)


class Command(ScrapyCommand):

    requires_project = True

    spider = None
    items = {}
    requests = {}

    first_response = None

    def syntax(self):
        return "[options] <url>"

    def short_desc(self):
        return "Parse URL (using its spider) and print the results"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("--spider", dest="spider", default=None,
            help="use this spider without looking for one")
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
            help="set spider argument (may be repeated)")
        parser.add_option("--pipelines", action="store_true",
            help="process items through pipelines")
        parser.add_option("--nolinks", dest="nolinks", action="store_true",
            help="don't show links to follow (extracted requests)")
        parser.add_option("--noitems", dest="noitems", action="store_true",
            help="don't show scraped items")
        parser.add_option("--nocolour", dest="nocolour", action="store_true",
            help="avoid using pygments to colorize the output")
        parser.add_option("-r", "--rules", dest="rules", action="store_true",
            help="use CrawlSpider rules to discover the callback")
        parser.add_option("-c", "--callback", dest="callback",
            help="use this callback for parsing, instead looking for a callback")
        parser.add_option("-m", "--meta", dest="meta",
            help="inject extra meta into the Request, it must be a valid raw json string")
        parser.add_option("-d", "--depth", dest="depth", type="int", default=1,
            help="maximum depth for parsing requests [default: %default]")
        parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
            help="print each depth level one by one")


    @property
    def max_level(self):
        levels = list(self.items.keys()) + list(self.requests.keys())
        if not levels:
            return 0
        return max(levels)
    # 添加items
    def add_items(self, lvl, new_items):
        old_items = self.items.get(lvl, [])
        self.items[lvl] = old_items + new_items
    # 添加request
    def add_requests(self, lvl, new_reqs):
        old_reqs = self.requests.get(lvl, [])
        self.requests[lvl] = old_reqs + new_reqs
    # 输出items
    def print_items(self, lvl=None, colour=True):
        if lvl is None:
            items = [item for lst in self.items.values() for item in lst]
        else:
            items = self.items.get(lvl, [])

        print("# Scraped Items ", "-"*60)
        display.pprint([dict(x) for x in items], colorize=colour)
    # 输出request
    def print_requests(self, lvl=None, colour=True):
        if lvl is None:
            levels = list(self.requests.keys())
            if levels:
                requests = self.requests[max(levels)]
            else:
                requests = []
        else:
            requests = self.requests.get(lvl, [])

        print("# Requests ", "-"*65)
        display.pprint(requests, colorize=colour)
    # 输出结果
    def print_results(self, opts):
        colour = not opts.nocolour

        if opts.verbose:
            for level in range(1, self.max_level+1):
                print('\n>>> DEPTH LEVEL: %s <<<' % level)
                if not opts.noitems:
                    self.print_items(level, colour)
                if not opts.nolinks:
                    self.print_requests(level, colour)
        else:
            print('\n>>> STATUS DEPTH LEVEL %s <<<' % self.max_level)
            if not opts.noitems:
                self.print_items(colour=colour)
            if not opts.nolinks:
                self.print_requests(colour=colour)
    # 执行回调函数
    def run_callback(self, response, cb):
        items, requests = [], []
        # 这里如果是解析就是parse(response)
        for x in iterate_spider_output(cb(response)):
            if isinstance(x, (BaseItem, dict)):     # 这里判定是否是item
                items.append(x)
            elif isinstance(x, Request):        # 这里判定是否是request
                requests.append(x)
        return items, requests
    # 从爬虫的rules属性中获取回调函数
    def get_callback_from_rules(self, spider, response):
        if getattr(spider, 'rules', None):
            for rule in spider.rules:
                if rule.link_extractor.matches(response.url):
                    return rule.callback or "parse"
        else:
            logger.error('No CrawlSpider rules found in spider %(spider)r, '
                         'please specify a callback to use for parsing',
                         {'spider': spider.name})
    # 初始化spider对象
    def set_spidercls(self, url, opts):
        spider_loader = self.crawler_process.spider_loader
        if opts.spider:
            try:
                self.spidercls = spider_loader.load(opts.spider)
            except KeyError:
                logger.error('Unable to find spider: %(spider)s',
                             {'spider': opts.spider})
        else:
            self.spidercls = spidercls_for_request(spider_loader, Request(url))
            if not self.spidercls:
                logger.error('Unable to find spider for: %(url)s',
                             {'url': url})

        # Request requires callback argument as callable or None, not string
        request = Request(url, None)
        # 初始化request，请求链接
        _start_requests = lambda s: [self.prepare_request(s, request, opts)]
        self.spidercls.start_requests = _start_requests
    # 开始解析，实际就是调度爬虫下载器进行下载解析，和正常调用爬虫是一样的
    def start_parsing(self, url, opts):
        self.crawler_process.crawl(self.spidercls, **opts.spargs)
        self.pcrawler = list(self.crawler_process.crawlers)[0]
        self.crawler_process.start()

        if not self.first_response:
            logger.error('No response downloaded for: %(url)s',
                         {'url': url})
    # 获取request和items
    def prepare_request(self, spider, request, opts):
        def callback(response):
            # memorize first request
            if not self.first_response:
                self.first_response = response

            # determine real callback
            cb = response.meta['_callback']
            if not cb:
                # 从选项callback中获取
                if opts.callback:
                    cb = opts.callback
                # 从spider的rules属性中获取，只获取一次
                elif opts.rules and self.first_response == response:
                    cb = self.get_callback_from_rules(spider, response)

                    if not cb:
                        logger.error('Cannot find a rule that matches %(url)r in spider: %(spider)s',
                                 {'url': response.url, 'spider': spider.name})
                        return
                # spider的parse方法
                else:
                    cb = 'parse'

            if not callable(cb):
                # 获取相应的回调方法
                cb_method = getattr(spider, cb, None)
                if callable(cb_method):
                    cb = cb_method
                else:
                    logger.error('Cannot find callback %(callback)r in spider: %(spider)s',
                                 {'callback': cb, 'spider': spider.name})
                    return

            # parse items and requests
            depth = response.meta['_depth']
            # 解析获取requests和items
            items, requests = self.run_callback(response, cb)
            if opts.pipelines:
                itemproc = self.pcrawler.engine.scraper.itemproc
                for item in items:
                    itemproc.process_item(item, spider)
            self.add_items(depth, items)
            self.add_requests(depth, requests)

            if depth < opts.depth:
                for req in requests:
                    req.meta['_depth'] = depth + 1
                    req.meta['_callback'] = req.callback
                    req.callback = callback
                return requests

        #update request meta if any extra meta was passed through the --meta/-m opts.
        if opts.meta:
            request.meta.update(opts.meta)

        request.meta['_depth'] = 1
        request.meta['_callback'] = request.callback
        request.callback = callback
        return request

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)

        self.process_spider_arguments(opts)
        self.process_request_meta(opts)

    def process_spider_arguments(self, opts):

        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)

    def process_request_meta(self, opts):

        if opts.meta:
            try:
                opts.meta = json.loads(opts.meta)
            except ValueError:
                raise UsageError("Invalid -m/--meta value, pass a valid json string to -m or --meta. " \
                                "Example: --meta='{\"foo\" : \"bar\"}'", print_help=False)


    def run(self, args, opts):
        # parse arguments
        if not len(args) == 1 or not is_url(args[0]):
            raise UsageError()
        else:
            url = args[0]

        # prepare spidercls
        # 初始化spidercls对象
        self.set_spidercls(url, opts)
        # 开始执行爬取并输出内容
        if self.spidercls and opts.depth > 0:
            self.start_parsing(url, opts)
            self.print_results(opts)
