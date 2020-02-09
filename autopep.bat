echo off
echo "starting"
autopep8 -v -i src\doujin_tagger\__init__.py
autopep8 -v -i src\doujin_tagger\artwork.py
autopep8 -v -i src\doujin_tagger\cmdline.py
autopep8 -v -i src\doujin_tagger\main.py
autopep8 -v -i src\doujin_tagger\spider.py
autopep8 -v -i src\doujin_tagger\logger.py
autopep8 -v -i src\doujin_tagger\util.py
autopep8 -v -i test\test_spider.py --ignore E501
autopep8 -v -i test\test_util.py

isort src\doujin_tagger\__init__.py
isort src\doujin_tagger\artwork.py
isort src\doujin_tagger\cmdline.py
isort src\doujin_tagger\main.py
isort src\doujin_tagger\spider.py
isort src\doujin_tagger\util.py
isort src\doujin_tagger\logger.py
isort test\test_spider.py
isort test\test_util.py
pause
