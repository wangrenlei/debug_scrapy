# -*- coding: UTF-8 -*-
from . import fetch, ScrapyCommand
from scrapy.utils.response import open_in_browser

class Command(fetch.Command):

    def short_desc(self):
        return "Open URL in browser, as seen by Scrapy"

    def long_desc(self):
        return "Fetch a URL using the Scrapy downloader and show its " \
            "contents in a browser"

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.remove_option("--headers")
    # 输出内容，将response通过webbrowser来在浏览器打开
    def _print_response(self, response, opts):
        open_in_browser(response)
