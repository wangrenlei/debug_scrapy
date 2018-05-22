# debug_scrapy
> This repository is about how to debug scrapy core source code and read it .</br>

    （注：此repo是从scrapy源码中抽离出来的scrapy目录，并对大多数代码做了翻译解读，仅供阅读参考，如果有不正确的地方欢迎讨论。小弟翻译不容易，可否给我个小star，让我更有动力去完善它。谢谢！）
###  1. Get the code:
 git clone https://github.com/wangrenlei/debug_scrapy.git

### 2. Setup the environment
    >   python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
        install_requires=[
        'Twisted>=13.1.0',
        'w3lib>=1.17.0',
        'queuelib',
        'lxml',
        'pyOpenSSL',
        'cssselect>=0.9',
        'six>=1.5.2',
        'parsel>=1.4',
        'PyDispatcher>=2.0.5',
        'service_identity']</br>

    （注：可能环境中的依赖不够完全，那么就在项目运行中根据情况自行添加吧，年纪大了实在是忘了当时候可能装过啥）

### 3. Run the application:
* `python __main__.py` or `python command.py`</br>

（注：这里默认使用IDE的debug调试，入口处写了所有指令的主要使用方式，根据实际调试情况自行进行注释或释放）

### 4. Other helps:
* `https://blog.csdn.net/column/details/22621.html`</br>


> 翻译解读还未完全完成，见谅 .