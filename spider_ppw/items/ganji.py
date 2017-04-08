import scrapy

from . import CustomItem


class SpiderPpwItem(CustomItem):
    # 城市
    citycode = scrapy.Field()
    # 类型（店铺转让/出租招商/找店）
    type = scrapy.Field()
    # 发布时间
    create_time = scrapy.Field()
    # 收集时间
    collect_time = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 联系人
    contact = scrapy.Field()
    # 电话
    tel = scrapy.Field()
    # 详情URL
    url = scrapy.Field()
    # source
    source = scrapy.Field()


class SpiderPpwItemTransfer(SpiderPpwItem):
    """转店类"""
    # 租金价格
    rent = scrapy.Field()
    # 租金单位
    rent_unit = scrapy.Field()
    # 商铺面积
    area = scrapy.Field()
    # 商铺概况
    # overview = scrapy.Field()
    # 商铺状态(新铺/空铺/营业中)
    shop_state = scrapy.Field()
    # 商铺类型(商业街商铺/社区住宅底商/写字楼配套/宾馆酒店/旅游点商铺/主题卖场/百货购物中心/其他)
    industry_type = scrapy.Field()
    # 商铺名称
    shop_name = scrapy.Field()
    # 所在区域
    district = scrapy.Field()
    # 商圈
    business_center = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 适合经营
    suit = scrapy.Field()
    # 转让费
    # cost = scrapy.Field()
    # 商铺配套
    # supporting = scrapy.Field()
    # 房源状况
    detail = scrapy.Field()
    # 图片
    img = scrapy.Field()


class SpiderPpwItemRentOut(SpiderPpwItem):
    """出租类"""
    # 面积
    area = scrapy.Field()
    # 租金
    rent = scrapy.Field()
    # 租金单位
    rent_unit = scrapy.Field()
    # 商铺状态（新铺 / 空铺 / 营业中）
    shop_state = scrapy.Field()
    # 商铺类型（商业街商铺 / 社区住宅底商 / 写字楼配套 / 宾馆酒店 / 旅游点商铺 / 主题卖场 / 百货购物中心 / 其他
    industry_type = scrapy.Field()
    # 商铺名称
    shop_name = scrapy.Field()
    # 所在区域
    district = scrapy.Field()
    # 商圈
    business_center = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 适合经营
    suit = scrapy.Field()
    # 描述
    detail = scrapy.Field()
    # 图片
    img = scrapy.Field()


class SpiderPpwItemRentIn(SpiderPpwItem):
    """求租类"""
    # 期望租金
    rent = scrapy.Field()
    # 租金单位
    rent_unit = scrapy.Field()
    # 期望面积
    area = scrapy.Field()
    # 期望区域
    district = scrapy.Field()
    # 期望地址
    address = scrapy.Field()
    # 描述
    detail = scrapy.Field()
