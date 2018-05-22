# -*- coding: UTF-8 -*-
import os
from six.moves import cPickle as pickle
import warnings

from importlib import import_module
from os.path import join, dirname, abspath, isabs, exists

from scrapy.utils.conf import closest_scrapy_cfg, get_config, init_env
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured

ENVVAR = 'SCRAPY_SETTINGS_MODULE'
DATADIR_CFG_SECTION = 'datadir'

# 判定当前执行命令的位置是否在一个scrapy项目下
def inside_project():
    scrapy_module = os.environ.get('SCRAPY_SETTINGS_MODULE')
    if scrapy_module is not None:
        try:
            import_module(scrapy_module)
        except ImportError as exc:
            warnings.warn("Cannot import scrapy settings module %s: %s" % (scrapy_module, exc))
        else:
            return True
    return bool(closest_scrapy_cfg())


def project_data_dir(project='default'):
    """Return the current project data dir, creating it if it doesn't exist"""
    if not inside_project():
        raise NotConfigured("Not inside a project")
    cfg = get_config()
    if cfg.has_option(DATADIR_CFG_SECTION, project):
        d = cfg.get(DATADIR_CFG_SECTION, project)
    else:
        scrapy_cfg = closest_scrapy_cfg()
        if not scrapy_cfg:
            raise NotConfigured("Unable to find scrapy.cfg file to infer project data dir")
        d = abspath(join(dirname(scrapy_cfg), '.scrapy'))
    if not exists(d):
        os.makedirs(d)
    return d


def data_path(path, createdir=False):
    """
    Return the given path joined with the .scrapy data directory.
    If given an absolute path, return it unmodified.
    """
    if not isabs(path):
        if inside_project():
            path = join(project_data_dir(), path)
        else:
            path = join('.scrapy', path)
    if createdir and not exists(path):
        os.makedirs(path)
    return path

# 获取项目配置
def get_project_settings():
    if ENVVAR not in os.environ:
        # 获取环境配置项
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        # 初始化项目配置，实际就是将项目根目录下的scrapy.cfg配置中的[settings]的default属性值配置到系统变量SCRAPY_SETTINGS_MODULE
        init_env(project)
    # 读取setting配置文件所有配置项到内存
    settings = Settings()
    settings_module_path = os.environ.get(ENVVAR)   #cfg文件中配置的settings路径
    if settings_module_path:    #项目的settings配置覆盖default.settings配置
        settings.setmodule(settings_module_path, priority='project')

    # XXX: remove this hack
    pickled_settings = os.environ.get("SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE")
    if pickled_settings:
        settings.setdict(pickle.loads(pickled_settings), priority='project')

    # XXX: deprecate and remove this functionality
    env_overrides = {k[7:]: v for k, v in os.environ.items() if
                     k.startswith('SCRAPY_')}
    if env_overrides:       #覆盖settings配置
        settings.setdict(env_overrides, priority='project')

    return settings
