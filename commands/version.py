# -*- coding: UTF-8 -*-
from __future__ import print_function

import scrapy
from . import ScrapyCommand
from scrapy.utils.versions import scrapy_components_versions


class Command(ScrapyCommand):

    default_settings = {'LOG_ENABLED': False,
                        'SPIDER_LOADER_WARN_ONLY': True}

    def syntax(self):
        return "[-v]"

    def short_desc(self):
        return "Print Scrapy version"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("--verbose", "-v", dest="verbose", action="store_true",
            help="also display twisted/python/platform info (useful for bug reports)")

    def run(self, args, opts):
        # --verbose参数，输出各个依赖组件版本
        if opts.verbose:
            versions = scrapy_components_versions()
            width = max(len(n) for (n, _) in versions)
            patt = "%-{}s : %s".format(width)
            for name, version in versions:
                print(patt % (name, version))
        # 输出scrapy版本
        else:
            print("Scrapy %s" % scrapy.__version__)

