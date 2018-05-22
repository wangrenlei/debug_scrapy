# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.spiders
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.spider` is deprecated, "
              "use `scrapy.spiders` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from spiders import *
