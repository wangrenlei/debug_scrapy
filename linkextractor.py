# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.linkextractors
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.linkextractor` is deprecated, "
              "use `scrapy.linkextractors` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from linkextractors import *
