# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import io
import os
from unittest.mock import Mock, patch

import pytest
from doujin_tagger.spider import process_dlsite_info, spider_dlsite
from requests import Session

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
        info = {}
        info['rjcode'] = name[:name.index('.')]
        spider_dlsite(info, io.BytesIO(), False, '', 0)
        info.pop('rjcode')
        assert info == expected


def test_process_dlsite_info():
    info_date = {'date': ['2019年1月1日']}
    info_tags = {'genre': ['school', ' / ', 'ear cleaning  ',
                           ' \n /', ' / \n /', 'pure/love']}
    # now process_dlsite_info modify info_date in place
    process_dlsite_info(info_date)
    assert info_date['date'] == ['2019-01', ]
    process_dlsite_info(info_tags)
    assert info_tags['genre'] == ['school', 'ear cleaning', 'pure/love']
