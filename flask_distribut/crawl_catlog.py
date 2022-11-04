# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 14:17 
思路：
"""
import requests
from lxml import etree
import cchardet
import logging
import time

from api_handler import insert_task
from config import URL, HEADERS

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S', )
file_handler = logging.FileHandler("biquge.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def crawl_catalog(area, page, header=None):
    """
    写入目录
    @param page:
    @param header:
    @return:
    """
    url = URL.format(area, page)
    headers = header if header else HEADERS
    while True:
        try:
            has_next_page = True
            response = requests.get(url, headers=headers)
            encoding = cchardet.detect(response.content)['encoding']
            html = response.content.decode(encoding)
            dom = etree.HTML(html)
            items = dom.xpath('//div[@class="clearfix rec_rullist"]/ul')
            for item in items:
                novel_url = item.xpath('./li[@class="two"]/a/@href')[0]
                name = item.xpath('./li[@class="two"]/a/text()')[0][:-4]
                catalog = {
                    "name": name,
                    "url": novel_url
                }
                insert_task("catalog", catalog)
                catalog['last_crawl_time'] = 0
                catalog['status'] = 0
                insert_task("catalog_task", catalog)
            if not dom.xpath('//a[@class="next"]'):
                has_next_page = False
            return has_next_page
        except Exception as e:
            logger.exception(e)
            time.sleep(1)


def run():
    """
    图书抓取
    @return:
    """
    # 图书种类1-9
    areas = [1, 2, 3]
    logger.info('start...')
    for area in areas:
        page = 1
        while page <= 3:
            logger.info('page: {} ......'.format(page))
            try:
                has_next_page = crawl_catalog(area, page)
                if not has_next_page:
                    break
            except Exception as e:
                logger.exception(e)
            page += 1
    logger.info('finish .....')
    

if __name__ == '__main__':
    run()
