import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'spider_ppw.settings')
from datetime import datetime
from atexit import register

import redis

from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
from spider_ppw.spiders import GanJiSpider


process = CrawlerProcess(settings)


def date_time():
    return datetime.now().strftime('%H:%M:%S')


if __name__ == '__main__':
    process.crawl(GanJiSpider)
    print('!'*40)
    print('爬虫开始：{}'.format(date_time()))
    print('!' * 40)
    process.start()


@register
def _at_exit():
    # redis_conn = redis.StrictRedis.from_url(settings.get('REDIS_URL'))
    # redis_conn.flushdb()
    print('爬虫结束：{}'.format(date_time()))
