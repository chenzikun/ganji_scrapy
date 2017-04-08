import scrapy
from . import CustomItem


class BaseItem(CustomItem):
    # 城市
    citycode = scrapy.Field()
    # 类型
    type = scrapy.Field()
    # 创建时间
    create_time = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 联系人
    contact = scrapy.Field()
    # url
    url = scrapy.Field()
    # 区域
    district = scrapy.Field()
    # 来源
    source = scrapy.Field()
    # 详情
    detail = scrapy.Field()
    # 面积 - 小面积
    area = scrapy.Field()
    sub_area = scrapy.Field()
    # 商圈
    business_center = scrapy.Field()
    # 收集时间
    collect_time = scrapy.Field()
    # 电话
    tel = scrapy.Field()


class LeaseItem(BaseItem):  # 24

    neighborhood = scrapy.Field()
    industry_type = scrapy.Field()
    address = scrapy.Field()
    engaged = scrapy.Field()

    rent = scrapy.Field()
    rent_unit = scrapy.Field()

    img = scrapy.Field()
    # 为空
    industry = scrapy.Field()
    cost = scrapy.Field()
    cost_unit = scrapy.Field()
    minus_rent = scrapy.Field()

    # id = scrapy.Field()
    # shop_state = scrapy.Field()
    # shop_name = scrapy.Field()
    # suit = scrapy.Field()


class RentItem(BaseItem):  # 24
    neighborhood = scrapy.Field()
    industry_type = scrapy.Field()
    rent = scrapy.Field()
    rent_unit = scrapy.Field()
    # 为空
    img = scrapy.Field()
    engaged = scrapy.Field()
    address = scrapy.Field()
    cost = scrapy.Field()
    cost_unit = scrapy.Field()
    minus_rent = scrapy.Field()
    industry = scrapy.Field()


class TransferItem(BaseItem):  # 24

    neighborhood = scrapy.Field()

    industry_type = scrapy.Field()
    address = scrapy.Field()
    rent = scrapy.Field()
    rent_unit = scrapy.Field()
    img = scrapy.Field()

    industry = scrapy.Field()
    cost = scrapy.Field()
    cost_unit = scrapy.Field()

    engaged = scrapy.Field()
    minus_rent = scrapy.Field()
