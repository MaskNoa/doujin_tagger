import re
import json
import logging
from os import path
from multiprocessing import Pool, freeze_support

from doujin_tagger.util import match_path
from doujin_tagger.artwork import ArtWork
from doujin_tagger.cmdline import banner, cmd_parser

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
filelog = logging.FileHandler(
    path.expanduser("~/dt_info.txt"), encoding="utf-8")
filelog.setLevel(logging.DEBUG)
fileformatter = logging.Formatter(
    "%(asctime)s %(name)-8s %(funcName)-13s| %(levelname)-8s | %(message)s",
    datefmt="[%Y-%m-%d %H:%M]")
filelog.setFormatter(fileformatter)
ch = logging.StreamHandler()
chformatter = logging.Formatter(
    "%(funcName)-16s| %(levelname)-8s | %(message)s")
ch.setFormatter(chformatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.addHandler(filelog)

RJPAT = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)

def worker(args):
    rjcode, root, dest, cover, lang, proxy = args
    a = ArtWork(rjcode, root, dest)
    a.fetch_and_feed(proxy, cover, lang)
    a.save_all()


def main():
    banner()
    options = cmd_parser()
    logger.info("starting")
    work_list = [(rjcode, root, options.dest, options.cover, options.lang, options.proxy)
                 for rjcode, root in match_path(options.orig, RJPAT)]
    if not work_list:
        logger.info("no match found")
        return
    if options.debug:
        for args in work_list:
            worker(args)
    else:
        with Pool() as pool:
            pool.map(worker, work_list)


if __name__ == '__main__':
    freeze_support()
    main()
