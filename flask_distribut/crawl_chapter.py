# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 17:26 
思路：
"""
import logging
import time
import requests
from lxml import etree
import cchardet

from config import HEADERS
from api_handler import get_task, insert_task, update_task

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S', )
file_handler = logging.FileHandler("biquge.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def crawl_chapter(t, header=None):
    chapter = {}
    headers = header if header else HEADERS
    try_times = 3
    while try_times > 0:
        try:
            url = t['url']
            response = requests.get(url, headers=headers)
            encoding = cchardet.detect(response.content)['encoding']
            html = response.content.decode(encoding)
            dom = etree.HTML(html)

            contents = dom.xpath('//div[@id="htmlContent"]/text()')
            # 数据清除 转化并清楚空白字符串
            contents1 = [content.strip() for content in contents]
            text = '\n'.join(contents1)
            chapter['url'] = t['url']
            chapter['chapters_content'] = text
            insert_task('chapter', chapter, logger)
            update_task('novels_task', t, 2, logger)
            break
        except Exception as e:
            info = 'url:%s, error:%s' % (t['url'], str(e))
            logger.info(info)


def run():
    while True:
        task = get_task('novels_task', logger)
        if not task:
            logger.info('finish crawl all tasks')
            return
        logger.info('url:{}'.format(task['url']))
        t0 = time.time()
        crawl_chapter(task)
        info = "finish crawl url:%s, t_diff:%s" % (task['url'], time.time() - t0)
        print(info)


if __name__ == '__main__':
    run()
