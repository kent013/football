# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../")

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint

m = Doc2Vec.load('models/doc2vec.model')

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).limit(10).all()

print('Start calculation')
for result in results:
    try:
        article_content, article, feed = result
        print('  %s %s' % (article.url, article.title))
        similar_articles = m.docvecs.most_similar(article.hash)

        for similar_article in similar_articles:
            similar_article_result = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == similar_article[0], Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).one()

            sim_article_content, sim_article, sim_feed = similar_article_result
            print('      %f %s %s' % (similar_article[1], sim_article.url, sim_article.title))
    except Exception as e:
        print(e)

session.close()
