from scrapy.spidermiddlewares.httperror import HttpError
# agent和ip池
from ..common.db import RedisDatabase
from ..common.utils import Util

util = Util()
redis_db = RedisDatabase()


class CustomUrlDropMiddleware(object):
    # 排除掉域名为w的url
    @staticmethod
    def process_spider_input(response, spider):
        url = response.url
        sub_domain = url.split('//')[1].split('.')[0]
        if sub_domain == 'w':
            raise HttpError(response, )


class CustomHttpErrorMiddleware(object):


    def process_spider_input(self, response, spider):
        if response.status == 404:
            urls_404 = redis_db.load('404')
            urls_404.append(response.request._url)
            redis_db.refresh_404_urls(urls_404)
            raise HttpError(response, '404, 加入redis中去')

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            util._404_logger.info(
                "404, url已添加到redis数据库中", response.request._url
            )
            util._404_logger.info(
                response.request._url
            )
