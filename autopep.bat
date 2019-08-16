echo off
echo "starting"
autopep8 -v -i src\doujin_tagger\__init__.py
autopep8 -v -i src\doujin_tagger\artwork.py
autopep8 -v -i src\doujin_tagger\audio.py
autopep8 -v -i src\doujin_tagger\cmdline.py
autopep8 -v -i src\doujin_tagger\id3.py
autopep8 -v -i src\doujin_tagger\image.py
autopep8 -v -i src\doujin_tagger\main.py
autopep8 -v -i src\doujin_tagger\mp4.py
autopep8 -v -i src\doujin_tagger\spider.py
autopep8 -v -i src\doujin_tagger\util.py
autopep8 -v -i src\doujin_tagger\xiph.py
autopep8 -v -i test\test_spider.py --ignore E501
autopep8 -v -i test\test_util.py
autopep8 -v -i test\test_concrete.py
autopep8 -v -i test\test_audio.py

isort -v -i src\doujin_tagger\__init__.py
isort -v -i src\doujin_tagger\artwork.py
isort -v -i src\doujin_tagger\audio.py
isort -v -i src\doujin_tagger\cmdline.py
isort -v -i src\doujin_tagger\id3.py
isort -v -i src\doujin_tagger\image.py
isort -v -i src\doujin_tagger\main.py
isort -v -i src\doujin_tagger\mp4.py
isort -v -i src\doujin_tagger\spider.py
isort -v -i src\doujin_tagger\util.py
isort -v -i src\doujin_tagger\xiph.py
isort -v -i test\test_spider.py --ignore E501
isort -v -i test\test_util.py
isort -v -i test\test_concrete.py
isort -v -i test\test_audio.py
pause
