import requests
import pyquery


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Util(metaclass=Singleton):


    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1)AppleWebKit/537.36 ("
                             "KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
               'Accept': 'text / html, application / xhtml + xml'
               }

    def get_dom(self, url):
        rep = requests.get(url=url, headers=self.headers, timeout=10).content
        dom = pyquery.PyQuery(rep)
        return dom
