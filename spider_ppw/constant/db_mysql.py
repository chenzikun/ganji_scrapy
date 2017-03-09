
from scrapy.conf import settings
from datetime import datetime
import pymysql


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


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
        sql = """select url, citycode from spiderdb"""
        urls = self.query(sql)
        for url, citycode in urls:
            if not self.url_map.get(citycode):
                self.url_map[citycode] = set()
            self.url_map[citycode].add(url)

        self.rent_unit_map = {"元/月": 0, "元/天": 1, "万元/年": 2, "元/平米/月": 3, "元/平米/天": 4}

        self.shop_state_map = {'新铺': 1, '空铺': 2, '营业中': 3}

        self.title_filter = ('Q','PW','LY','YP')

        self.num = 0

    def mysql_conn(self):
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

    def date_time(self):
        return datetime.now().strftime('%H:%M:%S')
