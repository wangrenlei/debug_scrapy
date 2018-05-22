# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys, os
import optparse
import cProfile
import inspect
import pkg_resources

from scrapy import __version__
from scrapy.crawler import CrawlerProcess
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.misc import walk_modules
from scrapy.utils.project import inside_project, get_project_settings
from scrapy.utils.python import garbage_collect
from scrapy.settings.deprecated import check_deprecated_settings

# 迭代commands目录下的所有类
def _iter_command_classes(module_name):
    # TODO: add `name` attribute to commands and and merge this function with
    # scrapy.utils.spider.iter_spider_classes
    for module in walk_modules(module_name):
        for obj in vars(module).values():
            if inspect.isclass(obj) and \
                    issubclass(obj, ScrapyCommand) and \
                    obj.__module__ == module.__name__ and \
                    not obj == ScrapyCommand:
                yield obj

def _get_commands_from_module(module, inproject):
    d = {}
    for cmd in _iter_command_classes(module):
        """
        这里根据scrapy.cfg文件的检测结果，如果不存在则代表不是一个scrapy创建的项目，则每个指令的类中的requires_project属性决定了
        是否需要存在创建的项目才能出现在命令集合中，如crawl,edit等指令如果没有创建项目则不会出现在指令集合
        """
        if inproject or not cmd.requires_project:
            cmdname = cmd.__module__.split('.')[-1]
            d[cmdname] = cmd()
    return d
# 动态调用scrapy.commands目录下的所有模块函数
def _get_commands_from_entry_points(inproject, group='scrapy.commands'):
    cmds = {}
    for entry_point in pkg_resources.iter_entry_points(group):
        obj = entry_point.load()
        if inspect.isclass(obj):
            cmds[entry_point.name] = obj()
        else:
            raise Exception("Invalid entry point %s" % entry_point.name)
    return cmds

# 将scrapy/commands目录下的模块存在dict中，并返回
def _get_commands_dict(settings, inproject):
    cmds = _get_commands_from_module('scrapy.commands', inproject)
    cmds.update(_get_commands_from_entry_points(inproject))
    cmds_module = settings['COMMANDS_MODULE']
    if cmds_module:
        cmds.update(_get_commands_from_module(cmds_module, inproject))
    return cmds
# 返回指令名/ key
def _pop_command_name(argv):
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            return arg
        i += 1
# 指令描述头部
def _print_header(settings, inproject):
    if inproject:
        print("Scrapy %s - project: %s\n" % (__version__, \
            settings['BOT_NAME']))
    else:
        print("Scrapy %s - no active project\n" % __version__)
# 指令描述信息
def _print_commands(settings, inproject):
    _print_header(settings, inproject)
    print("Usage:")
    print("  scrapy <command> [options] [args]\n")
    print("Available commands:")
    cmds = _get_commands_dict(settings, inproject)
    # 指令按照字母顺序排序并打印输出
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  %-13s %s" % (cmdname, cmdclass.short_desc()))
    if not inproject:
        print()
        print("  [ more ]      More commands available when run from project directory")
    print()
    print('Use "scrapy <command> -h" to see more info about a command')
# 未知指令输出信息
def _print_unknown_command(settings, cmdname, inproject):
    _print_header(settings, inproject)
    print("Unknown command: %s\n" % cmdname)
    print('Use "scrapy" to see available commands')
# 输出帮助信息
def _run_print_help(parser, func, *a, **kw):
    try:
        func(*a, **kw)
    except UsageError as e:
        if str(e):
            parser.error(str(e))
        if e.print_help:
            parser.print_help()
        sys.exit(2)
