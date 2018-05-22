# -*- coding: UTF-8 -*-
"""
Scrapy - a web crawling and web scraping framework written for Python
"""

__all__ = ['__version__', 'version_info', 'twisted_version',
           'Spider', 'Request', 'FormRequest', 'Selector', 'Item', 'Field']

# Scrapy version
# 获取scrapy版本信息
import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()
version_info = tuple(int(v) if v.isdigit() else v
                     for v in __version__.split('.'))
del pkgutil

# Check minimum required Python version
# 当前python版本校验
import sys
if sys.version_info < (2, 7):
    print("Scrapy %s requires Python 2.7" % __version__)
    sys.exit(1)

# Ignore noisy twisted deprecation warnings
# 忽略twisted警告
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='twisted')
del warnings

# Apply monkey patches to fix issues in external libraries
from . import _monkeypatches
del _monkeypatches

from twisted import version as _txv
twisted_version = (_txv.major, _txv.minor, _txv.micro)

# Declare top-level shortcuts
from spiders import Spider
from http import Request, FormRequest
from selector import Selector
from item import Item, Field

del sys
