# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import redis
import json
import random
import base64

# agent和ip池中间件
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
# 重试中间件
from scrapy.downloadermiddlewares.retry import RetryMiddleware


# agent和ip池
from .constant.useragent import AGENTS
from .constant.db import RedisDatabase


class SpiderPpwSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CustomUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers.setdefault(b'User-Agent', agent)


class CustomHttpProxyMiddleware(object):

    redis_db = RedisDatabase()

    def process_request(self, request, spider):
        # Set the location of the proxy
        if self.redis_db.ip_pond():
            ip, port = random.choice(list(self.redis_db.ip_pond()))
            print('代理：',ip, port)
            request.meta['proxy'] = 'http://' + str(ip) + ':' + str(port)
            encode_user_pass = base64.b64encode(''.encode()).decode()
            request.headers['Proxy-Authorization'] = 'Basic ' + encode_user_pass
        else:
            pass


class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        return response


class CustomSpiderMiddleware():
    # TODO:
    pass

class CustomCookieMiddleware(RetryMiddleware):

    redis_db = RedisDatabase()

    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        cookie = self.redis_db.get_cookie()
        if cookie:
            request.cookies = cookie
            request.meta['accountText'] = cookie

    def process_response(self, request, response, spider):
        if response.status != 200 or 301:
            self.redis_db.refresh_cookie()
