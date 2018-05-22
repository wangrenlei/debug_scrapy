# -*- coding: UTF-8 -*-
"""
Base class for Scrapy commands
"""
import os
from optparse import OptionGroup
from twisted.python import failure

from scrapy.utils.conf import arglist_to_dict
from scrapy.exceptions import UsageError

# scrapy 命令基类,运行的时候每个子类都有个run方法
class ScrapyCommand(object):
    # 是否是在startproject项目目录下或存在scrapy.cfg文件才可以使用的指令
    requires_project = False
    crawler_process = None
    # 该指令的配置优先级高于全局配置settings文件
    # default settings to be used for this command instead of global defaults
    default_settings = {}

    exitcode = 0

    def __init__(self):
        self.settings = None  # set in scrapy.cmdline
    # 设置当前crawler对象
    def set_crawler(self, crawler):
        assert not hasattr(self, '_crawler'), "crawler already set"
        self._crawler = crawler
    # 语法规则
    def syntax(self):
        """
        Command syntax (preferably one-line). Do not include command name.
        """
        return ""
    # 简短描述
    def short_desc(self):
        """
        A short description of the command
        """
        return ""
    # 详细描述
    def long_desc(self):
        """A long description of the command. Return short description when not
        available. It cannot contain newlines, since contents will be formatted
        by optparser which removes newlines and wraps text.
        """
        return self.short_desc()
    # 帮助
    def help(self):
        """An extensive help for the command. It will be shown when using the
        "help" command. It can contain newlines, since not post-formatting will
        be applied to its contents.
        """
        return self.long_desc()
    # 公共参数配置
    def add_options(self, parser):
        """
        Populate option parse with options available for this command
        """
        group = OptionGroup(parser, "Global Options")
        group.add_option("--logfile", metavar="FILE",
            help="log file. if omitted stderr will be used")
        group.add_option("-L", "--loglevel", metavar="LEVEL", default=None,
            help="log level (default: %s)" % self.settings['LOG_LEVEL'])
        group.add_option("--nolog", action="store_true",
            help="disable logging completely")
        group.add_option("--profile", metavar="FILE", default=None,
            help="write python cProfile stats to FILE")
        group.add_option("--pidfile", metavar="FILE",
            help="write process ID to FILE")
        group.add_option("-s", "--set", action="append", default=[], metavar="NAME=VALUE",
            help="set/override setting (may be repeated)")
        group.add_option("--pdb", action="store_true", help="enable pdb on failure")

        parser.add_option_group(group)
    # 当前进程配置
    def process_options(self, args, opts):
        try:
            self.settings.setdict(arglist_to_dict(opts.set),
                                  priority='cmdline')
        except ValueError:
            raise UsageError("Invalid -s value, use -s NAME=VALUE", print_help=False)

        if opts.logfile:
            self.settings.set('LOG_ENABLED', True, priority='cmdline')
            self.settings.set('LOG_FILE', opts.logfile, priority='cmdline')

        if opts.loglevel:
            self.settings.set('LOG_ENABLED', True, priority='cmdline')
            self.settings.set('LOG_LEVEL', opts.loglevel, priority='cmdline')

        if opts.nolog:
            self.settings.set('LOG_ENABLED', False, priority='cmdline')

        if opts.pidfile:
            with open(opts.pidfile, "w") as f:
                f.write(str(os.getpid()) + os.linesep)

        if opts.pdb:
            failure.startDebugMode()
    # 运行
    def run(self, args, opts):
        """
        Entry point for running commands
        """
        raise NotImplementedError
