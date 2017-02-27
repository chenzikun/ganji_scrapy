import requests
import json
import redis
import logging
# from ..settings import REDIS_URL

logger = logging.getLogger(__name__)

# rdb = redis.Redis.from_url(REDIS_URL, db=2, decode_responses=True)

login_url = ''

# 获取cookies
def get_cookie(account, password):
    req = requests.Session()
    payload = {
        'log': account,
        'pwd': password,
        'remember_me': 'forever',
        'wp-submit': '登录',
    }
    response = req.post(login_url, data=payload)
    cookies = response.cookies.get_dict()
    logger.warning('获取Cookie成功！(账号为：{})'.format(account))
    return json.dump(cookies)