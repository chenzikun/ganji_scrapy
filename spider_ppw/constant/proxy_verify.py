from .db import RedisDatabase
import requests
from multiprocessing import Process


class VerifyProxy(object):

    def __init__(self):
        self.redis_db = RedisDatabase()

        self.ip_pond = self.redis_db.ip_pond()

        print('筛选前ip池个数： {}'.format(len(self.redis_db.ip_pond())))
        self.main()
        print('筛选后ip池个数： {}'.format(len(self.ip_pond)))
        self.redis_db.refresh_ip_pond(self.ip_pond)

    def very_proxy(self, ip, port):
        # print(ip, port)
        proxies = {"http": "http://{}:{}".format(ip, port),
                   "https": "https://{}:{}".format(ip, port)}
        try:
            r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=30, verify=False)
            if r.status_code == 200:
                print('#ip {}:{} 通过测试'.format(ip, port))
                self.ip_pond.append((ip, port))
        except Exception as e:
            print('#ip {}:{}'.format(ip, port),e)

    def main(self):
        process_list = [Process(target=self.very_proxy, args=(self.ip_pond[index]))
                        for index in range(len(self.ip_pond))]
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()
