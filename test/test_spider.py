# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
from unittest.mock import Mock, patch

import pytest
from requests import Session

from doujin_tagger.spider import spider_dlsite

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')

params = [
    ("RJ234446.html", {
        "artist": ["琴香", "箱河ノア", "藤堂れんげ"],
        "album":["【大人向け耳かき】道草屋 はこべら5 時計修理のはこべらさん。他【汗の匂い】"],
        "nsfw":["18禁"],
        "date":["2018-09"],
        "maker":["桃色CODE"],
        "genre":["ローション", "耳かき", "耳舐め"],
        "series":["【耳かき】道草屋【安眠】"],
    }),
    # no artist, no series
    ("RJ202459.html", {
        'album': ['オナ指示、オナサポボイス10本セット(CV 如月なずな様10)'],
        'nsfw':["18禁"],
        'date':["2017-06"],
        'maker':['アイボイス'],
        'genre':['淫語', 'オナニー', '言葉責め', '逆レイプ', '童貞', '包茎'],
        'series': ['如月なずなさん作品'],
    }),
]


class FakeArtWork:
    # if we import artwork, which will import mutagen
    # I wish tox will run without mutagen installed.
    def __init__(self, rjcode, work_path, dest):
        self.rjcode = rjcode
        self.work_path = work_path
        self.dest = dest
        self.info = {
            "doujin": "1",
            "rjcode": rjcode,
            "comment":
            "Tagged By github.com/maybeRainH/doujin_tagger"}


class TestDlsiteParse:
    @patch.object(Session, 'get')
    @pytest.mark.parametrize('name,expected', params)
    def test_dlsite_output(self, mock_get, name, expected):
        uri = os.path.join(DATA, name)
        with open(uri, 'rb') as f:
            content = f.read()
        resp = Mock()
        resp.status_code = 200
        resp.text = content
        mock_get.return_value = resp
        artwork = FakeArtWork(name[:name.index('.')], 'fakepth', 'fakedest')
        spider_dlsite(artwork, {}, True, 0)
        info = artwork.info
        info.pop('rjcode')
        info.pop('comment')
        info.pop('doujin')
        assert info == expected
