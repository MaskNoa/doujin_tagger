# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import datetime
import logging
import os
import re
from pathlib import Path

logger = logging.getLogger("doutag.util")

USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
              "(KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")

JP_TRANSDICT = {
    "販売日": "date",
    "声優": "artist",
    "年齢指定": "nsfw",
    "ジャンル": "genre",
    "シリーズ名": "series",
}

CN_TRANSDICT = {
    "贩卖日": "date",
    "声优": "artist",
    "年龄指定": "nsfw",
    "分类": "genre",
    "系列名": "series",
}

TRANSDICTS = [JP_TRANSDICT, CN_TRANSDICT]
LANG_H = ["ja;q=1", "zh-CN,zh;q=1"]
LANGS = ['JP', 'CN']


def process_dlsite_info(info):
    """modified info dict in place"""
    for key, val in info.items():
        if key == "date":
            try:
                date_tuple = re.search(r"(\d+)年(\d+)月(\d+)日", val[0]).groups()
                fmt_date = datetime.datetime(*map(int, date_tuple))
                res = fmt_date.strftime("%Y-%m")
                # keep it a list for consistency
                info[key] = [res, ]
            except (AttributeError, TypeError) as e:
                logger.warning("PROCESS DATE ERROR")
                logger.debug(e)
                info[key] = ["", ]
        elif key in ("genre", "artist"):
            new = []
            for each in val:
                temp = each.strip()
                each = each.replace("/", "").strip()
                if each:
                    new.append(temp)
            info[key] = new


def match_path(path, pat):
    """find dirs matched RJPAT under given path"""
    for root, dirs, _ in os.walk(path):
        matchobj = pat.search(root)
        if matchobj:
            rjcode = matchobj.group(1).upper()
            # stop searching deeper
            dirs.clear()
            yield (rjcode, root)


def find_inner_most(orig):
    '''find the most inner dirs that holds the data'''
    orig = Path(orig)
    while len(list(orig.iterdir())) == 1:
        orig = next(orig.iterdir())
        if not orig.is_dir():
            orig = orig.parent
            break
    return orig
