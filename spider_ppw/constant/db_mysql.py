
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

        self.rent_unit_map = {"元/月": 0, "元/天": 1, "万元/年": 2, "元/平米/月": 3, "元/平米/天": 4}

        self.shop_state_map = {'新铺': 1, '空铺': 2, '营业中': 3}

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
