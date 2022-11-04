# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 16:08
思路：
"""
import requests
from lxml import etree
import cchardet
import logging
import time

from api_handler import get_task, insert_task, update_task
from config import HEADERS

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S', )
file_handler = logging.FileHandler("biquge.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def crawl_novel(task, header=None):
    """
    根据目录信息提取对应的章节信息
    @param task:
    @param header:
    @return:
    """
    headers = header if header else HEADERS
    try_times = 3
    while try_times > 0:
        try_times -= 1
        try:
            url = task['url']
            response = requests.get(url, headers=headers)
            encoding = cchardet.detect(response.content)['encoding']
            html = response.content.decode(encoding)
            dom = etree.HTML(html)
            items = dom.xpath('//ul[@class="mulu_list"]/li')
            for item in items:
                novels = {
                    "catalog_url": url,
                    "url": url + item.xpath('./a/@href')[0],
                    "novel_name": item.xpath('./a/text()')[0]
                }
                insert_task("novels", novels)
                update_task("catalog", task, 1, logger)
                novels['last_crawl_time'] = 0
                novels['status'] = 0
                insert_task("novels_task", novels)
            return True
        except Exception as e:
            logger.exception(e)
            time.sleep(1)
    

def run():
    while True:
        try:
            task = get_task('catalog_task', logger)
            if not task:
                logger.info('finish crawl all task')
                return
            
            t0 = time.time()
            crawl_novel(task)
            info = "finish crawl url:%s, t_diff:%s" % (task['url'], time.time() - t0)
            logger.info(info)
        except Exception as e:
            logger.exception(e)
            time.sleep(3)


if __name__ == '__main__':
    run()
