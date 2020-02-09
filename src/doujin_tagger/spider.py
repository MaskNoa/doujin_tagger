# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import logging

import requests
from lxml.etree import HTML
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .util import LANG_H, LANGS, TRANSDICTS, USER_AGENT, process_dlsite_info

logger = logging.getLogger("doutag.spider")
TIMEOUT = 10

se = requests.Session()
adapter = HTTPAdapter(max_retries=Retry(backoff_factor=0.3, total=3))
se.mount('http://', adapter)
se.mount('https://', adapter)


def spider_dlsite(artwork, proxy, cover, lang):
    logger.info(f"scraping [DLSITE] [{LANGS[lang]}]")
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
    rjcode = artwork.rjcode
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"
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
            artwork.info[TRANSDICTS[lang][info_name]] = info_attr
    artwork.info["maker"] = html.xpath("//*[@class='maker_name']/a/text()")
    artwork.info["album"] = html.xpath("//*[@id='work_name']/a/text()")
    if cover:
        img_url = html.xpath("//img[@itemprop='image']/@src")
        img_url = img_url[0] if img_url else ''
        if "no_img" in img_url:
            logger.debug("[Dlsite] No Cover Found")
        elif img_url:
            try:
                r = se.get("https:" + img_url, timeout=TIMEOUT,
                           headers=cov_headers)
                r.raise_for_status()
                artwork.cover = r.content
            except requests.exceptions.RequestException as e:
                logger.error(f"<{rjcode}> [DLSITE] COVERDL ERROR")
                logger.debug(f"COVERDL: {e!r}")
                artwork.cover = b''
    else:
        artwork.cover = b''
    process_dlsite_info(artwork.info)


def spider_hvdb(artwork, proxy, cover, lang):
    """当dlsite找不到artist爬取hvdb作为补充"""

    if 'artist' in artwork.info and not artwork.info['artist']:
        return
    logger.info(f"scraping [HVDB]")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    rjcode = artwork.rjcode[2:]
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
    artwork.info['artist'] = [each for each in pat.split(
        ',') if each and not each[0].isascii()]
