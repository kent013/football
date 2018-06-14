# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../")

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

from FootballFilter import FootballFilter

import pickle

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).limit(2).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 16).order_by(ArticleContents.id).all()

char_filters = [UnicodeNormalizeCharFilter(),
RegexReplaceCharFilter('&[^&]+;', '')
]
tokenizer = Tokenizer(mmap=True)
#token_filters = [POSStopFilter(['接続詞', '記号', '助詞', '助動詞'])]
#token_filters = [POSStopFilter(['接続詞', '記号', '助詞', '助動詞']), TokenCountFilter(att='surface')]
#token_filters = []
token_filters = [POSKeepFilter(['名詞']), FootballFilter()]
analyzer = Analyzer(char_filters, tokenizer, token_filters)

print('Start tokenize')
trainings = []
for result in results:
    try:
        article_content, article, feed = result
        print('  ' + article.url)
        content = article_content.extracted_content
        words = []
        if feed.language == "ja":
            tokens = list(analyzer.analyze(content))
            for token in tokens:
                words.append(token.surface)
        elif feed.language == "en":
            words = word_tokenize(content)
        trainings.append(TaggedDocument(words, tags=[article.hash]))
    except Exception as e:
        print(e)

session.close()

f = open('models/tokenized.pickle','wb')
pickle.dump(trainings, f)
f.close()
