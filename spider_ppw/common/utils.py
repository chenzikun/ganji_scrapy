import requests
import logging
from logging.handlers import RotatingFileHandler
import os

import pyquery
from scrapy.conf import settings
from datetime import datetime


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Util(metaclass=Singleton):
    def __init__(self):
        self._404_logger = self.create_logger('404')

    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1)AppleWebKit/537.36 ("
                             "KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
               'Accept': 'text / html, application / xhtml + xml'
               }

    def get_dom(self, url):
        rep = requests.get(url=url, headers=self.headers, timeout=10).content
        dom = pyquery.PyQuery(rep)
        return dom

    def create_logger(self, name):
        logger = logging.getLogger(name)
        base_dir = os.path.join(os.path.dirname(__file__), 'data--{}/'.format(self.date_time()))
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        file = os.path.join(base_dir, name)
        handler = RotatingFileHandler(filename=file, encoding="utf8")
        logger.addHandler(handler)
        logger.setLevel(level=settings.get('LOG_LEVEL', 'INFO'))

        return logger

    @staticmethod
    def date_time():
        return datetime.now().strftime('%Y:%m:%d')
