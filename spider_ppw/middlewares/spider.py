import logging

# agent和ip池
from ..constant.db import RedisDatabase

logger = logging.getLogger(__name__)

redis_db = RedisDatabase()


class CustomUrlDropMiddleware(object):
    # 排除掉域名为w的url
    @staticmethod
    def process_spider_input(response, spider):
        url = response.url
        sub_domain = url.split('//')[1].split('.')[0]
        if sub_domain == 'w':
            raise Exception


class CustomHttpErrorMiddleware(object):

    @staticmethod
    def process_spider_input(response, spider):
        if response.status == 404:
            urls_404 = redis_db.load('404')
            urls_404.append(response.request._url)
            redis_db.refresh_404_urls(urls_404)
            raise Exception



