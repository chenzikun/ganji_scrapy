from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import requests

class Constant:

    # url_str = 'http://www.kuaidaili.com/free/inha/{index}/'
    urls = ['http://www.kuaidaili.com/free/inha/{index}/'.format(index=i) for i in range(1, 2)]

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
               'Accept': 'text / html, application / xhtml + xml',
               'Referer': 'http://www.kuaidaili.com/free/inha/7/',
           }

    driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')


def create_soup(url):
    Constant.driver.get(url)
    sleep(1)
    response = Constant.driver.page_source
    soup = BeautifulSoup(response, 'lxml')
    return soup

def create_ip_items(soup):
    ips_and_ports = soup.find('tbody').findAll('tr')
    for item in ips_and_ports:
        ip = item.find('td', {'data-title': "IP"}).text
        port = item.find('td', {'data-title': "PORT"}).text
        ip_instance = Ip(ip=ip, port=port)
        yield ip_instance


class Ip:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class Ips:
    def __init__(self):
        self.items = []
        self.collect_ip()

    def collect_ip(self):
        for pagination_url in Constant.urls:
            try:
                pagination_soup = create_soup(pagination_url)
                pagination_ips = create_ip_items(pagination_soup)
                for ip_instance in pagination_ips:
                    proxies = {'http:': 'http://{}:{}'.format(ip_instance.ip, ip_instance.port)}
                    resp = requests.get('http://sz.ganji.com/', proxies=proxies)
                    if resp:
                        print('有效ip')
                        self.items.append(ip_instance)
                    else:
                        print('w无效ip')
                        continue
            except:
                sleep(10)


ip_pond = Ips().items

from atexit import register
@register
def _at_exit():
    print('ip池采集完毕：共获取{}个有效代理ip'.format(len(ip_pond)))
    Constant.driver.close()
