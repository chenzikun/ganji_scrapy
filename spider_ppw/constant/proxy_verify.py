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


