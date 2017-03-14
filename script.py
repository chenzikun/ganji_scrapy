import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'spider_ppw.settings')
from datetime import datetime
from atexit import register
import redis

# 计划任务
from apscheduler.schedulers.blocking import BlockingScheduler


from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
from spider_ppw.spiders import GanJiSpider

from spider_ppw.constant import proxy_verify
from spider_ppw.constant import ip_pond


process = CrawlerProcess(settings)


def date_time():
    return datetime.now().strftime('%H:%M:%S')


# def test_ip_pond():
#     sched = BlockingScheduler()
#     sched.add_job(, 'interval', seconds=180)

if __name__ == '__main__':
    ip_pond.Manager()
    print('ip池爬取完毕')
    proxy_verify.VerifyProxy()

    # 爬取进程
    process.crawl(GanJiSpider)
    print('!'*40)
    print('爬虫开始：{}'.format(date_time()))
    print('!' * 40)
    process.start()


@register
def _at_exit():
    redis_conn = redis.StrictRedis.from_url(settings.get('REDIS_URL'))
    redis_conn.flushdb()
    print('爬虫结束：{}'.format(date_time()))
