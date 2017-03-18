from datetime import datetime
import json

import pymysql
import redis

from scrapy.conf import settings
from .utils import Singleton
from .utils import Util
from .cookies import get_cookie


class MysqlDatabase(metaclass=Singleton):

    def __init__(self):

        # 装载城市字典
        self.city_map = {}
        sql = """SELECT code, name FROM district where status=2"""
        districts = self.query(sql)
        for code, name in districts:
            self.city_map[name] = code

        # 装载mobile字典
        # 字典构造 {city:set()}
        self.mobile_map = {}
        sql = """select DISTINCT mobile, city from opportunity"""
        mobiles = self.query(sql)
        for mobile, city in mobiles:
            if not self.mobile_map.get(city):
                self.mobile_map[city] = set()
            self.mobile_map[city].add(mobile)

        # 装载已经存在的urls字典
        self.url_map = {}
        sql = """select url, citycode from spiderdb where source=2"""
        urls = self.query(sql)
        for url, citycode in urls:
            if not self.url_map.get(citycode):
                self.url_map[citycode] = set()
            self.url_map[citycode].add(url)

        self.rent_unit_map = {"元/月": 0, "元/天": 1, "万元/年": 2, "元/平米/月": 3, "元/平米/天": 4}

        self.shop_state_map = {'新铺': 1, '空铺': 2, '营业中': 3}

        self.title_filter = ('Q', 'PW', 'LY', 'YP')

        self.num = 0

        # 建立subdomain --> code，采取城市列表时添加数据
        # 抓取入口页时跟新数据
        self.sub_domain_to_city_code_map = {}

        self.util = Util()
        self.collect_start_urls = []
        self.get_city_list()

    @staticmethod
    def mysql_conn():
        return pymysql.connect(**settings.get('MYSQL_CONFIG'))

    def insert_mysql(self, sql):
        conn = self.mysql_conn()
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()

    def query(self, sql):
        with self.mysql_conn().cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def insert(self, sql):
        self.num += 1
        print('成功写入第{}条记录：{}'.format(self.num, self.date_time()))
        return self.insert_mysql(sql)

    @staticmethod
    def date_time():
        return datetime.now().strftime('%H:%M:%S')

    def get_city_list(self):
        doc = self.util.get_dom('http://www.ganji.com/index.htm')
        for a in doc('.all-city')('a').items():
            link = a.attr('href')
            city = str(a.text())
            city_code = self.city_map.get(city)
            if city_code:
                sub_domain = link.split('//')[1].split('.')[0]
                self.sub_domain_to_city_code_map[sub_domain] = city_code
                url_transfer = 'http://{}.ganji.com/fang6/a1c1/'.format(sub_domain)
                url_rent_out = 'http://{}.ganji.com/fang6/a1c2/'.format(sub_domain)
                url_rent_in = 'http://{}.ganji.com/fang6/a1s2/'.format(sub_domain)
                url_division = [url_transfer, url_rent_out, url_rent_in]
                for url in url_division:
                    self.collect_start_urls.append(url)


class RedisDatabase(metaclass=Singleton):

    def __init__(self):
        self.refresh_cookie()

    @staticmethod
    def redis_conn():
        redis_conn_ = redis.StrictRedis.from_url(settings.get('REDIS_URL'))
        return redis_conn_

    def ip_pond(self):
        result = json.loads(self.redis_conn().get('ip_pond').decode()) if self.redis_conn().get('ip_pond') else []
        return result

    def get_cookie(self):
        result = json.loads(self.redis_conn().get('cookie').decode()) if self.redis_conn().get('cookie') else ''
        return result

    def refresh_cookie(self):
        data = get_cookie()
        self.redis_conn().delete('cookie')
        self.dump('cookie', data)

    def refresh_ip_pond(self, data):
        self.redis_conn().delete('ip_pond')
        self.dump('ip_pond', data)

    def dump(self, key, value):
        s = json.dumps(value)
        self.redis_conn().set(key, s)
