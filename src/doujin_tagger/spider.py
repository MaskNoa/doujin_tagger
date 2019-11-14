import time
import logging

import requests
from lxml.etree import HTML
from doujin_tagger.util import process_dlsite_info

logger = logging.getLogger(__name__)

JP_TRANSDICT = {
    "販売日": "date",
    "声優": "artist",
    "年齢指定": "nsfw",
    "ジャンル": "tags",
    "シリーズ名": "series",
}

CN_TRANSDICT = {
    "贩卖日": "date",
    "声优": "artist",
    "年龄指定": "nsfw",
    "分类": "tags",
    "系列名": "series",
}
TRANSDICTS = [JP_TRANSDICT, CN_TRANSDICT]
LANG_H = ["ja;q=1", "zh-CN,zh;q=1"]
LANGS = ['JP', 'CN']

# info now is DictMixin


def spider_dlsite(info, proxy, lang=0):
    logger.info(f"scraping [DLSITE] [{LANGS[lang]}]")
    dlsite_header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa
    "Accept-Language": LANG_H[lang],
    "Cookies": "adultchecked=1",
    "User-Agent": ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/"
                   "537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/"
                   "537.36")
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    rjcode = info["rjcode"]
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"
    maxtries = 3
    while maxtries:
        try:
            res = requests.get(url, headers=dlsite_header,
                               timeout=10, proxies=proxies)
            break
        except requests.Timeout:
            logger.error(f"<{rjcode}> Timeout, RETRING [{maxtries}]")
            time.sleep(1)
            maxtries -= 1
            continue
        except requests.ConnectionError as e:
            logger.error(repr(e) + f"<{rjcode}> RETRING [{maxtries}]")
            time.sleep(1)
            maxtries -= 1
            continue
    else:
        logger.error(f"<{rjcode}> Maxtries Reached")
        return info

    if res.status_code == 404:  # status_code's type is int, not str
        logger.error(f"<{rjcode}> NotFound On Dlsite")
        return info

    html = HTML(res.text)
    for each in html.xpath("//*[@id='work_outline']/descendant::tr"):
        info_name = each.xpath("th/text()")[0]
        info_attr = each.xpath("td/descendant::*/text()")
        if info_name in TRANSDICTS[lang]:
            info[TRANSDICTS[lang][info_name]] = info_attr
    info["maker"] = html.xpath("//*[@class='maker_name']/a/text()")
    info["album"] = html.xpath("//*[@id='work_name']/a/text()")
    img_url = html.xpath("//img[@itemprop='image']/@src")
    if "no_img" in img_url:
        logger.debug("No Cover Found On Dlsite")
    else:
        info["image_url"] = img_url
    info = process_dlsite_info(info)
    return info


def spider_hvdb(info, proxy, lang=0):
    """当dlsite找不到artist爬取hvdb作为补充"""

    if 'artist' in info and not info['artist']:
        return info
    logger.info(f"scraping [HVDB]")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    rjcode = info["rjcode"][2:]
    url = f"http://hvdb.me/Dashboard/WorkDetails/{rjcode}"
    maxtries = 3

    while maxtries:
        try:
            res = requests.get(url, timeout=10, proxies=proxies)
            break
        except requests.Timeout:
            logger.error(f"<{rjcode}> Timeout, RETRING [{maxtries}]")
            time.sleep(1)
            maxtries -= 1
            continue
        except requests.ConnectionError as e:
            logger.error(repr(e) + f"<{rjcode}> RETRING [{maxtries}]")
            time.sleep(1)
            maxtries -= 1
            continue
    else:
        logger.error(f"<{rjcode}> Maxtries Reached")
        return info

    if res.status_code == 500:
        logger.error(f"<{rjcode}> NotFound On HVDB")
        return info

    html = HTML(res.text)
    pat = html.xpath("//input[@name='CVsString']/@value")
    if not pat:
        return info
    pat = pat[0]
    # 可能存在声优第一个字符也是ASCII?
    info['artist'] = [each for each in pat.split(
        ',') if each and not each[0].isascii()]
    return info
