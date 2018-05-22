# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.commands
import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.command` is deprecated, "
              "use `scrapy.commands` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from commands import *
