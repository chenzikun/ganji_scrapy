# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from .constant.db_mysql import MysqlDatabase

from datetime import datetime
from collections import OrderedDict
import logging

# redis
from scrapy_redis.pipelines import RedisPipeline
from twisted.internet.threads import deferToThread


class SpiderPpwPipeline(object):

    logger = logging.getLogger('PipeLine')

    def process_item(self, item, spider):
        pass

    def open_spider(self, spider):
        self.logger.log('spider-{} 开始：{}'.format(spider.__class__.__name__, self.date_time()))
        return self

    def close_spider(self, spider):
        self.logger.log('spider-{} 结束：{}'.format(spider.__class__.__name__, self.date_time()))
        return self

    def date_time(self):
        return datetime.now().strftime('%H:%M:%S')


class CustomRedisPipeline(RedisPipeline):

    logger = logging.getLogger('PipeLine')

    db = MysqlDatabase()
    num = 0

    def process_item(self, item, spider):
        self.distribute_item(item, spider)
        return deferToThread(self._process_item, item, spider)

    def distribute_item(self, item, spider):
        self.num += 1
        _item = self.handle_item(item)
        if _item:
            sql = self.format_spl(_item)
            self.db.insert_mysql(sql)
            print('[INFO]: ')
            if isinstance(item, SpiderPpwItemTransfer):
                self.handle_transfer_item(_item, spider)
            if isinstance(item, SpiderPpwItemRentOut):
                self.handle_rent_out_item(_item, spider)
            if isinstance(item, SpiderPpwItemRentIn):
                self.handle_rent_in_item(_item, spider)

    def handle_item(self, item):
        if any(map(lambda x: x in item['title'], self.db.title_filter)):
            return None
        if item['area'] != '面议':
            item['area'] = item['area'][:-1]
        item['citycode'] = self.db.city_map.get(item['citycode'], 0)
        item['create_time'] = self.format_time(item['create_time'])
        item['tel'] = item['tel'].replace(' ', '')
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
        if item['shop_state']:
            item['shop_state'] = self.db.shop_state_map.get(item['shop_state'], 0)
        return item

    def handle_transfer_item(self, item, spider):
        print('#' * 5, '[转店]', item['citycode'], item['create_time'])
        return item

    def handle_rent_out_item(self, item, spider):
        print('*' * 5, '[出租]', item['citycode'], item['create_time'])
        return item

    def handle_rent_in_item(self, item, spider):
        print('@' * 5, '[找店]', item['citycode'], item['create_time'])
        return item

    def date_time(self):
        return datetime.now().strftime('%H:%M:%S')

    def format_time(self, time_str):
        if ':' in time_str:
            year = datetime.now().year
            day, hour = time_str.split(' ')
            day = str(year) + '-' + day
        else:
            day = time_str
            hour = '00:00'
        _time = "{day} {hour}:00".format(day=day, hour=hour)
        return self.format_str(_time)

    def format_tel(self, tel):
        return str(tel).strip(' ')

    def format_str(self, str_):
        return '\'' + str_ + '\''

    def format_spl(self, item):
        order = OrderedDict()
        for k, v in item._values.items():
            order[k] = str(v)
        order['source'] = '2'
        field = ','.join(list(order.keys()))
        values = ','.join(list(order.values()))
        sql = 'INSERT INTO spiderdb( ' + field + ') VALUES (' + values + ');'.replace('面议', '0')
        return sql
