# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, SimilarArticles, db_connect
from pprint import pprint

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

m = Doc2Vec.load('models/doc2vec.model')

engine=db_connect()

if args.renew:
    connection = engine.connect()
    result = connection.execute("TRUNCATE similar_articles")
    connection.close()

session_maker = sessionmaker(bind=engine)
session = session_maker()

results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).all()

print('Start calculation')
for result in results:
    try:
        article_content, article, feed = result
        print('  %s %s' % (article.url, article.title))
        if not args.renew and session.query(SimilarArticles).filter(SimilarArticles.article_hash == article.hash).count():
            continue

        similar_articles = m.docvecs.most_similar(article.hash)

        for similar_article in similar_articles:
            model = SimilarArticles()
            model.article_hash = article.hash
            model.similar_article_hash = similar_article[0]
            model.score =  similar_article[1]
            session.add(model)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise
    finally:
        session.close()