# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import concurrent.futures
import logging
import re
import time

import doujin_tagger.logger  # noqa
from doujin_tagger.artwork import ArtWork
from doujin_tagger.cmdline import banner, cmd_parser
from doujin_tagger.util import match_path
from tqdm import tqdm

logger = logging.getLogger("doutag")
RJPAT = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)


def worker(args):
    rjcode, root, dest, cover, lang, proxy = args
    a = ArtWork(rjcode, root, dest)
    if not a.update_audios():
        return
    a.fetch_and_feed(proxy, cover, lang)
    a.delete_all()  # 原来的标签可能乱码，全部删除
    a.save_all()


def multi(work_list):
    pbar = tqdm(total=len(work_list), dynamic_ncols=True, ascii=True)

    def callback_fn(future):
        if not future.cancelled():
            future.result()
            pbar.update(1)
    executor = concurrent.futures.ThreadPoolExecutor(5)
    future_list = []
    for url in work_list:
        future = executor.submit(worker, url)
        future.add_done_callback(callback_fn)
        future_list.append(future)
    while True:
        try:
            time.sleep(1)
            if all(e.done() for e in future_list):
                break
        except KeyboardInterrupt:
            pbar.close()
            logger.critical("wait for threads to quit")
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
