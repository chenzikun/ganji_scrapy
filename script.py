import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'spider_ppw.settings')
from datetime import datetime
from atexit import register

# 计划任务
from apscheduler.schedulers.blocking import BlockingScheduler

from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
from spider_ppw.spiders.ganji import GanJiSpider
from spider_ppw.constant import proxy_verify
from spider_ppw.constant import ip_pond


process = CrawlerProcess(settings)


class Main(object):

    def __init__(self):
        # ip池爬取次数计数
        self.ip_pond_num = 0
        # ip池验证计数数
        self.verify_ip_pond_num = 0
        # 主爬虫运行计数
        self.crawl_num = 0

    @staticmethod
    def date_time():
        return datetime.now().strftime('%H:%M:%S')

    def refresh_ip_pond(self):
        self.ip_pond_num += 1
        print('第{}次更新ip_pond: {}'.format(self.ip_pond_num, self.date_time()))
        ip_pond.Manager()
        print('ip池爬取完毕')

    def test_ip_pond(self):
        self.verify_ip_pond_num += 1
        print('第{}次更新ip_pond: {}'.format(self.verify_ip_pond_num, self.date_time()))
        proxy_verify.VerifyProxy()
        print('ip池验证完毕')

    def crawl(self):
        self.crawl_num += 1
        print('#' * 60)
        print(format('  第{}次进行主爬虫程序: {}  '.format(self.crawl_num, self.date_time())), '#^60')
        print('#' * 60)
        process.crawl(GanJiSpider)
        process.start()


if __name__ == '__main__':
    main = Main()
    sched = BlockingScheduler()
    sched.add_job(main.refresh_ip_pond, 'interval', minutes=20)
    sched.add_job(main.test_ip_pond, 'interval', minutes=5)
    sched.add_job(main.crawl, 'interval', minutes=30)
    try:
        print('开始计划任务')
        sched.start()
    except Exception as e:
        print(e)
        print('计划任务终止')


@register
def _at_exit():
    print('#' * 60)
    print(format('    爬虫结束：{}    '.format(main.date_time()), '^60'))
    print('#' * 60)
