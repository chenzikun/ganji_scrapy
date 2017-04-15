import re

from pyquery import PyQuery
from scrapy import Spider, Request

from ..common.db import MysqlDatabase, RedisDatabase
from ..items._58 import RentItem, TransferItem, LeaseItem


class _58_Spider(Spider):
    name = '58'

    start_urls = ['http://www.58.com/changecity.aspx']

    db = MysqlDatabase()
    redis_db = RedisDatabase()

    domain_str = 'http://{}.58.com'

    # list url
    list_page_urls = set()

    def parse(self, response):
        dom = PyQuery(response.body)
        dds = dom('dl#clist')('dd')

        # 采集子域名
        for dd in dds.items():
            for a in dd('a').items():
                city_name = a.text()
                city_code = self.db.city_map.get(city_name)
                if city_code:
                    city_py = a.attr('href').split('//')[1].split('.')[0]
                    if city_py:
                        self.db.sub_domain_to_city_code_map_58[city_py] = city_code
                        url_transfer = 'http://{}.58.com/shengyizr/0/'.format(city_py)
                        url_rent_out = 'http://{}.58.com/shangpucz/0/'.format(city_py)
                        url_rent_in = 'http://{}.58.com/shangpuqz/0/'.format(city_py)
                        url_division = [url_transfer, url_rent_out, url_rent_in]
                        for url in url_division:
                            yield Request(url, callback=self.list_page_parse)

    def list_page_parse(self, response):
        # 获取子域名
        city_py = response.request.url.split('//')[1].split('.')[0]
        city_code = self.db.sub_domain_to_city_code_map_58.get(city_py)

        dom = PyQuery(response.body)
        # 翻页
        for a in dom('.pager')('a').items():
            if a('span').text() <= '2':
                list_page = a('span').text()
                target_url = self.domain_str.format(city_py) + list_page
                yield Request(target_url, callback=self.list_page_parse)

        # 详情页url
        for tr in dom('table.tbimg')('tr').items():
            detail_url = tr('.t')('a').attr('href')
            if not self.db.visited_urls.get(city_code):
                self.db.visited_urls[city_code] = set()
            if detail_url not in self.db.visited_urls[city_code]:
                self.db.visited_urls[city_code].add(detail_url)
                if 'shengyizr' in response.request.url:
                    yield Request(detail_url, callback=self.transfer_detail_page_parse)
                if 'shangpucz' in response.request.url:
                    yield Request(detail_url, callback=self.rent_out_detail_page_parse)
                if 'shangpuqz' in response.request.url:
                    yield Request(detail_url, callback=self.rent_in_detail_page_parse)

    def transfer_detail_page_parse(self, response):
        """采集转店详情页"""
        item = TransferItem()
        item['source'] = 1
        item['type'] = 1
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="w headline"]/h1/text()').extract()
        item['district'] = response.xpath('//ul[@class="info"]/li[1]/a[1]/text()').extract() or ''
        item['business_center'] = response.xpath('//ul[@class="info"]/li[1]/a[2]/text()').extract() or ''
        info1 = response.xpath('//ul[@class="info"]/li[1]/text()').extract() or ''
        info2 = response.xpath('//ul[@class="info"]/li[2]/text()').extract() or ''
        info3 = response.xpath('//ul[@class="info"]/li[3]/text()').extract() or ''
        info4 = response.xpath('//ul[@class="info"]/li[4]/text()').extract() or ''
        info5 = response.xpath('//ul[@class="info"]/li[5]/text()').extract() or ''
        info6 = response.xpath('//ul[@class="info"]/li[6]/text()').extract() or ''
        info7 = response.xpath('//ul[@class="info"]/li[last()-1]').extract() or ''
        info8 = response.xpath('//ul[@class="info"]/li[last()]').extract() or ''
        item['industry_type'] = ''
        item['area'] = None
        item['address'] = ''
        item['neighborhood'] = ''
        item['industry'] = ''
        item['cost'] = None
        item['cost_unit'] = None

        data_extraction = DataExtraction()
        for i in [info1, info2, info3, info4, info5, info6, info7, info8]:
            if i:
                i = i[0]
                if i.startswith("类型："):
                    item['industry_type'] = i.replace("类型：", "").strip()
                if i.startswith("面积："):
                    item['sub_area'], item['area'] = data_extraction.decorate_area(i)
                if i.startswith("地址："):
                    item['address'] = i.replace("地址：", "").strip()
                if i.startswith("临近："):
                    item['neighborhood'] = i.replace("临近：", "").strip()
                if i.startswith("行业："):
                    item['industry'] = i.replace("行业：", "").strip()
                if "转让费" in i:
                    item['cost'], item['cost_unit'] = data_extraction.decorate_cost(i)
                if "租金" in i:
                    result = re.compile(r'\<em class=\"redfont\"\>(.*)\<\/em\>(.*)').search(i)
                    if result:
                        item['rent'] = result.group(1)
                        item['rent_unit'] = result.group(2)
                        if "面议" in item['rent']:
                            item['rent'] = 0
                            item['rent_unit'] = None
                        elif item['rent']:
                            try:
                                item['rent'] = int(float(item['rent']))
                            except ValueError:  # 解析出错
                                item['rent'] = None
                            if "元/月" in item['rent_unit']:
                                item['rent_unit'] = 1
                            elif "元/㎡/天" in item['rent_unit']:
                                item['rent_unit'] = 5
                            else:
                                item['rent_unit'] = None
                        else:
                            item['rent'] = None
                            item['rent_unit'] = None

        item['create_time'] = data_extraction.decorate_time(response)
        item['contact'] = data_extraction.decorate_contact(response)
        item['tel'] = data_extraction.decorate_tel(response)
        item['detail'] = data_extraction.decorate_detail(response)
        item['img'] = data_extraction.decorate_img(response)

        for i in ['title', 'district', 'business_center']:
            if item[i]:
                item[i] = item[i][0].strip()
            else:
                item[i] = ''

        # 为空
        item['sub_area'] = None
        item['minus_rent'] = None
        item['engaged'] = ''
        py = response.url.split('://')[1].split('.')[0]

        if self.db.sub_domain_to_city_code_map_58.get(py):
            item['citycode'] = self.db.sub_domain_to_city_code_map_58.get(py)
            yield item

    def rent_out_detail_page_parse(self, response):
        """采集出租详情页"""
        item = LeaseItem()
        item['source'] = 1
        item['type'] = 2
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="w headline"]/h1/text()').extract()
        item['district'] = response.xpath('//ul[@class="info"]/li[1]/a[1]/text()').extract() or ''
        item['business_center'] = response.xpath('//ul[@class="info"]/li[1]/a[2]/text()').extract() or ''
        item['rent'] = response.xpath('//ul[@class="info"]/li[last()]/em/text()').extract() or ''
        item['rent_unit'] = response.xpath('//ul[@class="info"]/li[last()]/text()').extract() or ''
        info1 = response.xpath('//ul[@class="info"]/li[1]/text()').extract() or ''
        info2 = response.xpath('//ul[@class="info"]/li[2]/text()').extract() or ''
        info3 = response.xpath('//ul[@class="info"]/li[3]/text()').extract() or ''
        info4 = response.xpath('//ul[@class="info"]/li[4]/text()').extract() or ''
        info5 = response.xpath('//ul[@class="info"]/li[5]/text()').extract() or ''
        info6 = response.xpath('//ul[@class="info"]/li[6]/text()').extract() or ''
        item['industry_type'] = ''
        item['area'] = None
        item['address'] = ''
        item['engaged'] = ''
        item['neighborhood'] = ''
        item['sub_area'] = None

        data_extraction = DataExtraction()
        for i in [info1, info2, info3, info4, info5, info6]:
            if i:
                i = i[0]
                if i.startswith("类型："):
                    item['industry_type'] = i.replace("类型：", "").strip()
                if i.startswith("面积："):
                    item['sub_area'], item['area'] = data_extraction.decorate_area(i)
                if i.startswith("地址："):
                    item['address'] = i.replace("地址：", "").strip()
                if i.startswith("历史经营:"):
                    item['engaged'] = i.replace("历史经营:", "").strip()
                if i.startswith("临近："):
                    item['neighborhood'] = i.replace("临近：", "").replace(' ', '')

        item['create_time'] = data_extraction.decorate_time(response)
        item['contact'] = data_extraction.decorate_contact(response)
        item['tel'] = data_extraction.decorate_tel(response)
        item['detail'] = data_extraction.decorate_detail(response)
        item['img'] = data_extraction.decorate_img(response)

        for i in ['title', 'district', 'business_center', 'rent']:
            if item[i]:
                item[i] = item[i][0].strip()
            else:
                item[i] = ''
        # rent
        if item['rent_unit']:
            item['rent_unit'] = item['rent_unit'][1].strip()
        else:
            item['rent_unit'] = None
        if "面议" in item['rent']:
            item['rent'] = 0
            item['rent_unit'] = None
        elif item['rent']:
            try:
                item['rent'] = int(float(item['rent']))
            except ValueError:
                item['rent'] = None
            if "元/月" in item['rent_unit']:
                item['rent_unit'] = 1
            elif "元/㎡/天" in item['rent_unit']:
                item['rent_unit'] = 5
            else:
                item['rent_unit'] = None
        else:
            item['rent'] = None
            item['rent_unit'] = None

        # 为空
        item['cost'] = None
        item['cost_unit'] = None
        item['minus_rent'] = None
        item['industry'] = None

        py = response.url.split('://')[1].split('.')[0]

        if self.db.sub_domain_to_city_code_map_58.get(py):
            item['citycode'] = self.db.sub_domain_to_city_code_map_58.get(py)
            yield item

    def rent_in_detail_page_parse(self, response):
        """采集找店详情页"""
        item = RentItem()
        item['source'] = 1
        item['type'] = 3
        item['url'] = response.url
        item['title'] = response.xpath('//div[@class="w headline"]/h1/text()').extract()
        item['district'] = response.xpath('//ul[@class="info"]/li[1]/a[1]/text()').extract() or ''
        item['business_center'] = response.xpath('//ul[@class="info"]/li[1]/a[2]/text()').extract() or ''
        item['rent'] = response.xpath('//ul[@class="info"]/li[last()]/em/text()').extract() or ''
        item['rent_unit'] = response.xpath('//ul[@class="info"]/li[last()]/text()').extract() or ''
        info1 = response.xpath('//ul[@class="info"]/li[1]/text()').extract() or ''
        info2 = response.xpath('//ul[@class="info"]/li[2]/text()').extract() or ''
        info3 = response.xpath('//ul[@class="info"]/li[3]/text()').extract() or ''
        info4 = response.xpath('//ul[@class="info"]/li[4]/text()').extract() or ''
        info5 = response.xpath('//ul[@class="info"]/li[5]/text()').extract() or ''
        info6 = response.xpath('//ul[@class="info"]/li[6]/text()').extract() or ''
        item['industry_type'] = ''
        item['area'] = None
        item['neighborhood'] = ''
        item['sub_area'] = None

        data_extraction = DataExtraction()
        for i in [info1, info2, info3, info4, info5, info6]:
            if i:
                i = i[0]
                if i.startswith("类型："):
                    item['industry_type'] = i.replace("类型：", "").strip()
                if i.startswith("面积："):
                    item['sub_area'], item['area'] = data_extraction.decorate_area(i)
                if i.startswith("临近："):
                    item['neighborhood'] = i.replace("临近：", "").strip().replace(' ', '')

        item['create_time'] = data_extraction.decorate_time(response)
        item['contact'] = data_extraction.decorate_contact(response)
        item['tel'] = data_extraction.decorate_tel(response)
        item['detail'] = data_extraction.decorate_detail(response)

        # rent
        item['minus_rent'] = None
        if item['rent_unit']:
            item['rent_unit'] = item['rent_unit'][1].strip()
        else:
            item['rent_unit'] = None
        if "面议" in item['rent']:
            item['rent'] = 0
            item['rent_unit'] = None
        elif item['rent']:
            if "-" in item['rent']:
                minus_rent, rent = item['rent'].split('-')
                try:
                    item['rent'] = int(float(rent))
                    item['minus_rent'] = int(float(minus_rent))
                except ValueError:
                    item['rent'] = None
                    item['minus_rent'] = None
            if "元/月" in item['rent_unit']:
                item['rent_unit'] = 1
            elif "元/㎡/天" in item['rent_unit']:
                item['rent_unit'] = 5
            else:
                item['rent_unit'] = None
        else:
            item['rent'] = None
            item['rent_unit'] = None

        # 为空
        item['engaged'] = ''
        item['img'] = ''
        item['address'] = ''
        item['cost'] = None
        item['cost_unit'] = None
        item['industry'] = None

        py = response.url.split('://')[1].split('.')[0]

        if self.db.sub_domain_to_city_code_map_58.get(py):
            item['citycode'] = self.db.sub_domain_to_city_code_map_58.get(py)
            yield item


