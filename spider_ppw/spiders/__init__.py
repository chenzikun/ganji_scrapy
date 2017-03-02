# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.


import scrapy
import re
from pyquery import PyQuery


from ..items import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from ..constant.db_mysql import MysqlDatabase


class GanJiSpider(scrapy.Spider):

    name = 'ganji'

    db = MysqlDatabase()

    domain = 'http://sz.ganji.com'

    start_urls = ['http://www.ganji.com/index.htm']

    urls = set()

    def parse(self, response):
        if response.status == 200 or 301:
            doc = PyQuery(response.body)
            for a in doc('.all-city')('a').items():
                link = a.attr('href')
                city = str(a.text())
                if self.db.city_map.get(city):
                    sub_domain = link.split('//')[1].split('.')[0]
                    url_transfer = 'http://{}.ganji.com/fang6/a1c1/'.format(sub_domain)
                    url_rent_out = 'http://{}.ganji.com/fang6/a1c2/'.format(sub_domain)
                    url_rent_in = 'http://{}.ganji.com/fang6/a1s2/'.format(sub_domain)
                    url_division = [url_transfer, url_rent_out, url_rent_in]
                    for url in url_division:
                        yield scrapy.Request(url, callback=self.list_page_parse)
        else:
            yield scrapy.Request(response.request._url, callback=self.list_page_parse)

    def list_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.list_page_parse)
        elif response.status == 200 or 301:
            doc = PyQuery(response.body)
            # 翻页
            for li in doc('.pageLink.clearfix')('li').items():
                list_url = li('a').attr('href')
                if list_url not in self.urls and list_url is not None:
                    # 只采集前2个列表页
                    if li('span').text() <= '2':
                        self.urls.add(self.domain + list_url)
                        yield scrapy.Request(self.domain + list_url, callback=self.list_page_parse)

            # 详情页
            for dl in doc('.listBox.list-img-style1')('dl').items():
                detail_url = self.domain + dl('a').attr('href')
                if '/a1c1/' in response._url:
                    yield scrapy.Request(detail_url, callback=self.transfer_detail_page_parse)
                if '/a1c2/' in response._url:
                    yield scrapy.Request(detail_url, callback=self.rent_out_detail_page_parse)
                if '/a1s2/' in response._url:
                    yield scrapy.Request(detail_url, callback=self.rent_in_detail_page_parse)
        else:
            yield scrapy.Request(response.request._url, callback=self.list_page_parse)

    def transfer_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.transfer_detail_page_parse)
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
            rent_unit = 5 if rent == '面议' else \
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
        else:
            yield scrapy.Request(response.request._url, callback=self.transfer_detail_page_parse)

    def rent_out_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.rent_out_detail_page_parse)
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
            rent_unit = 5 if rent == '面议' else \
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
        else:
            yield scrapy.Request(response.request._url, callback=self.rent_out_detail_page_parse)

    def rent_in_detail_page_parse(self, response):
        if 'sorry' in response._url:
            yield scrapy.Request(response.request._url, callback=self.rent_in_detail_page_parse)
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
            rent_unit = 5 if rent == '面议' else \
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
        else:
            yield scrapy.Request(response.request._url, callback=self.rent_in_detail_page_parse)
