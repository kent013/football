# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/src/")
sys.path.append(script_dir + "/../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint

from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import *
from janome.tokenfilter import *

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from nltk.tokenize import word_tokenize

from filters import FootballCompoundNounFilter, FootballNounFilter, FootballCompoundNounFilter, FootballAliasFilter
from neo4j_util import get_word_aliases

import pickle
import argparse

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

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

results = session.query(ArticleContents.extracted_content, Articles.hash, Feeds.language).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.extracted_content != None).order_by(ArticleContents.id).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 45).order_by(ArticleContents.id).all()

aliases = get_word_aliases()

char_filters = [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter('&[^&]+;', '')]
tokenizer = Tokenizer(mmap=True)
token_filters = [FootballCompoundNounFilter(), FootballNounFilter(), POSKeepFilter('名詞'), FootballAliasFilter(aliases)]
analyzer = Analyzer(char_filters, tokenizer, token_filters)


print('Start tokenize')

trainings = {}
model_cache_path = script_dir + '/../../var/models/tokenized.pickle'
if not args.renew and os.path.isfile(model_cache_path):
    with open(model_cache_path, mode='rb') as f:
        trainings = pickle.load(f)

for result in results:
    try:
        if result.hash in trainings:
            continue
        if not result.extracted_content:
            continue
        print('  ' + result.hash)
        content = result.extracted_content
        words = []
        if result.language == "ja":
            tokens = list(analyzer.analyze(content))

            for token in tokens:
                words.append(token.surface)
        elif result.language == "en":
            words = word_tokenize(content)

        trainings[result.hash] = TaggedDocument(words, tags=[result.hash])
    except Exception as e:
        print(e)

session.close()

f = open(model_cache_path, 'wb')
pickle.dump(trainings, f)
f.close()

print('  Done')
