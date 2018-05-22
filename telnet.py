# -*- coding: UTF-8 -*-
# 已弃用  替换至——>scrapy.extensions.telnet
import warnings
from exceptions import ScrapyDeprecationWarning
warnings.warn("Module `scrapy.telnet` is deprecated, "
              "use `scrapy.extensions.telnet` instead",
              ScrapyDeprecationWarning, stacklevel=2)

from extensions.telnet import *
