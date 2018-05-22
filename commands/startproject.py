# -*- coding: UTF-8 -*-
from __future__ import print_function
import re
import os
import string
from importlib import import_module
from os.path import join, exists, abspath
from shutil import ignore_patterns, move, copy2, copystat

import scrapy
from . import ScrapyCommand
from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.exceptions import UsageError


TEMPLATES_TO_RENDER = (
    ('scrapy.cfg',),
    ('${project_name}', 'settings.py.tmpl'),
    ('${project_name}', 'items.py.tmpl'),
    ('${project_name}', 'pipelines.py.tmpl'),
    ('${project_name}', 'middlewares.py.tmpl'),
)

IGNORE = ignore_patterns('*.pyc', '.svn')

# 快速构建scrapy项目
class Command(ScrapyCommand):

    requires_project = False
    default_settings = {'LOG_ENABLED': False,
                        'SPIDER_LOADER_WARN_ONLY': True}

    def syntax(self):
        return "<project_name> [project_dir]"

    def short_desc(self):
        return "Create new project"
    # 校验项目名
    def _is_valid_name(self, project_name):
        def _module_exists(module_name):
            try:
                import_module(module_name)
                return True
            except ImportError:
                return False

        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print('Error: Project names must begin with a letter and contain'\
                    ' only\nletters, numbers and underscores')
        elif _module_exists(project_name):
            print('Error: Module %r already exists' % project_name)
        else:
            return True
        return False

    def _copytree(self, src, dst):
        """
        Since the original function always creates the directory, to resolve
        the issue a new function had to be created. It's a simple copy and
        was reduced for this case.

        More info at:
        https://github.com/scrapy/scrapy/pull/2005
        """
        ignore = IGNORE
        names = os.listdir(src)
        ignored_names = ignore(src, names)

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in names:
            if name in ignored_names:
                continue

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
        copystat(src, dst)

    def run(self, args, opts):
        if len(args) not in (1, 2):
            raise UsageError()
        # 项目名
        project_name = args[0]
        # 项目目录
        project_dir = args[0]

        if len(args) == 2:
            project_dir = args[1]
        # 该项目根目录下是否存在scrapy.cfg文件
        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print('Error: scrapy.cfg already exists in %s' % abspath(project_dir))
            return
        # 项目名正确性校验
        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return
        # 将模板目录templates下内容拷贝到当前项目下
        self._copytree(self.templates_dir, abspath(project_dir))
        # 将module替换成项目名
        move(join(project_dir, 'module'), join(project_dir, project_name))
        # 选择爬虫类模板文件，并填充内容，生成代码文件
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir,
                string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name,
                ProjectName=string_camelcase(project_name))
        print("New Scrapy project %r, using template directory %r, created in:" % \
              (project_name, self.templates_dir))
        print("    %s\n" % abspath(project_dir))
        print("You can start your first spider with:")
        print("    cd %s" % project_dir)
        print("    scrapy genspider example example.com")

    # 模板目录
    @property
    def templates_dir(self):
        _templates_base_dir = self.settings['TEMPLATES_DIR'] or \
            join(scrapy.__path__[0], 'templates')
        return join(_templates_base_dir, 'project')

