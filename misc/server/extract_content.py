# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from getsizes import getsizes

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint
from dragnet import extract_content, extract_content_and_comments
from extractcontent3 import ExtractContent

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import diskcache

import math
import re

import argparse

parser = argparse.ArgumentParser(
  prog="extract_content",
  usage="",
  description="extract content from article",
  epilog = "",
  add_help = True,
)

parser.add_argument("-n","--renew",
  action = "store_true"
)
args = parser.parse_args()

dc = diskcache.Cache(script_dir + '/../../var/images')

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

if args.renew:
    results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).all()
else:
    results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.extracted_content == None).order_by(ArticleContents.id).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 5).order_by(ArticleContents.id).all()

#extractor = ExtractContent({"debug":True, 'threthold': 100})
extractor = ExtractContent()

try:
    for result in results:
        article_content, article, feed = result
        text = ''
        content = article_content.content
        pprint(article.url)
        try:
            if feed.language == 'ja':
                extractor.analyse(content)
                text, title = extractor.as_text()
                text = re.sub('名前：[^\s]+', '', text)
                text = re.sub('ID:[^\s]+', '', text)
                text = re.sub('https?:[^\s]+', '', text)
                text = re.sub('[0-9]+ +[0-9]+:[0-9]+:[0-9]+\.[0-9]+', '', text)
                text = re.sub('[<＜>＞]+\s?[0-9\s]+', '', text)
                text = re.sub('引用元：', '', text)
                text = re.sub('[0-9]+\s+：[0-9]+\/[0-9]+\/[0-9]+.+?[0-9]+:[0-9]+:[0-9]+\.[0-9]+', '', text)
                text = re.sub('<[^>]+>', '', text)
            else:
                text = extract_content(content)
        except Exception as e:
            print(e)
   
        if not text:
            text = article.summary
        article_content.extracted_content = article.title.strip() + " " + text.strip()

        # extract main image
        bs = BeautifulSoup(content, "lxml")
        max = 0
        primary_image_url = None

        for image_url in bs.find_all('img'):
            src = image_url.get('src')

            if not src or re.match('data:image', src):
                continue

            if not re.match('http', src):
                src = urljoin(article.url, src)

            if re.search('common|share|button|footer|header|head|logo|menu|banner|parts|thumbnail|ranking|icon|copyright|feedly|ico|seesaablog.gif|fan_read.gif|fan_received.gif|captcha|/n.gif|/u.gif|chart.apis.google.com|images-amazon.com|facebook.com|powered_by|rss.rssad.jp|blank|navi|custom.search.yahoo.co.jp|pixel|xrea.com|w=64|i2i|microad.jp|resize.blogsys.jp|b.hatena.ne.jp|accesstrade.net|poweredby|scorecardresearch.com|ssc.api.bbc.com|sa.bbc.co.uk|amazon-adsystem.com|zero-tools.com|clicktrack2.ziyu.net|nakanohito.jp|pv.geki.jp|arrow_left|arrow_right|spacer.gif|spike.png|wp-content/themes', src):
                continue
            print("  " + src)
            width, height = getsizes(src, dc)
            if not width:
                continue
            square = width * height
            aspect_ratio = width / height
            if square > max and aspect_ratio > 0.5 and aspect_ratio < 1.8:
                primary_image_url = src
                max = square

        article_content.primary_image_url = primary_image_url
        if article_content.primary_image_url:
            print("  PRIMARY IMAGE: " + article_content.primary_image_url)
        else:
            print("  PRIMARY IMAGE: Not Detected")


        session.add(article_content)
    session.commit()
except Exception as e:
    print(e)
    session.rollback()
    raise
finally:
    session.close()
