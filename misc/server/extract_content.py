# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint
from dragnet import extract_content, extract_content_and_comments
from extractcontent3 import ExtractContent

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

parser.add_argument("-n","--new",
  action = "store_true"
)
args = parser.parse_args()

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

if args.new:
    results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.extracted_content == None).order_by(ArticleContents.id).all()
else:
    results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 2).order_by(ArticleContents.id).all()

#extractor = ExtractContent({"debug":True, 'threthold': 100})
extractor = ExtractContent()

try:
    for result in results:
        article_content, article, feed = result
        text = ''
        content = article_content.content
        pprint(article.url)
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

        if not text:
            text = article.summary
        article_content.extracted_content = article.title.strip() + " " + text.strip()
        session.add(article_content)
    session.commit()
except Exception as e:
    print(e)
    session.rollback()
    raise
finally:
    session.close()
