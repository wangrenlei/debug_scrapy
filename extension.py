# -*- coding: UTF-8 -*-
# 扩展管理器
"""
The Extension Manager

See documentation in docs/topics/extensions.rst
"""
from middleware import MiddlewareManager
from utils.conf import build_component_list

class ExtensionManager(MiddlewareManager):

    component_name = 'extension'

    # 从配置信息中获取扩展中间件列表并构建
    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings.getwithbase('EXTENSIONS'))
