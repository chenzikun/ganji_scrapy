from multiprocessing import Process

from .utils import Util
from .proxy_verify import VerifyProxy
from .db import RedisDatabase


class GetFreeProxy(object):
    def __init__(self):

        self.util = Util()

        self.ip_pond = []

    # 快代理
    def free_proxy_first_source(self):
        pass

    # 抓取代理66 http://www.66ip.cn/
    def free_proxy_second_source(self):
        url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea="
        for index in range(1, 50):
            try:
                dom = self.util.get_dom(url.format(str(index)))
                ips = dom('body').text().split(' ')
                for item in ips:
                    ip, port = item.strip().split(':')
                    self.ip_pond.append((ip, port))
            except Exception as e:
                print(e)

    # 有代理
    def free_proxy_third_source(self):
        url = "http://www.youdaili.net/Daili/http/"
        dom = self.util.get_dom(url)
        target_url = list(dom('.chunlist')('ul')('li').items())[0]('a').attr('href')
        dom_ = self.util.get_dom(target_url)
        ip_list = dom_('.content')('p')
        for item in ip_list.items():
            try:
                ip, port = item.text().split('@')[0].strip().split(':')
                self.ip_pond.append((ip, port))
            except Exception as e:
                print(e)

    # 抓取西刺代理 http://api.xicidaili.com/free2016.txt
    def free_proxy_fourth_source(self):
        url = "http://www.xicidaili.com/"
        dom = self.util.get_dom(url)
        ip_list = list(dom('#ip_list')('tbody')('tr').items())[2:20]
        for item in ip_list:
            try:
                ip = list(item('th').items)[1].strip()
                port = list(item('th').items)[2].strip()
                self.ip_pond.append((ip, port))
            except Exception as e:
                print(e)

    # 抓取全网代理ip
    def free_proxy_fifth_source(self):
        url = "http://www.goubanjia.com/free/gngn/index.shtml"
        dom = self.util.get_dom(url)
        ip_list = dom('.table')('.ip')
        for td in ip_list.items():
            try:
                text = ''.join(item.text() for item in td.items()).strip()
                ip, port = text.split(':')
                self.ip_pond.append((ip, port))
            except Exception as e:
                print(e)


class IpPondManager(object):
    def __init__(self):
        self.redis_db = RedisDatabase()

        self.free_proxy = GetFreeProxy()
        self.verify_hook = VerifyProxy()

        self.target_list = [self.free_proxy.free_proxy_second_source(), self.free_proxy.free_proxy_third_source(),
                            self.free_proxy.free_proxy_fourth_source(), self.free_proxy.free_proxy_fifth_source()]

        self.num = 0

    def main(self):
        process_list = [Process(target=item, args=()) for item in self.target_list]
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()
        self.redis_db.refresh_ip_pond(self.free_proxy.ip_pond)
        if self.num == 0:
            self.verify_hook.main()
            self.num = 1
