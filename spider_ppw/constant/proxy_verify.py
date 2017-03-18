from time import sleep
from multiprocessing import Process

import requests

from .db import RedisDatabase
from .utils import Singleton


class VerifyProxy(metaclass=Singleton):

    def __init__(self):
        self.redis_db = RedisDatabase()

        self.collect_ips = []

    def ip_nums(self):
        num = len(self.redis_db.ip_pond())
        return num

    # process.join方法实现同样的作用，用于监听processes是否全部结束
    # def is_processed_finished(self, pros):
    #     try:
    #         if not any(map(lambda p: p.is_alive(), pros)):
    #             self.redis_db.refresh_ip_pond(self.redis_db.ip_pond)
    #             print('筛选后ip池个数： {}'.format(self.ip_nums()))
    #         else:
    #             print('ip池等待更新...')
    #             sleep(1)
    #             self.is_processed_finished(pros)
    #     except Exception as e:
    #         print(e)

    # 验证ip是否有效
    def very_proxy(self, ip, port):
        proxies = {"http": "http://{}:{}".format(ip, port),
                   "https": "https://{}:{}".format(ip, port)}
        try:
            r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=10, verify=False)
            if r.status_code == 200:
                self.collect_ips.append((ip, port))
        except Exception:
            pass

    def main(self):
        ip_pond = self.redis_db.ip_pond()

        process_list = [Process(target=self.very_proxy, args=(ip_pond.pop()))
                        for index in range(self.ip_nums())]
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()

        self.redis_db.refresh_ip_pond(self.collect_ips)
        self.collect_ips = []


