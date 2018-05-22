# -*- coding: UTF-8 -*-
# 检查爬虫中是否有错误代码
from __future__ import print_function
import time
import sys
from collections import defaultdict
from unittest import TextTestRunner, TextTestResult as _TextTestResult

from . import ScrapyCommand
from scrapy.contracts import ContractsManager
from scrapy.utils.misc import load_object
from scrapy.utils.conf import build_component_list

# 输出校验结果
class TextTestResult(_TextTestResult):
    def printSummary(self, start, stop):
        write = self.stream.write
        writeln = self.stream.writeln

        run = self.testsRun
        plural = "s" if run != 1 else ""

        writeln(self.separator2)
        writeln("Ran %d contract%s in %.3fs" % (run, plural, stop - start))
        writeln()

        infos = []
        if not self.wasSuccessful():
            write("FAILED")
            failed, errored = map(len, (self.failures, self.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            write("OK")

        if infos:
            writeln(" (%s)" % (", ".join(infos),))
        else:
            write("\n")


class Command(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <spider>"

    def short_desc(self):
        return "Check spider contracts"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-l", "--list", dest="list", action="store_true",
                          help="only list contracts, without checking them")
        parser.add_option("-v", "--verbose", dest="verbose", default=False, action='store_true',
                          help="print contract tests for all spiders")

    def run(self, args, opts):
        # load contracts
        # 获取系统基础的contracts类路径
        contracts = build_component_list(self.settings.getwithbase('SPIDER_CONTRACTS'))
        # 使用ContractManager进行contract加载
        conman = ContractsManager(load_object(c) for c in contracts)
        # 实例化一个TextTestRunner对象
        runner = TextTestRunner(verbosity=2 if opts.verbose else 1)
        # 返回处理后的TextTestResult对象
        result = TextTestResult(runner.stream, runner.descriptions, runner.verbosity)

        # contract requests
        # contract 请求
        contract_reqs = defaultdict(list)
        # 实例化爬虫加载器
        spider_loader = self.crawler_process.spider_loader

        for spidername in args or spider_loader.list():
            spidercls = spider_loader.load(spidername)
            spidercls.start_requests = lambda s: conman.from_spider(s, result)
            # 获取测试方法
            tested_methods = conman.tested_methods_from_spidercls(spidercls)
            if opts.list:
                for method in tested_methods:
                    contract_reqs[spidercls.name].append(method)
            elif tested_methods:        #如果有测试方法，则进行crawl方法
                self.crawler_process.crawl(spidercls)

        # start checks
        # 开始检验
        if opts.list:
            for spider, methods in sorted(contract_reqs.items()):
                if not methods and not opts.verbose:
                    continue
                print(spider)
                for method in sorted(methods):
                    print('  * %s' % method)
        else:
            start = time.time()
            self.crawler_process.start()
            stop = time.time()

            result.printErrors()
            result.printSummary(start, stop)
            self.exitcode = int(not result.wasSuccessful())

