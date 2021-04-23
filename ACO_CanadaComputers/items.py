# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CC_Product(scrapy.Item):
    name = scrapy.Field()
    img = scrapy.Field()
    item_id = scrapy.Field()
    stock = scrapy.Field()
