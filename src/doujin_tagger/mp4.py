# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Credits:
# The code in this file is largely copied and modified from:
# https://github.com/quodlibet/quodlibet/blob/master/quodlibet/quodlibet/formats/mp4.py

from doujin_tagger.audio import AudioFile
from doujin_tagger.mp4_patch import MP4, MP4Cover
from doujin_tagger.util import AudioFileError, translate_errors


class MP4File(AudioFile, ext=["mp4", "m4a", "m4v", "3gp", "3g2", "3gp2"]):
    translate = {
        "\xa9nam": "title",
        "\xa9alb": "album",
        "\xa9ART": "artist",
        "\xa9day": "date",
        "\xa9cmt": "comment",
        "----:com.apple.iTunes:TAGS": "tags",
        "----:com.apple.iTunes:DOUJIN": "doujin",
        "----:com.apple.iTunes:MAKER": "maker",
        "----:com.apple.iTunes:NSFW": "nsfw",
        "----:com.apple.iTunes:RJCODE": "rjcode",
        "----:com.apple.iTunes:SERIES": "series"}
    rtranslate = {v: k for k, v in translate.items()}

    def __init__(self, filename):
        super().__init__(filename=filename)
        with translate_errors():
            self.audio = MP4(self["filename"])

    def save(self):
        for key in self:
            try:
                name = self.rtranslate[key]
            except KeyError:
                continue
            values = self.tolist(key)
            if name.startswith("----"):
                values = list(map(lambda v: v.encode("utf-8"), values))
            self.audio[name] = values

        with translate_errors():
            self.audio.save()

    def delete_all_tags(self):
        self.audio.delete()

    def set_image(self, image):
        with image:
            if image.mime_type == "image/jpeg":
                image_format = MP4Cover.FORMAT_JPEG
            elif image.mime_type == "image/png":
                image_format = MP4Cover.FORMAT_PNG
            else:
                raise AudioFileError(
                    f"mp4: Unsupported image format {image.mimi_type}")
            cover = MP4Cover(image.read(), image_format)
            self.audio["covr"] = [cover]
