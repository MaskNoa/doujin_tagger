# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


import io
import logging
from pathlib import Path

from mutagen import apev2

from .common import cover2dir, fetch_info, move_to

logger = logging.getLogger("doutag.S2T")


# Dlsite上卖的音频一般就mp3,wav,flac三种,这里另外包括了常见的格式
# 如果你经常转换的格式没有在里面,可以自行添加
# 这个方法是fb2k专用,所以像raw aac没有包含在内,因为fb2k本身支持不好
AUDIO_EXT = {".mp3", '.mp4', '.m4a', ".mpc",
             ".wav", ".wv", ".wma", ".wmv",
             ".ogg", ".oga", ".flac", ".oggflac", ".ogv", ".opus",
             ".tta", ".tak", ".ape"}


def update_audios(work_path):
    work_path = Path(work_path)
    cover_dirs = set()
    audios_lst = []
    for each in work_path.rglob('*'):
        if each.suffix in AUDIO_EXT:
            audios_lst.append(each)
            cover_dirs.add(each.parent)
    return audios_lst, cover_dirs


def save_all(audios_lst, info):
    logger.debug(f"<{info['rjcode']}> info is {info}")
    a = apev2.APEv2()
    a.update(info)
    # 和save2file的方法类似,将title置为空
    a['title'] = ''
    buf = io.BytesIO()
    a.save(buf)
    for each in audios_lst:
        tagfile = each.with_suffix(each.suffix + '.tag')
        try:
            tagfile.write_bytes(b'TAGFILE' + buf.getvalue())
        except OSError as e:
            logger.error("无法写入TAG文件")
            logger.debug(e)
            return False
        each.touch()
    return True


def main(args):
    rjcode, root, options = args
    audios_lst, cover_dirs = update_audios(root)
    if not audios_lst:
        logger.error(f"<{rjcode}> 找不到音频文件")
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
