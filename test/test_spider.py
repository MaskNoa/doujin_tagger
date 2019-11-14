import os
from unittest.mock import Mock, patch

import pytest
import requests
from doujin_tagger.audio import DictMixin
from doujin_tagger.spider import spider_dlsite

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')
INFO = DictMixin({"rjcode": "RJ0"})

params = [
    ("RJ234446.html", {
        "artist": ["琴香", "箱河ノア", "藤堂れんげ"],
        "album":["【大人向け耳かき】道草屋 はこべら5 時計修理のはこべらさん。他【汗の匂い】"],
        "nsfw":["18禁"],
        "date":["2018-09"],
        "maker":["桃色CODE"],
        "image_url":["//img.dlsite.jp/modpub/images2/work/doujin/RJ235000/RJ234446_img_main.jpg"],  # noqa
        "tags":["ローション", "耳かき", "耳舐め"],
        "series":["【耳かき】道草屋【安眠】"],
    }),
    # no artist, no series
    ("RJ202459.html", {
        'album': ['オナ指示、オナサポボイス10本セット(CV 如月なずな様10)'],
        'nsfw':["18禁"],
        'date':["2017-06"],
        'maker':['アイボイス'],
        'image_url':['//img.dlsite.jp/modpub/images2/work/doujin/RJ203000/RJ202459_img_main.jpg'],  # noqa
        'tags':['淫語', 'オナニー', '言葉責め', '逆レイプ', '童貞', '包茎'],
        'series': ['如月なずなさん作品'],
    }),
]


class TestDlsite:
    @pytest.mark.online
    def test_dlsite_404_online(self, caplog):
        spider_dlsite(INFO, {})
        # set `log_level = ERROR` in pytest.ini
        res = [record for record in caplog.records]
        assert len(res) == 1
        assert 'NotFound' in res[0].message

    @patch('requests.get')
    def test_dlsite_404(self, mock_req, caplog):
        resp = requests.Response()
        resp.status_code = 404
        mock_req.return_value = resp
        spider_dlsite(INFO, {})
        res = [record for record in caplog.records]
        assert len(res) == 1
        assert 'NotFound' in res[0].message

    @patch('requests.get')
    def test_dlsite_timeout(self, mock_req, caplog):
        mock_req.side_effect = requests.Timeout('mock timeout')
        spider_dlsite(INFO, {})
        res = [record for record in caplog.records]
        assert len(res) == 4
        assert 'Maxtries' in res.pop().message

    # a lot of resp object made by offline html file
    @patch('requests.get')
    @pytest.mark.parametrize('name,expected', params)
    def test_dlsite_output(self, mock_req, name, expected):
        uri = os.path.join(DATA, name)
        with open(uri, 'rb') as f:
            content = f.read()
        resp = Mock()
        resp.status_code = 200
        resp.text = content
        mock_req.return_value = resp
        mock_req.text = 'haha'
        info = DictMixin({'rjcode': name[:name.index('.')]})
        info = spider_dlsite(info, {})
        info.pop('rjcode')
        assert info.list_repr() == expected
