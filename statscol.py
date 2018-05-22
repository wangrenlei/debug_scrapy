# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.statscollectors
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.statscol` is deprecated, "
              "use `scrapy.statscollectors` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from statscollectors import *
