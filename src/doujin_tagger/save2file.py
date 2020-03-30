# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


import io
import logging
import os
import re
import traceback
from pathlib import Path

from mutagen import File, MutagenError, easyid3, easymp4

from .common import FunctionRet, cover2dir, fetch_info, move_to

logger = logging.getLogger("doutag.S2F")

easymp4.EasyMP4Tags.RegisterTextKey('comment', '\xa9cmt')
easymp4.EasyMP4Tags.RegisterFreeformKey('rjcode', 'RJCODE')
easymp4.EasyMP4Tags.RegisterFreeformKey('maker', 'MAKER')
easymp4.EasyMP4Tags.RegisterFreeformKey('nsfw', 'NSFW')
easymp4.EasyMP4Tags.RegisterFreeformKey('series', 'SERIES')
easymp4.EasyMP4Tags.RegisterFreeformKey('doujin', 'DOUJIN')

easyid3.EasyID3.RegisterTextKey('comment', 'COMM')
easyid3.EasyID3.RegisterTXXXKey('rjcode', 'RJCODE')
easyid3.EasyID3.RegisterTXXXKey('maker', 'MAKER')
easyid3.EasyID3.RegisterTXXXKey('nsfw', 'NSFW')
easyid3.EasyID3.RegisterTXXXKey('series', 'SERIES')
easyid3.EasyID3.RegisterTXXXKey('doujin', 'DOUJIN')


AUDIO_EXT = ["mp3", "m4a", "ogg", "flac"]
AUDIO_PAT = re.compile(fr".*\.({'|'.join(AUDIO_EXT)})$")
UNSUPPORT_PAT = re.compile(r".*\.(wav|ape)$")


def update_audios(rjcode, work_path):
    audios_lst = []
    cover_dirs = []
    for root, dirs, files in os.walk(work_path):
        audio_found = False
        for eachfile in files:
            if UNSUPPORT_PAT.match(eachfile):
                logger.error(f"<{rjcode}> UNSUPPORT FMT FOUND")
                raise FunctionRet
            elif AUDIO_PAT.match(eachfile):
                audio_found = True
                full_path = os.path.join(root, eachfile)
                try:
                    f = File(full_path, easy=True)
                except MutagenError:
                    logger.error(f"<{rjcode}> LOADING ERROR --> {eachfile}")
                    logger.debug(traceback.format_exc())
                    raise FunctionRet
                assert f is not None
                audios_lst.append(f)
        else:
            if audio_found:
                cover_dirs.append(Path(root))

    if not audios_lst:
        logger.error(f"<{rjcode}> AUDIOS NOT FOUND")
        raise FunctionRet
    logger.debug(f"<{rjcode}> dirs_need_cover: {len(cover_dirs)}")
    logger.debug(f"<{rjcode}> audios: {len(audios_lst)}")
    return audios_lst, cover_dirs


def save_all(audios_lst, info):
    """save infos to all files in this album and move to dest"""
    logger.debug(f"<{info['rjcode']}> info is {info}")
    for each in audios_lst:
        try:
            if each.tags is None:
                each.add_tags()
            for k, v in info.items():
                each.tags[k] = v
            # 可以直接先使用each.delete()删掉所有标签,
            # 以防商家打的标签存在乱码, 但是delete方法
            # 会单独保存一次,且会不必要的删除封面,可能很慢
            # 乱码中,影响最大的是title字段,所以直接清空这一个字段就可以
            each['title'] = ''
            each.save()
        except Exception:
            logger.error(f"<{info['rjcode']}> 保存出错!")
            logger.debug(traceback.format_exc())
            return False
    return True


def main(args):
    rjcode, root, options = args
    try:
        audios_lst, cover_dirs = update_audios(rjcode, root)
    except FunctionRet:
        return
    info = {
        "doujin": "1",
        "rjcode": rjcode,
        "comment":
        "Tagged By github.com/maybeRainH/doujin_tagger"}
    cov_data = io.BytesIO()
    coverp = options.cover
    if not fetch_info(info, cov_data, coverp, options.proxy, options.lang):
        return
    if coverp:
        cover2dir(cover_dirs, cov_data)
    if not save_all(audios_lst, info):
        return
    move_to(root, options.dest, info)
