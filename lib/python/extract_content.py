# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint
from dragnet import extract_content, extract_content_and_comments
from extractcontent3 import ExtractContent

import math

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 16).order_by(ArticleContents.id).all()

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
