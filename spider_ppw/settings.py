# -*- coding: utf-8 -*-

# Scrapy settings for spider_ppw project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'spider_ppw'

SPIDER_MODULES = ['spider_ppw.spiders']
NEWSPIDER_MODULE = 'spider_ppw.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spider_ppw (+http://www.yourdomain.com)'
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'spider_ppw.middlewares.CustomUserAgentMiddleware': 400,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'spider_ppw.middlewares.CustomUserAgentMiddleware': 1,
   # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
   # 'spider_ppw.middlewares.CustomHttpProxyMiddleware': 100,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'spider_ppw.pipelines.SpiderPpwPipeline': 300,
   'spider_ppw.pipelines.CustomRedisPipeline': 300,
   # 'scrapy_redis.pipelines.RedisPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# log相关
# LOG_ENABLED默认为True
# LOG_ENABLED = False
# log_level， CRITICAL、 ERROR、WARNING、INFO、DEBUG
LOG_LEVEL = 'ERROR'

# redis
# 启用Redis调度存储请求队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 确保所有的爬虫通过Redis去重
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# slave的ip为master的ip地址，主机需要关闭redis的保护模式
#REDIS_URL = 'redis://192.168.0.61:6379'
REDIS_URL = 'redis://127.0.0.1:6379'

# mysql配置
MYSQL_CONFIG = {'host': '192.168.1.253',
                'port': 20002,
                'user': 'chenzikun',
                'password': 'ppwchenzikun',
                'db': 'xw',
                'charset': 'utf8mb4'
                }

# MYSQL_CONFIG = {'host': '127.0.0.1',
#                 'port': 3306,
#                 'user': 'root',
#                 'password': '',
#                 'db': 'demo',
#                 'charset': 'utf8mb4'
#                 }
