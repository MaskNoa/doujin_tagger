echo off
echo "starting"
autopep8 -v -i src\doujin_tagger\__init__.py
autopep8 -v -i src\doujin_tagger\cmdline.py
autopep8 -v -i src\doujin_tagger\main.py
autopep8 -v -i src\doujin_tagger\spider.py
autopep8 -v -i src\doujin_tagger\logger.py
autopep8 -v -i src\doujin_tagger\common.py
autopep8 -v -i src\doujin_tagger\save2ape.py
autopep8 -v -i src\doujin_tagger\save2file.py
autopep8 -v -i test\test_spider.py --ignore E501
autopep8 -v -i test\test_common.py

isort src\doujin_tagger\__init__.py
isort src\doujin_tagger\cmdline.py
isort src\doujin_tagger\main.py
isort src\doujin_tagger\spider.py
isort src\doujin_tagger\logger.py
isort src\doujin_tagger\common.py
isort src\doujin_tagger\save2ape.py
isort src\doujin_tagger\save2file.py
isort test\test_spider.py
isort test\test_common.py
pause
