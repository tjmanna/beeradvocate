# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BeeradvocateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    style = scrapy.Field()
    brewery = scrapy.Field()
    score = scrapy.Field()
    style_rank = scrapy.Field()
    overall_rank = scrapy.Field()
    abv = scrapy.Field()
    avg_rating = scrapy.Field()
    num_reviews = scrapy.Field()
    num_ratings = scrapy.Field()
    region = scrapy.Field()
    country = scrapy.Field()
    availability = scrapy.Field()

