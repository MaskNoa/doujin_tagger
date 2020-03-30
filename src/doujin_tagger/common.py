# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


import logging
import os
import re
import shutil
import traceback
from pathlib import Path

from . import spider

logger = logging.getLogger("doutag.common")
FIELDS = {'album', 'genre'}
ILLEGAL_PAT = re.compile(r"[\\/:*?\"<>|\r\n]+")


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


class FunctionRet(Exception):
    pass


def fetch_info(info, cov_data, coverp, proxy, lang):
    spiders = {}
    for k, v in vars(spider).items():
        if k.startswith("spider") and callable(v):
            spiders[k] = v

    for k, func in spiders.items():
        func(info, cov_data, coverp, proxy, lang)
    if FIELDS - info.keys():
        logger.error(f"<{info['rjcode']}> INFO UNCOMPLETE, CHECK SPIDER LOG")
        return False
    return True


def move_to(work_path, dest, info):
    work_path = Path(work_path)
    dest = Path(dest)
    # 这里有bug,album key error
    dir_name = f"{info['rjcode']} {info['album'][0]}"
    dir_name = ILLEGAL_PAT.sub("", dir_name)
    full_name = dest / dir_name
    # XXX sometimes find_inner_most will work incorrectly
    # due to invisible __MACOSX dir
    path_to_move = find_inner_most(work_path)
    logger.debug(f"{path_to_move.name} moving to {full_name}")
    try:
        path_to_move.rename(full_name)
    except FileExistsError:
        logger.error(f"<{info['rjcode']}> SAME DIR IN DEST FOUND!")
        return False
    except Exception as e:
        logger.error(f"{repr(e)}")
        logger.debug(traceback.format_exc())
        return False
    # rescan and remove all empty dir
    if work_path.exists():
        if any(i for i in work_path.rglob("*") if i.is_file()):
            logger.error(f"<{info['rjcode']}> FILES REMAINING")
            return False
        else:
            shutil.rmtree(work_path)
    return True


def cover2dir(cover_dirs, cov_data):
    if cov_data.seek(0, 2) == 0:
        logger.warning('No Cover Found')
        return
    for eachdir in cover_dirs:
        cover_path = eachdir / "cover.jpg"
        if not cover_path.exists():
            cover_path.write_bytes(cov_data.getvalue())
