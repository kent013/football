# -*- coding: utf-8 -*-

# Scrapy settings for football project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../lib/python/src/")

BOT_NAME = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0'

SPIDER_MODULES = ['football.spiders']
NEWSPIDER_MODULE = 'football.spiders'

HTTPCACHE_STORAGE = 'scrapy.contrib.httpcache.FilesystemCacheStorage'
HTTPCACHE_DIR = 'cache'
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_IGNORE_HTTP_CODES = [500, 501, 502, 503, 400, 401, 402, 403, 404]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
  'football.pipelines.FootballPipeline': 300
}

DATABASE = {
    'drivername': 'mysql',
    'host': 'localhost',
    'port': '3306',
    'username': 'root',
    'password': '',
    'database': 'football'
}

USER_AGENT = BOT_NAME
DOWNLOAD_DELAY = 0
RANDOMIZE_DOWNLOAD_DELAY = 0
LOG_LEVEL='ERROR'
SQL_DEBUG_MODE = 0

SLACK_WEBHOOK = 'https://hooks.slack.com/services'
SLACK_NOTIFY_USERS = '@kent013'
SLACK_MSG_ROOM_PARSER_ERROR = "Parser error is occurred. Check it out now! "
SLACK_MSG_ROOM_PARSER_NOT_FOUND = "Parse function for rooms is not found. Perhaps Airbnb's view is changed. Check it out now!"

TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
