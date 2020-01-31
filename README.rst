doujin_tagger
=============

|travis|  |support|

`中文说明 <README.zh_cn.rst>`__

doujin_tagger is a doujin voice audio file tagger.

Installation
=============
::
    
    git clone https://github.com/maybeRainH/doujin_tagger
    cd doujin_tagger
    python setup.py install

Usage
======

-h, --help            show this help message and exit
--orig ORIG, -o ORIG  directory to process
--dest DEST, -d DEST  destination
--cov, -c             save cover(default)
--nocov, -q           do not save cover
--lang LANG, -l LANG  0 for Japanese(default), 1 for Chinese
--proxy               proxy used for spider(see example below)

usage::

    doutag -o <dir> -d <dir> -q --lang=1 --proxy=socks5://127.0.0.1:1080

Attention
=========
* Under Windows, please use double backslash, eg. E:\\MUSIC\\ORIG
* press Ctrl+C once to safely exit the mutlithread.
* ``orig`` and ``dest`` **MUST** under the same mount point.
* ``orig`` and ``dest`` **MUST** NOT be the same or one is a subdirectory of other.
* **not support WAV** for now.
* now saving cover under each audio dir.

ChangeLog
==========
v0.4.0 (2019-12-31)
-------------------
* [feat] use tqdm to prettify output.
* [feat] mutlithread safe exit.
* [feat] deletel 'debug' option.
* [bug] delete all possible mojibake tags tagged by producer

v0.3.0 (2019-10-19)
-------------------
* [feat] remove json configuration. use a bash/bat script instead.
* [feat] add proxy options
* [feat] scrape hvdb artist info when artist not found in dlsite.

v0.2.0 (2019-8-30)
-------------------
* [feat] add rjcode tags
* [feat] add series tags
* [fix] url concat in dlsite spider 

.. |travis| image:: https://travis-ci.org/maybeRainH/doujin_tagger.svg?branch=master
    :target: https://travis-ci.org/maybeRainH/doujin_tagger   
.. |support| image:: https://img.shields.io/badge/support-mp3%7Cm4a%7Cxiph(ogg%2Cflac...)-orange
