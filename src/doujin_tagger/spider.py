# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import datetime
import logging
import re

import requests
from lxml.etree import HTML
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger("doutag.spider")
TIMEOUT = 10

se = requests.Session()
adapter = HTTPAdapter(max_retries=Retry(backoff_factor=0.3, total=3))
se.mount('http://', adapter)
se.mount('https://', adapter)


USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
              "(KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")

JP_TRANSDICT = {
    "販売日": "date",
    "声優": "artist",
    "年齢指定": "nsfw",
    "ジャンル": "genre",
    "シリーズ名": "series",
}

CN_TRANSDICT = {
    "贩卖日": "date",
    "声优": "artist",
    "年龄指定": "nsfw",
    "分类": "genre",
    "系列名": "series",
}

TRANSDICTS = [JP_TRANSDICT, CN_TRANSDICT]
LANG_H = ["ja;q=1", "zh-CN,zh;q=1"]


def spider_dlsite(info, cov_data, coverp, proxy, lang):
    logger.debug(f"<{info['rjcode']}> scraping [DLSITE]")
    dlsite_header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa
    "Accept-Language": LANG_H[lang],
    "Cookies": "adultchecked=1",
    "User-Agent": ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/"
                   "537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/"
                   "537.36")
    }
    cov_headers = {
        "User-Agent": USER_AGENT,
        "Host": "img.dlsite.jp",
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    rjcode = info['rjcode']
    url = f"http://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"
    try:
        res = se.get(url, headers=dlsite_header,
                     timeout=TIMEOUT, proxies=proxies)
    except requests.exceptions.RequestException as e:
        logger.error(f"<{rjcode}> [DLSITE] {e!r}")
        return

    if res.status_code == 404:
        logger.warning(f"<{rjcode}> [Dlsite] INFO NotFound")
        return

    html = HTML(res.text)
    for each in html.xpath("//*[@id='work_outline']/descendant::tr"):
        info_name = each.xpath("th/text()")[0]
        info_attr = each.xpath("td/descendant::*/text()")
        if info_name in TRANSDICTS[lang]:
            info[TRANSDICTS[lang][info_name]] = info_attr
    info["maker"] = html.xpath("//*[@class='maker_name']/a/text()")
    info["album"] = html.xpath("//*[@id='work_name']/a/text()")
    if coverp:
        img_url = html.xpath("//img[@itemprop='image']/@src")
        img_url = img_url[0] if img_url else ''
        if "no_img" in img_url:
            logger.debug("[Dlsite] No Cover Found")
        elif img_url:
            try:
                r = se.get("https:" + img_url, timeout=TIMEOUT,
                           headers=cov_headers)
                r.raise_for_status()
                cov_data.write(r.content)
            except Exception as e:
                logger.error(f"<{rjcode}> [DLSITE] COVERDL ERROR")
                logger.debug(f"COVERDL: {e!r}")
    process_dlsite_info(info)


def spider_hvdb(info, cov_data, coverp, proxy, lang):
    """当dlsite找不到artist爬取hvdb作为补充"""

    if 'artist' in info and not info['artist']:
        return
    logger.debug(f"<{info['rjcode']}> scraping [HVDB]")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    rjcode = info['rjcode'][2:]
    url = f"http://hvdb.me/Dashboard/WorkDetails/{rjcode}"
    try:
        res = se.get(url, timeout=TIMEOUT, proxies=proxies)
    except requests.exceptions.RequestException as e:
        logger.error(f"<{rjcode}> [HVDB] {e!r}")
        return
    if res.status_code == 500:
        logger.warning(f"<{rjcode}> [HVDB] NotFound")
        return

    html = HTML(res.text)
    pat = html.xpath("//input[@name='CVsString']/@value")
    pat = pat[0] if pat else ''
    # 可能存在声优第一个字符也是ASCII?
    info['artist'] = [each for each in pat.split(
        ',') if each and not each[0].isascii()]


def process_dlsite_info(info):
    """modified info dict in place"""
    for key, val in info.items():
        if key == "date":
            try:
                date_tuple = re.search(r"(\d+)年(\d+)月(\d+)日", val[0]).groups()
                fmt_date = datetime.datetime(*map(int, date_tuple))
                res = fmt_date.strftime("%Y-%m")
                # keep it a list for consistency
                info[key] = [res, ]
            except (AttributeError, TypeError) as e:
                logger.warning("PROCESS DATE ERROR")
                logger.debug(e)
                info[key] = ["", ]
        elif key in ("genre", "artist"):
            new = []
            for each in val:
                temp = each.strip()
                each = each.replace("/", "").strip()
                if each:
                    new.append(temp)
            info[key] = new
