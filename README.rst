doujin_tagger
=============

|travis|

doujin_tagger 是一个同人音声音频的批量标签处理程序.

安装
=============
::

    pip install mutagen

    git clone https://github.com/maybeRainH/doujin_tagger

    cd doujin_tagger; python setup.py install

用法
======

-h, --help            显示帮助
--orig ORIG, -o ORIG  源文件夹
--dest DEST, -d DEST  处理好的文件需要移动过去的目标文件夹
--nocov, -q           不保存封面
--lang LANG, -l LANG  0: 日语标签(默认), 1: 中文标签
--proxy               代理(见下面的举例)
--method              保存信息的方法

举例::

    doutag -o <文件夹> -d <文件夹> -q --lang=1 --proxy=127.0.0.1:1080 --method=save2ape

两种保存方法
=============
1. method=save2ape(默认)
    利用foobar2000 + external_tags_ 插件,无需保存信息到音频文件的标签中,速度快
    记得打开fb2k > 配置 > 高级 > 标签 > External Tags > Take over all tagging打上勾

2. method=save2file
    将信息保存到音频文件中,优点是跨生态,主流的音乐管理软件都可以读取

注意
=========
* Dlsite被墙,请使用proxy选项
* Windows下的路径名请使用双反斜杠,例如: ``E:\\MUSIC\\ORIG``
* 按一下Ctrl+C可以等待多线程安全退出
* ``orig`` 和 ``dest`` **必须** 处于同一分区
* ``orig`` 和 ``dest`` **不能** 一个是另一个的子文件夹甚至同一文件夹
* save2file方法 **暂时不支持WAV文件** ,遇到时会停止处理当前RJ号所在文件夹

更新日志
=========
v0.6.0 (2020-3-31)
------------------
* [feat] 增加了两种方法的选择
* [docs] 不再推荐使用我自己forked的mutagen版本,m4a的多值识别问题只存在与facet插件中

v0.5.0 (2020-2-9)
------------------
* [feat] 删掉烂七八糟的audio相关代码和测试,爽!
* [feat] 删掉cov选项,默认下载封面
* [breaking change] 原来TAGS标签现在改用GENRE,请使用fb2k的MassTagger插件批量处理

v0.4.0 (2019-12-31)
-------------------
* [feat] 使用tqdm的进度条式输出.
* [feat] 多线程的安全退出,使用CTRL+C.
* [feat] 删除了debug选项
* [bug] 实现删除原来的可能是社团自行加上的乱码的标签.

v0.3.0 (2019-10-19)
-------------------
* [feat] 删除json配置,使用bash/bat处理,查看example.bat
* [feat] 加入代理选项
* [feat] 在dlsite里artist信息缺失时爬取hvdb的artist信息

v0.2.0 (2019-8-30)
-------------------
* [feat] 新增 ``rjcode`` 的tag
* [feat] 新增 ``series`` 的tag
* [fix] dlsite爬虫中的请求地址的拼接错误 

.. |travis| image:: https://travis-ci.org/maybeRainH/doujin_tagger.svg?branch=master
    :target: https://travis-ci.org/maybeRainH/doujin_tagger
.. _external_tags: https://www.foobar2000.org/components/view/foo_external_tags