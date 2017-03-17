# from time import sleep
import requests
import pyquery
from multiprocessing import Process

from .db import RedisDatabase


class GetFreeProxy(object):

    def __init__(self):
        self.util = Utils()

        self.ip_pond = []

    # 快代理
    def free_proxy_first_source(self):
        urls = ['http://www.kuaidaili.com/free/inha/{index}/'.format(index=i) for i in range(1, 3)]
        for url in urls:
            dom=self.util.get_dom(url)
            ips = dom('')
        pass

    # 抓取代理66 http://www.66ip.cn/
    def free_proxy_second_source(self):
        url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea="
        for index in range(1,50):
            dom = self.util.get_dom(url.format(str(index)))
            ips=dom('body').text().split(' ')
            for item in ips:
                ip, port = item.split(':')
                self.ip_pond.append((ip, port))

    # 有代理
    def free_proxy_third_source(self):
        url = "http://www.youdaili.net/Daili/http/"
        dom = self.util.get_dom(url)
        target_url = list(dom('.chunlist')('ul')('li').items())[0]('a').attr('href')
        dom_ = self.util.get_dom(target_url)
        ip_list = dom_('.content')('p')
        for item in ip_list.items():
            ip, port = item.text().split('@')[0].split(':')
            self.ip_pond.append((ip, port))

    # 抓取西刺代理 http://api.xicidaili.com/free2016.txt
    def free_proxy_fourth_source(self):
        url = "http://www.xicidaili.com/"
        dom = self.util.get_dom(url)
        ip_list = list(dom('#ip_list')('tbody')('tr').items())[2:20]
        for item in ip_list:
            ip = list(item('th').items)[1]
            port = list(item('th').items)[2]
            self.ip_pond.append((ip, port))

    # 抓取全网代理ip
    def free_proxy_fifth_source(self):
        url = "http://www.goubanjia.com/free/gngn/index.shtml"
        dom = self.util.get_dom(url)
        ip_list = dom('.table')('.ip')
        for td in ip_list.items():
            text = ''.join(item.text() for item in td.items())
            ip, port = text.split(':')
            yield ip, port


class Utils:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
               'Accept': 'text / html, application / xhtml + xml',
           }

    def get_dom(self, url):
        rep = requests.get(url=url, headers=self.headers, timeout=10).content
        dom = pyquery.PyQuery(rep)
        return dom


class Manager():
    def __init__(self):
        self.free_proxy = GetFreeProxy()

        self.redis_db = RedisDatabase()


        self.target_list = [self.free_proxy.free_proxy_second_source(), self.free_proxy.free_proxy_third_source(),
                            self.free_proxy.free_proxy_fourth_source(), self.free_proxy.free_proxy_fifth_source()]

        self.create_ip()
        self.redis_db.dump('ip_pond', self.free_proxy.ip_pond)


    def create_ip(self):
        process_list = [Process(target=item, args=()) for item in self.target_list]
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()
