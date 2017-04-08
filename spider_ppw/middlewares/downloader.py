import random
import base64
import logging

# agent和ip池中间件
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.conf import settings
from scrapy.exceptions import IgnoreRequest

# agent和ip池
from ..common.useragent import AGENTS
from ..common.db import RedisDatabase
from ..common.db import MysqlDatabase


redis_db = RedisDatabase()

db = MysqlDatabase()


# download middleware
class CustomUserAgentMiddleware(UserAgentMiddleware):
    """随机更改Usera"""

    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers.setdefault(b'User-Agent', agent)


class CustomHttpProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('PROXY')
        proxy_user_pass = settings.get('PROXY_USER_PASSWORD')
        encode_user_pass = base64.b64encode(proxy_user_pass.encode()).decode()
        request.headers['Proxy-Authorization'] = 'Basic ' + encode_user_pass


class CustomUrlFilterMiddleware(object):
    def process_request(self, request, spider):
        url = request._url
        sub_domain = url.split('//')[1].split('.')[0]
        # 过滤子域名为'w'的url
        if sub_domain == 'w':
            raise IgnoreRequest

        # 过滤跳转url, 避免重复请求
        if url in db.redirect_urls:
            raise IgnoreRequest


class CustomCookieMiddleware(RetryMiddleware):
    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        cookie = redis_db.get_cookie()
        if cookie:
            request.cookies = cookie
            request.meta['accountText'] = cookie

    def process_response(self, request, response, spider):
        if response.status != 200 or 301:
            redis_db.refresh_cookie()
