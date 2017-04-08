import requests
import logging

logger = logging.getLogger(__name__)

login_url = 'https://passport.ganji.com/login.php?next=/'


# 获取cookies
def get_cookie():
    req = requests.Session()
    payload = {
        'login_username': '15151829176',
        'login_password': 'czk19911001',
        'setcookie': 'checked',
        'chk-vm': '登录赶集',
    }
    response = req.post(login_url, data=payload)
    cookies = response.cookies.get_dict()

    return cookies
