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
# from .constant.ip_pond import ip_pond


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

class CustomHttpProxyMiddleware(HttpProxyMiddleware):

    def process_request(self, request, spider):
        # Set the location of the proxy
        ip_instance = random.choice([])
        request.meta['proxy'] = "http//{}:{}".format(ip_instance.ip, ip_instance.port)

        # Use the following lines if your proxy requires authentication
        proxy_user_pass = "USERNAME:PASSWORD"
        # setup basic authentication for the proxy
        encoded_user_pass = base64.encodestring(proxy_user_pass)
        request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class CookieMiddleware(RetryMiddleware):
    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)
        self.rconn = redis.from_url(settings['REDIS_URL'], db=1, decode_responses=True)  ##decode_responses设置取出的编码为str
        # init_cookie(self.rconn, crawler.spider.name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        redisKeys = self.rconn.keys()
        while len(redisKeys) > 0:
            elem = random.choice(redisKeys)
            if spider.name + ':Cookies' in elem:
                cookie = json.loads(self.rconn.get(elem))
                request.cookies = cookie
                request.meta["accountText"] = elem.split("Cookies:")[-1]
                break
            # else:
            # redisKeys.remove(elem)

    # def process_response(self, request, response, spider):

        # """
        # 下面的我删了，各位小伙伴可以尝试以下完成后面的工作

        # 你需要在这个位置判断cookie是否失效

        # 然后进行相应的操作，比如更新cookie  删除不能用的账号

        # 写不出也没关系，不影响程序正常使用，

        # """
