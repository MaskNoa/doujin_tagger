import re
import logging
from os import path
import concurrent.futures

from doujin_tagger.util import match_path
from doujin_tagger.artwork import ArtWork
from doujin_tagger.cmdline import banner, cmd_parser
import time


logging.logThreads = 0
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
    if a.update_audios() == 1:
        return
    a.fetch_and_feed(proxy, cover, lang)
    a.delete_all()  # 原来的标签可能乱码，全部删除
    a.save_all()


def multi(work_list):
    def fn(future):
        if not future.cancelled():
            future.result()
    executor =  concurrent.futures.ThreadPoolExecutor(5)
    future_list = []
    for url in work_list:
        future = executor.submit(worker,url)
        future.add_done_callback(fn)
        future_list.append(future)
    while True:
        try:
            time.sleep(1)
            if all(e.done() for e in future_list):
                break
        except KeyboardInterrupt:
            count = 0
            done = 0
            for e in future_list:
                if not e.done():
                    count += 1
                    e.cancel()
                else:
                    done += 1
            logger.info(f'cancel {count} work, done {done} work')
            break

     
def main():
    banner()
    options = cmd_parser()
    logger.info("starting")
    work_list = [(rjcode, root, options.dest, options.cover,
                  options.lang, options.proxy)
                 for rjcode, root in match_path(options.orig, RJPAT)]
    if not work_list:
        logger.info("no match found")
        return
    multi(work_list)


if __name__ == '__main__':
    main()
