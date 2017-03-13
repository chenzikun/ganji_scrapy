from time import sleep
import requests
import pyquery


class GetFreeProxy(object):

    util = Utils()

    # 快代理
    def free_proxy_first_source(self):
        urls = ['http://www.kuaidaili.com/free/inha/{index}/'.format(index=i) for i in range(1, 2)]
        for url in urls:
            dom=self.util.get_dom(url)
            ips = dom('')
        pass

    # 抓取代理66 http://www.66ip.cn/
    def free_proxy_second_source(self):
        url_str = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea="
        urls = [url_str.format(i) for i in range(1, 100)]
        for url in urls:
            dom = self.util.get_dom(url)
            ip, port=dom('body').text().split(':')
            yield ip, port

    # 有代理
    def free_proxy_third_source(self):
        url = "http://www.youdaili.net/Daili/http/"
        dom = self.util.get_dom(url)
        target_url = list(dom('.chunlist')('ul')('li').items())[0]('a').attr('href')
        dom_ = self.util.get_dom(url)
        ip_list = dom_('.content')('p')
        for item in ip_list.items():
            ip, port = item.text().split('@')[0].split(':')
            yield ip, port

    # 抓取西刺代理 http://api.xicidaili.com/free2016.txt
    def free_proxy_fourth_source(self):
        url = "http://www.xicidaili.com/"
        dom = self.util.get_dom(url)
        ip_list = list(dom('#ip_list')('tbody')('tr').items())[2:15]
        for item in ip_list:
            ip = list(item('th').items)[1]
            port = list(item('th').items)[2]
            yield ip, port

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


from atexit import register
@register
def _at_exit():
    print('ip池采集完毕')
