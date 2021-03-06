# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/src/")
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
parser.add_argument("-d","--dryrun",
  action = "store_true"
)
args = parser.parse_args()

m = Doc2Vec.load(script_dir + '/../../var/models/doc2vec.model')

engine=db_connect()

if args.renew:
    connection = engine.connect()
    result = connection.execute("TRUNCATE similar_articles")
    result = connection.execute("UPDATE article_contents SET similar_article_calculated = 0")
    connection.close()

session_maker = sessionmaker(bind=engine)
session = session_maker()
session.expire_on_commit = False

results = session.query(Articles.hash).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.similar_article_calculated == False, ArticleContents.extracted_content != None).order_by(ArticleContents.id).all()

print('Start calculation')
try:
    for result in results:
        try:
            print('  %s' % (result.hash))
            similar_articles = m.docvecs.most_similar(result.hash, topn=20)

            for similar_article in similar_articles:
                model = SimilarArticles()
                model.article_hash = result.hash
                model.similar_article_hash = similar_article[0]
                model.score =  similar_article[1]
                if not args.dryrun:
                    session.add(model)
            if not args.dryrun:
                session.query(ArticleContents).filter(ArticleContents.article_hash == result.hash).update({"similar_article_calculated": True})
        except Exception as e:
            print(e)
    if not args.dryrun:
        session.commit()
except Exception as e:
    print(e)
    session.rollback()
    raise
finally:
    session.close()

print('  Done')
