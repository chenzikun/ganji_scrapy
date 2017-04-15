from datetime import datetime
from datetime import timedelta
from collections import OrderedDict
import logging

# redis
from scrapy_redis.pipelines import RedisPipeline
from twisted.internet.threads import deferToThread
from scrapy.exceptions import DropItem

from .items.ganji import SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn
from .items._58 import RentItem, TransferItem, LeaseItem
from .common.db import MysqlDatabase


class DropRedirectUrlPipeline(object):
    db = MysqlDatabase()

    def process_item(self, item, spider):
        city_code = item['city_code']
        if self.db.visited_urls.get(city_code, 0):
            if item['url'] in self.db.visited_urls[city_code]:
                self.db.redirect_urls.add(item['url'])
                raise DropItem
        return item


class CustomRedisPipeline(RedisPipeline):
    db = MysqlDatabase()
    num = 0

    def process_item(self, item, spider):
        item = self.before_handled(item)
        if item:
            self.distribute_item(item)
            self.num += 1
            print('[INFO]: {}'.format(self.num))
            self.after_handled(item)
        return deferToThread(self._process_item, item, spider)

    def distribute_item(self, item):
        if isinstance(item, (TransferItem, RentItem, LeaseItem)):
            self.handle_58_item(item)
            if isinstance(item, TransferItem):
                self._print(item, '58', '转店')
            if isinstance(item, LeaseItem):
                self._print(item, '58', '出租')
            if isinstance(item, RentItem):
                self._print(item, '58', '找店')
        if isinstance(item, (SpiderPpwItemTransfer, SpiderPpwItemRentOut, SpiderPpwItemRentIn)):
            self.handle_ganji_item(item)
            if isinstance(item, SpiderPpwItemTransfer):
                self._print(item, '赶集', '转店')
            if isinstance(item, SpiderPpwItemRentOut):
                self._print(item, '赶集', '出租')
            if isinstance(item, SpiderPpwItemRentIn):
                self._print(item, '赶集', '找店')

    def before_handled(self, item):
        if any(map(lambda x: x in item['title'], self.db.title_filter)):
            return None
        else:
            return item

    def after_handled(self, item):
        sql, value = self.format_spl(item)
        try:
            self.db.insert(sql, value)
        except Exception as e:
            if isinstance(e, tuple):
                if 'Duplicate entry' in e[1]:
                    self.db.redirect_urls.add(item['url'].strip('\''))

    def handle_ganji_item(self, item):
        item['source'] = '2'
        if item['area'] != '面议':
            item['area'] = item['area'][:-1]
        item['create_time'] = self.format_time(item['create_time'])
        item['tel'] = item['tel'].replace(' ', '')
        item['citycode'] = self.db.city_map.get(item['citycode'], 0)
        if item['citycode']:
            if item['tel'] in self.db.mobile_map.get(item['citycode']):
                return None
        if item['suit'] is not None:
            if item['suit'] == '':
                item['suit'] = 'NULL'
        if item['rent'] == '面议':
            item['rent'] = 0
        if item['img'] is not None:
            if item['img'] == '':
                item['img'] = 'NULL'
        if item['shop_state']:
            item['shop_state'] = self.db.shop_state_map.get(item['shop_state'], 0)
        item['collect_time'] = self.collect_time()
        return item

    def handle_58_item(self, item):
        item['collect_time'] = self.collect_time()
        return item

    @staticmethod
    def collect_time():
        time = datetime.now() + timedelta(hours=8)
        return time.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _print(item, source, type_):
        print(format(source, "^5"), '-->[{}]'.format(type_), item['citycode'], item['create_time'], item['url'])
        return item

    @staticmethod
    def now():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def format_time(time_str):
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
        return _time

    @staticmethod
    def format_tel(tel):
        return str(tel).strip(' ')

    @staticmethod
    def format_str(str_):
        return '\'' + str_ + '\''

    @staticmethod
    def format_spl(item):
        order = OrderedDict()
        item_fields = len(item)
        for k, v in item._values.items():
            order[k] = str(v)
        field = ','.join(list(order.keys()))
        values = ','.join(list(order.values()))
        sql = 'INSERT INTO spiderdb ( ' + field + ') VALUES (' + ','.join('%s' * item_fields) + ');'
        return sql, values.replace('面议', 'NULL')
