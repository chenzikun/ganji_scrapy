import re

from pyquery import PyQuery

from scrapy import Spider, Request

from ..items.ganji import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from ..common.db import MysqlDatabase
from ..common.db import RedisDatabase


class GanJiSpider(Spider):
    """
    采集数据subdomain, name, code 的解决方式
    赶集 name --> sub_domain
    公司 name --> code (table district)
    为了去重的提高检索效率，构建 code --> urls (table spiderdb)
    """
    name = 'ganji'

    db = MysqlDatabase()

    redis_db = RedisDatabase()

    domain_str = 'http://{}.ganji.com'

    start_urls = ['http://www.ganji.com/index.htm']

    # 列表页
    urls = set()

    # 采集列表页准备
    def parse(self, response):
        dom = PyQuery(response.body)
        for a in dom('.all-city')('a').items():
            link = a.attr('href')
            city = str(a.text())
            city_code = self.db.city_map.get(city)
            if city_code:
                sub_domain = link.split('//')[1].split('.')[0]
                self.db.sub_domain_to_city_code_map[sub_domain] = city_code
                url_transfer = 'http://{}.ganji.com/fang6/a1c1/'.format(sub_domain)
                url_rent_out = 'http://{}.ganji.com/fang6/a1c2/'.format(sub_domain)
                url_rent_in = 'http://{}.ganji.com/fang6/a1s2/'.format(sub_domain)
                url_division = [url_transfer, url_rent_out, url_rent_in]
                for url in url_division:
                    yield Request(url, callback=self.list_page_parse)

    # 采集列表页
    def list_page_parse(self, response):
        sub_domain = response.request.url.split('.')[0].strip('http://')
        city_code = self.db.sub_domain_to_city_code_map.get(sub_domain)
        dom = PyQuery(response.body)
        # 翻页
        for li in dom('.pageLink.clearfix')('li').items():
            list_url = li('a').attr('href')
            if list_url not in self.urls and list_url is not None:
                # 只采集前2个列表页
                if li('span').text() <= '2':
                    target_url = self.domain_str.format(sub_domain) + list_url
                    self.urls.add(target_url)
                    yield Request(target_url, callback=self.list_page_parse)

        # 详情页
        for dl in dom('.listBox.list-img-style1')('dl').items():
            detail_url = dl('a').attr('href')
            if 'http' not in detail_url:
                detail_url = self.domain_str.format(sub_domain) + detail_url
            if self.db.visited_urls.get(city_code):
                self.db.visited_urls[city_code] = set()
            if detail_url not in self.db.visited_urls[city_code]:
                self.db.visited_urls[city_code].add(detail_url)
                if detail_url not in self.redis_db.load('404'):
                    if '/a1c1/' in response.request.url:
                        yield Request(detail_url, callback=self.transfer_detail_page_parse)
                    if '/a1c2/' in response.request.url:
                        yield Request(detail_url, callback=self.rent_out_detail_page_parse)
                    if '/a1s2/' in response.request.url:
                        yield Request(detail_url, callback=self.rent_in_detail_page_parse)

    def transfer_detail_page_parse(self, response):
        """采集转店详情页"""
        dom = PyQuery(response.body)
        citycode = dom('.fc-city').text()
        create_time = dom('.f10.pr-5').text()
        title = dom('.title-name').text()
        contact = dom('.fc-4b').text()
        tel = dom('.contact-mobile').text()
        url = response.url
        rent = dom('.basic-info-price').text()

        sub_doc = list(dom('.basic-info-ul')('li').items())
        re_compile = re.compile(r'\s.{3}（')
        rent_unit = 'Null' if rent == '面议' else \
            self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
        area = sub_doc[1].text().split(' ')[1]

        shop_state = sub_doc[2].text().split(' ')[1]
        industry_type = sub_doc[3]('a').text()
        shop_name = sub_doc[4].text().split(' ')[1]
        district, _, business_center = sub_doc[5].text().split(' ')[3:6]
        address = sub_doc[6].text().split(' ')[1]

        suit = ','.join([i.text() for i in dom('.ico-equip-items').items() if i('.ico-equip-has')])
        detail = dom('.summary-cont').text()
        img = ','.join([i('img').attr('src') for i in dom('.cont-box.pics')('a').items()])

        item = SpiderPpwItemTransfer(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                     tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                     shop_state=shop_state, industry_type=industry_type, shop_name=shop_name,
                                     address=address, suit=suit, detail=detail, img=img, type=1,
                                     business_center=business_center, district=district)
        self.log('获取详情页： {url}'.format(url=url))
        yield item

    def rent_out_detail_page_parse(self, response):
        """采集出租详情页"""
        dom = PyQuery(response.body)
        citycode = dom('.fc-city').text()
        create_time = dom('.f10.pr-5').text()
        title = dom('.title-name').text()
        contact = dom('.fc-4b').text()
        tel = dom('.contact-mobile').text()
        url = response.url
        rent = dom('.basic-info-price').text()

        sub_doc = list(dom('.basic-info-ul')('li').items())
        re_compile = re.compile(r'\s.{3}（')
        rent_unit = 'Null' if rent == '面议' else \
            self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
        area = sub_doc[1].text().split(' ')[1]
        shop_state = sub_doc[2].text().split(' ')[1]
        industry_type = sub_doc[3]('a').text()
        shop_name = sub_doc[4].text().split(' ')[1]
        district, _, business_center = sub_doc[5].text().split(' ')[3:6]
        address = sub_doc[6].text().split(' ')[1]

        suit = ','.join([i.text() for i in dom('.ico-equip-items').items() if i('.ico-equip-has')])
        detail = dom('.summary-cont').text()
        img = ','.join([i('img').attr('src') for i in dom('.cont-box.pics')('a').items()])

        item = SpiderPpwItemRentOut(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                    tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                    shop_state=shop_state, industry_type=industry_type, shop_name=shop_name,
                                    address=address, suit=suit, detail=detail, img=img, type=2,
                                    business_center=business_center, district=district)

        self.log('获取详情页： {url}'.format(url=url))
        yield item

    def rent_in_detail_page_parse(self, response):
        """采集找店详情页"""
        dom = PyQuery(response.body)
        citycode = dom('.fc-city').text()
        create_time = dom('.f10.pr-5').text()
        title = dom('.title-name').text()
        contact = dom('.fc-4b').text()
        tel = dom('.contact-mobile').text()
        url = response.url
        rent = dom('.basic-info-price').text()

        sub_doc = list(dom('.basic-info-ul')('li').items())
        re_compile = re.compile(r'\s.{3}（')
        rent_unit = 'Null' if rent == '面议' else \
            self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
        area = sub_doc[1].text().split(' ')[1]
        try:
            district = dom('.with-area.clearfix').text().split(' ')[3]
        except Exception:
            district = dom('.with-area.clearfix').text().split(' ')[1]

        address = sub_doc[4].text().split(' ')[1]
        detail = dom('.summary-cont').text()

        item = SpiderPpwItemRentIn(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                   tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                   address=address, detail=detail, type=3, district=district)

        self.log('获取详情页： {url}'.format(url=url))
        yield item
