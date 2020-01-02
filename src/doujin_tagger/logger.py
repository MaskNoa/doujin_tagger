import logging
from tqdm import tqdm
from os import path

logging.logThreads = 0
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger("doutag")
logger.setLevel(logging.DEBUG)
filelog = logging.FileHandler(
    path.expanduser("~/dt_info.txt"), encoding="utf-8")
filelog.setLevel(logging.DEBUG)
fileformatter = logging.Formatter(
    "%(asctime)s %(name)-8s %(funcName)-13s| %(levelname)-8s | %(message)s",
    datefmt="[%Y-%m-%d %H:%M]")
filelog.setFormatter(fileformatter)
logger.addHandler(filelog)


class TqdmHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write(msg)
        except Exception:
            self.handleError(record)
        self.flush()


tqch = TqdmHandler(tqdm)
tqchformatter = logging.Formatter(
    "%(funcName)-16s | %(levelname)-8s | %(message)s")
tqch.setFormatter(tqchformatter)
tqch.setLevel(logging.ERROR)
logger.addHandler(tqch)