class DataExtraction:
    """进行处理数据"""

    def decorate_cost(self, i):
        result = re.compile(r'\<em class=\"redfont\"\>(.*)\<\/em\>(.*)').search(i)
        if result:
            cost = result.group(1)
            cost_unit = result.group(2)  # 读到的都是万元
            if "面议" in cost:
                cost_ = 0
                cost_unit_ = None
            else:
                try:
                    if int(float(cost)) > 10000:
                        cost_ = int(float(cost))
                        cost_unit_ = 2  # 万元
                    else:
                        cost_ = int(float(cost) * 10000)
                        cost_unit_ = 1  # 元
                except ValueError:  # 解析出错，
                    cost_ = None
                    cost_unit_ = None
        else:
            cost_ = None
            cost_unit_ = None
        return cost_, cost_unit_

    def decorate_area(self, i):
        area = i.replace("面积：", "").strip().replace("㎡", "")
        if "-" in area:
            sub_area, area = area.split('-')
            sub_area_ = int(sub_area)
            area_ = int(area)
        elif " " in area:
            sub_area, area = area.split()
            sub_area_ = int(sub_area)
            area_ = int(area)
        else:
            sub_area_ = None
            area_ = int(area)
        return sub_area_, area_

    def decorate_time(self, response):
        """获取时间"""
        create_time = response.xpath('//div[@class="other"]/text()').extract()
        if create_time:
            if "发布时间：" in create_time[0]:
                time = create_time[0].replace("发布时间：", "")
            else:
                time = create_time[0]
        else:
            time = None
        return time

    def decorate_contact(self, response):
        """获取联系人"""
        contact = response.xpath('//div[@class="user"]/script/text()').extract()
        if contact:
            contact = contact[0]
            contact = re.match(r'([\S|\s]+)username:\'([\S|\s]+)\',', contact)
            if contact:
                contact_ = contact.group(2)
            else:
                contact_ = ''
        else:
            contact_ = ''
        return contact_

    def decorate_tel(self, response):
        """获取电话"""
        tel = response.xpath('//span[@id="t_phone"]/script/text()').extract()
        if tel:
            tel = tel[0]
            p = re.compile(r'\<img src=\'(.*)\' \/\>')
            tel_ = p.search(tel).group(1)
        elif response.xpath('//*[@id="t_phone"]/text()').extract():
            tel_ = response.xpath('//*[@id="t_phone"]/text()').extract()[0].strip()
        else:
            tel_ = ''
        return tel_

    def decorate_detail(self, response):
        """获取详情"""
        data1 = response.xpath('//div[@class="maincon"]')
        detail = ''
        if data1:
            for i in data1:
                detail = detail + i.xpath('string(.)').extract()[0]
        if detail:
            detail_ = detail.strip().replace(' ', '').replace(u'\u200b', '')
            detail_ = self.remove_non_charac(detail_)
        else:
            detail_ = ''
        return detail_

    def remove_non_charac(self, detail):
        """去掉非正常的字"""
        detail_ = detail.encode(encoding='utf-8')
        i = 0
        detail_ = bytearray(detail_)
        while i < len(detail_):
            if ((detail_[i] & 0xF8) == 0xF0):
                for j in range(4):
                    detail_[i + j] = 0x30
                i = i + 3
            i = i + 1
        detail_ = detail_.decode('utf-8')
        return detail_

    def decorate_img(self, response):
        """获取图片"""
        photos = response.xpath('//*[@class="conleft"]/script[3]/text()').extract() or ''
        img = ''
        if photos:
            for i in photos:
                p = re.compile(r'img_list.push\(\"(http://pic.*)\"\)\;')
                img = ','.join(p.findall(i))
        return img