# 命令行入口，也是项目执行入口
def execute(argv=None, settings=None):
    # 获取命令行输入参数
    if argv is None:
        argv = sys.argv

    # --- backwards compatibility for scrapy.conf.settings singleton ---
    # 向上兼容scrapy.conf单例,其实是报不支持这种配置方式的异常了
    if settings is None and 'scrapy.conf' in sys.modules:
        from . import conf
        if hasattr(conf, 'settings'):
            settings = conf.settings
    # ------------------------------------------------------------------

    # 获取项目配置
    if settings is None:
        settings = get_project_settings()
        # set EDITOR from environment if available
        try:
            editor = os.environ['EDITOR']
        except KeyError: pass
        else:
            settings['EDITOR'] = editor
    # 检验失效配置项(提示哪些配置已经失效了，这应该是打的补丁把-.-)
    check_deprecated_settings(settings)

    # --- backwards compatibility for scrapy.conf.settings singleton ---
    import warnings
    from scrapy.exceptions import ScrapyDeprecationWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ScrapyDeprecationWarning)
        from scrapy import conf
        conf.settings = settings    #获取项目配置
    # ------------------------------------------------------------------
    # 通过查找有没有cfg文件判定是否在当前执行目录下，用于后面对比require_project属性，决定指令是否可用
    inproject = inside_project()
    # 获取命令字典（key=命令名:value=实例对象）
    cmds = _get_commands_dict(settings, inproject)
    cmdname = _pop_command_name(argv)   #解析返回当前指令名称
    # 指令解析对象
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), \
        conflict_handler='resolve')
    if not cmdname:
        # 不存在的指令,打印内容（和 -version打印的内容其实一样）
        _print_commands(settings, inproject)
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(settings, cmdname, inproject)
        sys.exit(2)     #这里告诫我们，没事不要瞎输，你看程序退出了把=。=
    # 获取指令对象
    cmd = cmds[cmdname]
    # 指令语法
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    # 指令描述
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')      #保存cmd的settings，并且重复项将会覆盖之前的全局配置
    cmd.settings = settings         #重复项覆盖之后重新赋值给当前命令settings属性
    cmd.add_options(parser)         #给指令添加相应指令选项
    opts, args = parser.parse_args(args=argv[1:])
    _run_print_help(parser, cmd.process_options, args, opts)        #输出公共指令参数

    # 创建爬虫进程对象，通过此对象进行爬虫启动运行(划重点！！此处可能运行报错不通过，重新安装cryptography)
    cmd.crawler_process = CrawlerProcess(settings)
    _run_print_help(parser, _run_command, cmd, args, opts)
    sys.exit(cmd.exitcode)

# 指令运行
def _run_command(cmd, args, opts):
    if opts.profile:
        _run_command_profiled(cmd, args, opts)
    else:
        cmd.run(args, opts)

def _run_command_profiled(cmd, args, opts):
    if opts.profile:
        sys.stderr.write("scrapy: writing cProfile stats to %r\n" % opts.profile)
    loc = locals()
    p = cProfile.Profile()
    p.runctx('cmd.run(args, opts)', globals(), loc)
    if opts.profile:
        p.dump_stats(opts.profile)

if __name__ == '__main__':
    try:
        # =================》所有支持的指令《=================
        # execute(['scrapy'])

        # bench   用于批量测试
        # require代表必须在scrapy项目根目录下才存在的指令，或者有scrapy.cfg文件的目录
        # todo  translate
        # (require)check   校验爬虫的代码是否有错误
        # (require)crawl   运行一个爬虫
        # (require)edit    编辑爬虫
        # fetch   使用scrapy下载器拉取URL
        # genspider   根据之前定义的模板生成爬虫
        # runspider   运行自身包含的爬虫（没有创建项目）
        # settings    获取配置值
        # shell   scrapy指令交互窗口
        # startproject    快速创建一个scrapy项目
        # version     scrapy的版本号
        # view    在浏览器打开URL，通过scrapy查看


        # =================》version《=================
        # execute(['scrapy', 'version', '--help'])
        # execute(['scrapy','version','--verbose'])

        # =================》bench《=================
        # execute(['scrapy','bench'])

        # =================》fetch《=================
        # execute(['scrapy','fetch'])

        # =================》crawl《=================
        # execute(['scrapy','crawl','doutu'])

        # =================》check《=================
        # execute(['scrapy','check', '--help'])
        # execute(['scrapy', 'check', 'doutu'])

        # =================》edit《=================
        # execute(['scrapy','edit','doutu'])

        # =================》fetch《=================
        # execute(['scrapy','fetch','http://www.baidu.com'])

        # =================》genspider《=================
        # execute(['scrapy','genspider','-l'])
        # execute(['scrapy', 'genspider', 'AAA','aaa.com'])

        # =================》list《=================
        # execute(['scrapy','list'])

        # =================》parse《=================
        # execute(['scrapy','parse','http://www.baidu.com'])
        # execute(['scrapy', 'parse', 'https://www.doutula.com'])

        # =================》runspider《=================
        # execute(['scrapy','runspider','/home/wangsir/code/sourceWorkSpace/scrapy/spiders/spidertest/spider_apply.py'])

        # =================》settings《=================
        # execute(['scrapy','settings','--get','BOT_NAME'])

        # =================》settings《=================
        # execute(['scrapy', 'shell'])
        # execute(['scrapy', 'shell', 'http://www.baidu.com','--nolog'])

        # =================》settings《=================
        # execute(['scrapy', 'startproject', ''])

        # =================》version《=================
        # execute(['scrapy', 'version', '--verbose'])

        # =================》view《=================
        execute(['scrapy', 'view', 'http://www.baidu.com'])
    finally:
        # Twisted prints errors in DebugInfo.__del__, but PyPy does not run gc.collect()
        # on exit: http://doc.pypy.org/en/latest/cpython_differences.html?highlight=gc.collect#differences-related-to-garbage-collection-strategies
        garbage_collect()
