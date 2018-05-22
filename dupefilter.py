# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.dupefilters
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.dupefilter` is deprecated, "
              "use `scrapy.dupefilters` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from dupefilters import *
