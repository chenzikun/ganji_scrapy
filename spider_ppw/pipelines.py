# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from collections import OrderedDict
import logging

# redis
from scrapy_redis.pipelines import RedisPipeline
from twisted.internet.threads import deferToThread
from scrapy.exceptions import DropItem


from .items import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from .constant.db import MysqlDatabase


class DropRedirectUrlPipeline(object):
    db = MysqlDatabase()

    logger = logging.getLogger('PipeLine')

    def process_item(self, item, spider):
        city_code = item['city_code']
        if self.db.url_map.get(city_code, 0):
            if item['url'] in self.db.url_map[city_code]:
                self.db.redirect_urls.add(item['url'])
                raise DropItem
        return item


class CustomRedisPipeline(RedisPipeline):
    logger = logging.getLogger('PipeLine')

    db = MysqlDatabase()
    num = 0

    def process_item(self, item, spider):
        print(format('    {}    '.format(self.num), '!^30s'))
        self.distribute_item(item)
        return deferToThread(self._process_item, item, spider)

    def distribute_item(self, item):
        self.num += 1
        _item = self.handle_item(item)
        if _item:
            sql = self.format_spl(_item)
            try:
                self.db.insert_mysql(sql)
                print('[INFO]: ')
                if isinstance(item, SpiderPpwItemTransfer):
                    self.handle_transfer_item(_item)
                if isinstance(item, SpiderPpwItemRentOut):
                    self.handle_rent_out_item(_item)
                if isinstance(item, SpiderPpwItemRentIn):
                    self.handle_rent_in_item(_item)
            except Exception as e:
                if isinstance(e, tuple):
                    if 'Duplicate entry' in e[1]:
                        self.db.redirect_urls.add(item['url'].strip('\''))

    def handle_item(self, item):
        if any(map(lambda x: x in item['title'], self.db.title_filter)):
            return None
        if item['area'] != '面议':
            item['area'] = item['area'][:-1]
        item['create_time'] = self.format_time(item['create_time'])
        item['tel'] = item['tel'].replace(' ', '')
        item['citycode'] = self.db.city_map.get(item['citycode'], 0)
        if item['citycode']:
            if item['tel'] in self.db.mobile_map.get(item['citycode']):
                return None
        item['detail'] = self.format_str(item['detail'])
        item['title'] = self.format_str(item['title'])
        item['url'] = self.format_str(item['url'])
        item['contact'] = self.format_str(item['contact'])
        if item['suit'] is not None:
            if item['suit'] == '':
                item['suit'] = 'NULL'
            else:
                item['suit'] = self.format_str(item['suit'])
        if item['rent'] == '面议':
            item['rent'] = 0
        # if item['rent_unit']:
        #     item['rent_unit'] = self.format_str(item['rent_unit'])
        if item['shop_name']:
            item['shop_name'] = self.format_str(item['shop_name'])
        if item['address']:
            item['address'] = self.format_str(item['address'])
        if item['business_center']:
            item['business_center'] = self.format_str(item['business_center'])
        if item['img'] is not None:
            if item['img'] == '':
                item['img'] = 'NULL'
            else:
                item['img'] = self.format_str(item['img'])
        if item['industry_type']:
            item['industry_type'] = self.format_str(item['industry_type'])
        if item['district']:
            item['district'] = self.format_str(item['district'])
        if item['shop_state']:
            item['shop_state'] = self.db.shop_state_map.get(item['shop_state'], 0)
        return item

    @staticmethod
    def handle_transfer_item(item):
        print('#' * 5, '[转店]', item['citycode'], item['create_time'], item['url'])
        return item

    @staticmethod
    def handle_rent_out_item(item):
        print('*' * 5, '[出租]', item['citycode'], item['create_time'], item['url'])
        return item

    @staticmethod
    def handle_rent_in_item(item):
        print('@' * 5, '[找店]', item['citycode'], item['create_time'], item['url'])
        return item

    @staticmethod
    def date_time():
        return datetime.now().strftime('%H:%M:%S')

    def format_time(self, time_str):
        if ':' in time_str:
            year = datetime.now().year
            day, hour = time_str.split(' ')
            if day > datetime.now().strftime('%m-%d'):
                year = year - 1
            day = str(year) + '-' + day
        else:
            day = time_str
            hour = '00:00'
        _time = "{day} {hour}:00".format(day=day, hour=hour)
        return self.format_str(_time)

    @staticmethod
    def format_tel(tel):
        return str(tel).strip(' ')

    @staticmethod
    def format_str(str_):
        return '\'' + str_ + '\''

    @staticmethod
    def format_spl(item):
        order = OrderedDict()
        for k, v in item._values.items():
            order[k] = str(v)
        order['source'] = '2'
        field = ','.join(list(order.keys()))
        values = ','.join(list(order.values()))
        sql = 'INSERT INTO spiderdb( ' + field + ') VALUES (' + values + ');'.replace('面议', 'NULL')
        return sql


