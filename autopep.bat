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

isort -v
isort src\doujin_tagger\__init__.py
isort src\doujin_tagger\artwork.py
isort src\doujin_tagger\audio.py
isort src\doujin_tagger\cmdline.py
isort src\doujin_tagger\id3.py
isort src\doujin_tagger\image.py
isort src\doujin_tagger\main.py
isort src\doujin_tagger\mp4.py
isort src\doujin_tagger\spider.py
isort src\doujin_tagger\util.py
isort src\doujin_tagger\xiph.py
isort src\doujin_tagger\logger.py
isort test\test_spider.py
isort test\test_util.py
isort test\test_concrete.py
isort test\test_audio.py
pause
