import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'spider_ppw.settings')
from datetime import datetime
from atexit import register
from time import sleep

# 计划任务
from apscheduler.schedulers.blocking import BlockingScheduler

from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
from spider_ppw.spiders.ganji import GanJiSpider
from spider_ppw.constant import proxy_verify
from spider_ppw.constant import ip_pond


class Main(object):

    def __init__(self):
        # ip池爬取次数计数
        self.ip_pond_num = 0
        # ip池验证计数数
        self.verify_ip_pond_num = 0
        # 主爬虫运行计数
        self.crawl_num = 0

        self.process = CrawlerProcess(settings)
        self.process.crawl(GanJiSpider)

    @staticmethod
    def print_(text):
        print('#' * 60)
        print(format(text, '#^55s'))
        print('#' * 60)

    @staticmethod
    def date_time():
        return datetime.now().strftime('%H:%M:%S')

    def refresh_ip_pond(self):
        self.ip_pond_num += 1
        self.print_('  第{}次更新ip_pond: {}  '.format(self.ip_pond_num, self.date_time()))
        ip_pond.Manager()

    def test_ip_pond(self):
        self.verify_ip_pond_num += 1
        self.print_('  第{}次更新ip_pond: {}  '.format(self.verify_ip_pond_num, self.date_time()))
        proxy_verify.VerifyProxy()

    def crawl(self):
        self.crawl_num += 1
        self.process._stop_reactor()
        self.process.start()
        self.print_('  第{}次进行主爬虫程序: {}  '.format(self.crawl_num, self.date_time()))

    def first_start(self):
        self.refresh_ip_pond()
        sleep(120)
        self.test_ip_pond()


if __name__ == '__main__':
    main = Main()
    sched = BlockingScheduler()
    sched.add_job(main.refresh_ip_pond, trigger='cron', minute="*/60", hour="7-23", day="*")
    sched.add_job(main.test_ip_pond, trigger='cron', minute="*/20", hour="7-23", day="*")
    sched.add_job(main.crawl, trigger='cron', minute="*/10", hour="7-23", day="*")
    main.first_start()
    try:
        main.print_('开始计划任务: {}'.format(main.date_time()))
        sched.start()
    except Exception as e:
        print(e)
        main.print_('计划任务终止 : {}'.format(main.date_time()))


@register
def _at_exit():
    main.print_('    爬虫结束：{}    '.format(main.date_time()))


# if __name__ == '__main__':
#     main = Main()
#     main.crawl()
