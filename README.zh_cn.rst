doujin_tagger
=============

|travis|

doujin_tagger 是一个同人音声音频的批量标签处理程序.

安装
=============
::
    
    git clone https://github.com/maybeRainH/doujin_tagger
    cd doujin_tagger
    python setup.py install

用法
======

-h, --help            显示帮助
--orig ORIG, -o ORIG  源文件夹
--dest DEST, -d DEST  处理好的文件需要移动过去的目标文件夹
--cov, -c             保存封面(默认)
--nocov, -q           不保存封面
--lang LANG, -l LANG  0: 日语标签(默认), 1: 中文标签
--proxy               代理(见下面的举例)

使用::

    doutag -o <文件夹> -d <文件夹> -q --lang=1 --proxy=socks5://127.0.0.1:1080

注意
=========
* Dlsite被墙,请使用proxy选项
* Windows下的路径名请使用双反斜杠\\,例如: E:\\MUSIC\\ORIG
* 按一下Ctrl+C可以等待多线程安全退出
* **删除了使用json保存上次配置的功能,请使用bash/bat处理,查看example.bat**
* ``orig`` 和 ``dest`` **必须** 处于同一分区
* ``orig`` 和 ``dest`` **不能** 一个是另一个的子文件夹甚至同一文件夹
* **暂时不支持WAV文件**
* 现在保存封面在每一个包含音频的文件夹下面

更新日志
=========
v0.4.0 (2019-12-31)
-------------------
* [feat] 使用tqdm的进度条式输出.
* [feat] 多线程的安全退出,使用CTRL+C.
* [feat] 删除了debug选项
* [bug] 实现删除原来的可能是社团自行加上的乱码的标签.

v0.3.0 (2019-10-19)
-------------------
* [feat] 删除json配置
* [feat] 加入代理选项
* [feat] 在dlsite里artist信息缺失时爬取hvdb的artist信息

v0.2.0 (2019-8-30)
-------------------
* [feat] 新增 ``rjcode`` 的tag
* [feat] 新增 ``series`` 的tag
* [fix] dlsite爬虫中的请求地址的拼接错误 

.. |travis| image:: https://travis-ci.org/maybeRainH/doujin_tagger.svg?branch=master
    :target: https://travis-ci.org/maybeRainH/doujin_tagger