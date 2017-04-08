# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CustomItem(scrapy.Item):
    def __getitem__(self, key):
        if key in self.fields:
            return self._values[key]
        else:
            return None