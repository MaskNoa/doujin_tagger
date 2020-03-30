# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import logging
import sys
from argparse import ArgumentParser
from os import path

from doujin_tagger import __author__, __version__

logger = logging.getLogger("doutag.cmdline")


def banner():
    print('''
  _____                    _______
 |  __ \                  |__   __|
 | |  | |   ___    _   _     | |      __ _    __ _
 | |  | |  / _ \  | | | |    | |     / _` |  / _` |
 | |__| | | (_) | | |_| |    | |    | (_| | | (_| |
 |_____/   \___/   \__,_|    |_|     \__,_|  \__, |
                                              __/ |
                                             |___/
                                       v%s by %s
''' % (__version__, __author__))


def cmd_parser():
    parser = ArgumentParser(description="a doujin voice tagger")
    parser.add_argument("--orig", "-o", type=str, dest="orig",
                        action="store", help="directory to process")
    parser.add_argument("--dest", "-d", type=str,
                        dest="dest", action="store", help="destination")
    parser.add_argument("--nocov", "-q", action="store_false",
                        dest="cover", default=True, help="do not save cover")
    parser.add_argument("--debug", action="store_true", dest="debug",
                        default=False, help="run in single thread for debug")
    parser.add_argument("--lang", "-l", type=int, dest="lang", action="store",
                        default=0, help="0 for Japanese(default), 1 for Chinese")
    parser.add_argument("--proxy", type=str, dest="proxy", action="store",
                        help="proxy, the same as 'requests' module")
    parser.add_argument("--method", "-m", type=str, dest="method", default="save2ape",
                        action="store", help="how to save tags")

    options = parser.parse_args(sys.argv[1:])
    if not (options.orig and options.dest):
        logger.error("必须提供orig和dest参数")
        exit(1)
    if not path.exists(options.orig) or not path.exists(options.dest):
        logger.error("orig或者dest文件夹不存在")
        exit(1)
    # for file rename, we must have both on the same mount point.
    # XXX not tested on *nix if two on different mount point
    if path.splitdrive(options.orig)[0] != path.splitdrive(options.dest)[0]:
        logger.error("orig和dest文件夹不在一个分区")
        exit(1)
    logger.debug(f"options is {options}")

    return options
