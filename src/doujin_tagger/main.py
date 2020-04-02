import concurrent.futures
import importlib
import logging
import re
import time

from tqdm import tqdm

from . import logger  # noqa
from .cmdline import banner, cmd_parser
from .common import match_path

RJPAT = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)
mlogger = logging.getLogger("doutag")


def multi(module, work_list):
    pbar = tqdm(total=len(work_list), dynamic_ncols=True, ascii=True)

    def callback_fn(future):
        if not future.cancelled():
            future.result()
            pbar.update(1)
    executor = concurrent.futures.ThreadPoolExecutor(5)
    future_list = []
    for url in work_list:
        future = executor.submit(module.main, url)
        future.add_done_callback(callback_fn)
        future_list.append(future)
    while True:
        try:
            time.sleep(1)
            if all(e.done() for e in future_list):
                break
        except KeyboardInterrupt:
            pbar.close()
            mlogger.critical("等待线程退出,不要进一步操作")
            # 不准了
            # count = 0
            # done = 0
            for e in future_list:
                if not e.done():
                    # count += 1
                    e.cancel()
                # else:
                    # done += 1
            # mlogger.info(f'已取消{count}个任务')
            break


def main():
    banner()
    options = cmd_parser()
    try:
        module = importlib.import_module("doujin_tagger." + options.method)
    except ModuleNotFoundError:
        mlogger.error(f"方法{options.method}不存在")
        exit(1)
    work_list = [(rjcode, root, options)
                 for rjcode, root in match_path(options.orig, RJPAT)]
    if not work_list:
        mlogger.info("找不到匹配的音声专辑")
        exit(1)
    multi(module, work_list)


if __name__ == '__main__':
    main()
