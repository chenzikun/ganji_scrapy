
import scrapy
import re
from pyquery import PyQuery


from ..items import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from ..constant.db import MysqlDatabase


class GanJiSpider(scrapy.Spider):
    """
    采集数据subdomain, name, code 的解决方式
    赶集 name --> sub_domain
    公司 name --> code (table district)
    为了去重的提高检索效率，构建 code --> urls (table spiderdb)
    """

    name = 'ganji'

    db = MysqlDatabase()

    domain = "http://ganji.com"

    domain_str = 'http://{}.ganji.com'

    start_urls = ['http://www.ganji.com/index.htm']

    urls = set()

    # 建立subdomain --> code，采取城市列表时添加数据
    sub_domain_to_city_code_map = {}

    # 采集列表页准备
    def parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.parse)
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            for a in doc('.all-city')('a').items():
                link = a.attr('href')
                city = str(a.text())
                city_code = self.db.city_map.get(city)
                if city_code:
                    sub_domain = link.split('//')[1].split('.')[0]
                    self.sub_domain_to_city_code_map[sub_domain] = city_code
                    url_transfer = 'http://{}.ganji.com/fang6/a1c1/'.format(sub_domain)
                    url_rent_out = 'http://{}.ganji.com/fang6/a1c2/'.format(sub_domain)
                    url_rent_in = 'http://{}.ganji.com/fang6/a1s2/'.format(sub_domain)
                    url_division = [url_transfer, url_rent_out, url_rent_in]
                    for url in url_division:
                        yield scrapy.Request(url, callback=self.list_page_parse)
        elif response.status == 404:
            return
        else:
            yield scrapy.Request(response.request._url, callback=self.parse)

    # 采集列表页
    def list_page_parse(self, response):
        sub_domain = response.request._url.split('.')[0].strip('http://')
        city_code = self.sub_domain_to_city_code_map.get(sub_domain)
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.list_page_parse)
        elif response.status == 404:
            return
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            # 翻页
            for li in doc('.pageLink.clearfix')('li').items():
                list_url = li('a').attr('href')
                if list_url not in self.urls and list_url is not None:
                    # 只采集前2个列表页
                    if li('span').text() <= '2':
                        target_url = self.domain_str.format(sub_domain) + list_url
                        self.urls.add(target_url)
                        yield scrapy.Request(target_url, callback=self.list_page_parse)

            # 详情页
            for dl in doc('.listBox.list-img-style1')('dl').items():
                detail_url = self.domain_str.format(sub_domain) + dl('a').attr('href')
                city_urls_set = self.db.url_map.get(city_code, set())
                if detail_url not in city_urls_set:
                    if '/a1c1/' in response.request._url:
                        yield scrapy.Request(detail_url, callback=self.transfer_detail_page_parse)
                    if '/a1c2/' in response.request._url:
                        yield scrapy.Request(detail_url, callback=self.rent_out_detail_page_parse)
                    if '/a1s2/' in response.request._url:
                        yield scrapy.Request(detail_url, callback=self.rent_in_detail_page_parse)

    # 采集转店详情页
    def transfer_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.transfer_detail_page_parse)
        elif response.status == 404:
            return
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            citycode = doc('.fc-city').text()
            create_time = doc('.f10.pr-5').text()
            title = doc('.title-name').text()
            contact = doc('.fc-4b').text()
            tel = doc('.contact-mobile').text()
            url = response._url
            rent = doc('.basic-info-price').text()

            sub_doc = list(doc('.basic-info-ul')('li').items())
            re_compile = re.compile(r'\s.{3}（')
            rent_unit = 'Null' if rent == '面议' else \
                self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
            area = sub_doc[1].text().split(' ')[1]

            shop_state = sub_doc[2].text().split(' ')[1]
            industry_type = sub_doc[3]('a').text()
            shop_name = sub_doc[4].text().split(' ')[1]
            district, _, business_center = sub_doc[5].text().split(' ')[3:6]
            address = sub_doc[6].text().split(' ')[1]

            suit = ','.join([i.text() for i in doc('.ico-equip-items').items() if i('.ico-equip-has')])
            detail = doc('.summary-cont').text()
            img = ','.join([i('img').attr('src') for i in doc('.cont-box.pics')('a').items()])

            item = SpiderPpwItemTransfer(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                         tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                         shop_state=shop_state, industry_type=industry_type, shop_name=shop_name,
                                         address=address, suit=suit, detail=detail, img=img, type=1,
                                         business_center=business_center)

            self.log('获取详情页： {url}'.format(url=url))
            yield item

    # 采集出租详情页
    def rent_out_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.rent_out_detail_page_parse)
        elif response.status == 404:
            return
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            citycode = doc('.fc-city').text()
            create_time = doc('.f10.pr-5').text()
            title = doc('.title-name').text()
            contact = doc('.fc-4b').text()
            tel = doc('.contact-mobile').text()
            url = response._url
            rent = doc('.basic-info-price').text()

            sub_doc = list(doc('.basic-info-ul')('li').items())
            re_compile = re.compile(r'\s.{3}（')
            rent_unit = 'Null' if rent == '面议' else \
                self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
            area = sub_doc[1].text().split(' ')[1]
            shop_state = sub_doc[2].text().split(' ')[1]
            industry_type = sub_doc[3]('a').text()
            shop_name = sub_doc[4].text().split(' ')[1]
            district, _, business_center = sub_doc[5].text().split(' ')[3:6]
            address = sub_doc[6].text().split(' ')[1]

            suit = ','.join([i.text() for i in doc('.ico-equip-items').items() if i('.ico-equip-has')])
            detail = doc('.summary-cont').text()
            img = ','.join([i('img').attr('src') for i in doc('.cont-box.pics')('a').items()])

            item = SpiderPpwItemRentOut(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                        tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                        shop_state=shop_state, industry_type=industry_type, shop_name=shop_name,
                                        address=address, suit=suit, detail=detail, img=img, type=2,
                                        business_center=business_center)

            self.log('获取详情页： {url}'.format(url=url))
            yield item

    # 采集找店详情页
    def rent_in_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.rent_in_detail_page_parse)
        elif response.status == 404:
            return
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            citycode = doc('.fc-city').text()
            create_time = doc('.f10.pr-5').text()
            title = doc('.title-name').text()
            contact = doc('.fc-4b').text()
            tel = doc('.contact-mobile').text()
            url = response._url
            rent = doc('.basic-info-price').text()

            sub_doc = list(doc('.basic-info-ul')('li').items())
            re_compile = re.compile(r'\s.{3}（')
            rent_unit = 'Null' if rent == '面议' else \
                self.db.rent_unit_map.get(re_compile.findall(sub_doc[0].text())[0].strip('（').strip(' '))
            area = sub_doc[1].text().split(' ')[1]
            try:
                try:
                    district, _, business_center = doc('.with-area.clearfix').text().split(' ')[3:6]
                except:
                    district = doc('.with-area.clearfix').text().split(' ')[1]
                    business_center = ' '
            except:
                district, business_center = ' ', ' '

            address = sub_doc[4].text().split(' ')[1]
            detail = doc('.summary-cont').text()

            item = SpiderPpwItemRentIn(citycode=citycode, create_time=create_time, title=title, contact=contact,
                                       tel=tel, url=url, rent=rent, rent_unit=rent_unit, area=area,
                                       address=address, detail=detail, type=3)

            self.log('获取详情页： {url}'.format(url=url))
            yield item
