# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
class FootballSiteCategoryItem(scrapy.Item):
    id = scrapy.Field()
    display_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballSiteTypeItem(scrapy.Item):
    id = scrapy.Field()
    display_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballFeedItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    language = scrapy.Field()
    feed_url = scrapy.Field()
    site_url = scrapy.Field()
    description = scrapy.Field()
    site_category_id = scrapy.Field()
    site_type_id = scrapy.Field()
    enabled = scrapy.Field()
    scraped_at = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballArticleItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    creator = scrapy.Field()
    url = scrapy.Field()
    hash = scrapy.Field()
    subject = scrapy.Field()
    feed_id = scrapy.Field()
    published_at = scrapy.Field()
    scraped_at = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballArticleContentItem(scrapy.Item):
    id = scrapy.Field()
    content = scrapy.Field()
    extracted_content = scrapy.Field()
    primary_image_url = scrapy.Field()
    article_hash = scrapy.Field()
    content_hash = scrapy.Field()
    similar_article_calculated = scrapy.Field()
    tweeted = scrapy.Field()
    token_extracted = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballTokenItem(scrapy.Item):
    id = scrapy.Field()
    base_form = scrapy.Field()
    part_of_speech1 = scrapy.Field()
    part_of_speech2 = scrapy.Field()
    part_of_speech3 = scrapy.Field()
    part_of_speech4 = scrapy.Field()
    occurrence_count = scrapy.Field()
    is_noise = scrapy.Field()
    hash = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballTokenTypeItem(scrapy.Item):
    id = scrapy.Field()
    display_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballTokenRelationshipTypeItem(scrapy.Item):
    id = scrapy.Field()
    display_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class FootballSimilarArticleItem(scrapy.Item):
    id = scrapy.Field()
    article_hash = scrapy.Field()
    similar_article_hash = scrapy.Field()
    score = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
