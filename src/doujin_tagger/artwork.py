import os
import re
import shutil
import logging
import traceback
from pathlib import Path

from doujin_tagger import spider
from doujin_tagger.id3 import ID3File, MP3File  # noqa
from doujin_tagger.mp4 import MP4File  # noqa
from doujin_tagger.util import dl_cover, find_inner_most
from doujin_tagger.xiph import *  # noqa
from doujin_tagger.audio import AudioFile, DictMixin, AudioFileError
from doujin_tagger.image import EmbeddedImage

logger = logging.getLogger("doutag.artwork")

# \u30FB : Katakana Middle Dot
# \u301c : Wave Dash
# \uFF5E : Fullwidth Tilde (no problem)
# \u2600-\u26ff : Misc Sym
REFMT_REGISTRY = "|".join(AudioFile._registry)
AUDIO_PAT = re.compile(fr".*\.({REFMT_REGISTRY})$")
UNSUPPORT_PAT = re.compile(r".*\.(wav|ape)$")
ILLEGAL_PAT = re.compile(r"[\\/:*?\"<>|\r\n\u30FB\u301c\u2600-\u26ff]+")


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

    fields = {"album", "tags"}

    def __init__(self, rjcode, work_path, dest):
        self.rjcode = rjcode
        self.work_path = Path(work_path)
        self.dest = Path(dest)
        self.logger = MyLogger(logger, {"ref": self})
        self.audios = []  # AufioFile objs
        self.cover = b''  # store binary data of image
        # <doujin> tag is always set to "1" to distinguish with normal music
        self.info = DictMixin({"doujin": "1", "rjcode": rjcode})

    def update_audios(self):
        for root, _, files in os.walk(self.work_path):
            for eachfile in files:
                if UNSUPPORT_PAT.match(eachfile):
                    self.logger.error("UNSUPPORT FMT FOUND")
                    return False
                elif AUDIO_PAT.match(eachfile):
                    full_path = os.path.join(root, eachfile)
                    try:
                        self.audios.append(AudioFile(full_path))
                    except AudioFileError as e:
                        self.logger.error(f"LOADING ERROR --> {eachfile}")
                        self.logger.debug(traceback.format_exc())
                        return False
        if not self.audios:
            self.logger.error("AUDIOS NOT FOUND")
            return False
        return True

    def __len__(self):
        return len(self.audios)

    def _recur_del_and_move(self):
        # make sure this is the last thing to do
        # because we don't want to keep track of the filenames after moving
        dir_name = f"{self.rjcode} {self.info['album']}"
        dir_name = ILLEGAL_PAT.sub("", dir_name)
        full_name = self.dest / dir_name
        path_to_move = find_inner_most(self.work_path)
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
        return not (self.fields - self.info.keys())

    def fetch_and_feed(self, proxy, cover=True, lang=0):
        """give info fetched by spiders to each `AudioFile`"""
        # spider 是一个dict似乎没用
        # 另外,这种机制真的好吗,不过似乎可以先放着,等学会了scrapy再说
        for k, func in self.spiders.items():
            self.info = func(self.info, proxy, lang)
        for each in self.audios:
            each.feed(self.info)
        if cover:
            self.logger.debug("getting cover")
            image_url = self.info.get("image_url")
            if not image_url:
                self.logger.warning("Cover Not Found")
            else:
                self.cover = dl_cover(image_url)

    def delete_all(self):
        """delete all files' tags in this album"""
        for each in self.audios:
            each.delete_all_tags()
        self.logger.debug(f"[{len(self)}] files info deleted")

    def save_all(self):
        """save infos to all files in this album and move to dest"""
        self.logger.debug(f"self.info is {self.info}")

        if not self._check_field():
            self.logger.error("INFO UNCOMPLETE, CHECK SPIDER LOG")
            return False

        if not self.cover:
            return False
        for each in self.audios:
            try:
                img = EmbeddedImage(self.cover)
                each.set_image(img)
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
