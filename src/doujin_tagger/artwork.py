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

from mutagen import File, MutagenError, easyid3, easymp4

from . import spider
from .util import find_inner_most

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

logger = logging.getLogger("doutag.artwork")

# if you convent to some uncommon fmt, you are on your own
MP3EXTS = []
AUDIOEXTS = ["mp3", "m4a", "ogg", "flac"]
AUDIO_PAT = re.compile(fr".*\.({'|'.join(AUDIOEXTS)})$")
UNSUPPORT_PAT = re.compile(r".*\.(wav|ape)$")
ILLEGAL_PAT = re.compile(r"[\\/:*?\"<>|\r\n]+")


class MyLogger(logging.LoggerAdapter):
    '''add rjcode prompt in the front of logger message'''

    def process(self, msg, kwargs):
        return "<{0.rjcode}> {1!s}".format(self.extra["ref"], msg), kwargs


class ArtWork:
    """one logical album superset with many `AudioFile`s inside"""

    # register all spider functions in spider module
    spiders = {}
    for k, v in vars(spider).items():
        if k.startswith("spider") and callable(v):
            spiders[k] = v

    fields = {"album", "genre"}

    def __init__(self, rjcode, work_path, dest):
        self.rjcode = rjcode
        self.work_path = Path(work_path)
        self.dest = Path(dest)
        self.logger = MyLogger(logger, {"ref": self})
        self.audios = []
        self.cover = b''  # store binary data of image
        # <doujin> tag is always set to "1" to distinguish with normal music
        self.info = {
            "doujin": "1",
            "rjcode": rjcode,
            "comment":
            "Tagged By github.com/maybeRainH/doujin_tagger"}

    def update_audios(self):
        dirs_need_cover = []
        for root, dirs, files in os.walk(self.work_path):
            audio_found = False
            for eachfile in files:
                if UNSUPPORT_PAT.match(eachfile):
                    self.logger.error("UNSUPPORT FMT FOUND")
                    return False
                elif AUDIO_PAT.match(eachfile):
                    audio_found = True
                    full_path = os.path.join(root, eachfile)
                    try:
                        f = File(full_path, easy=True)
                    except MutagenError:
                        self.logger.error(f"LOADING ERROR --> {eachfile}")
                        self.logger.debug(traceback.format_exc())
                        return False
                    assert f is not None
                    self.audios.append(f)
            else:
                if audio_found:
                    dirs_need_cover.append(Path(root))

        if not self.audios:
            self.logger.error("AUDIOS NOT FOUND")
            return False
        self.dirs_need_cover = dirs_need_cover
        self.logger.debug(f"dirs_need_cover: {len(self.dirs_need_cover)}")
        self.logger.debug(f"audios: {len(self.audios)}")
        return True

    def __len__(self):
        return len(self.audios)

    def _recur_del_and_move(self):
        # make sure this is the last thing to do
        # because we don't want to keep track of the filenames after moving
        dir_name = f"{self.rjcode} {self.info['album'][0]}"
        self.logger.debug(f'dir_name is {dir_name}')
        dir_name = ILLEGAL_PAT.sub("", dir_name)
        full_name = self.dest / dir_name
        path_to_move = find_inner_most(self.work_path)
        self.logger.info(f"moving to {full_name}")
        try:
            path_to_move.rename(full_name)
        except FileExistsError:
            self.logger.error("SAME DIR IN DEST FOUND!")
            return False
        except Exception as e:
            self.logger.error(f"{repr(e)}")
            self.logger.debug(traceback.format_exc())
            return False
        # rescan and remove all empty dir
        if self.work_path.exists():
            if any(i for i in self.work_path.rglob("*") if i.is_file()):
                self.logger.error("FILES REMAINING")
                return False
            else:
                shutil.rmtree(self.work_path)
        return True

    def _check_field(self):
        """make sure rjcode and album are present to complete rename process"""
        if (self.fields - self.info.keys()):
            self.logger.error("INFO UNCOMPLETE, CHECK SPIDER LOG")
            return False
        else:
            return True

    def fetch_and_feed(self, proxy, cover=True, lang=0):
        """give info fetched by spiders to each `AudioFile`"""
        for k, func in self.spiders.items():
            func(self, proxy, cover, lang)
        if not self._check_field():
            return False
        return True

    def delete_all(self):
        """delete all files' tags in this album"""
        for each in self.audios:
            each.delete()
        self.logger.debug(f"[{len(self)}] files info deleted")

    def save_all(self):
        """save infos to all files in this album and move to dest"""
        self.logger.debug(f"self.info is {self.info}")
        if self.cover:
            for eachdir in self.dirs_need_cover:
                cover_path = eachdir / "cover.jpg"
                if not cover_path.exists():
                    cover_path.write_bytes(self.cover)
        for each in self.audios:
            try:
                if each.tags is None:
                    each.add_tags()
                for k, v in self.info.items():
                    each.tags[k] = v
                each.save()
            except Exception:
                self.logger.error("EXCEPTION WHEN SAVING, ABORT!")
                self.logger.debug(traceback.format_exc())
                break
        else:
            # if no error
            if self._recur_del_and_move():
                # self.logger.info(f"Success! Saved [{len(self)}]")
                return True
        return False
