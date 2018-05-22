# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.squeues
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.squeue` is deprecated, "
              "use `scrapy.squeues` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from squeues import *
