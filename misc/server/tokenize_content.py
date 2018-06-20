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

from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import *
from janome.tokenfilter import *

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from nltk.tokenize import word_tokenize

from filters import FootballCompoundNounFilter, FootballNounFilter

import pickle

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id).order_by(ArticleContents.id).all()
#results = session.query(ArticleContents, Articles, Feeds).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.id == 45).order_by(ArticleContents.id).all()

char_filters = [UnicodeNormalizeCharFilter(),
RegexReplaceCharFilter('&[^&]+;', '')
]
tokenizer = Tokenizer(mmap=True)
#token_filters = [POSStopFilter(['接続詞', '記号', '助詞', '助動詞'])]
#token_filters = [POSStopFilter(['接続詞', '記号', '助詞', '助動詞']), TokenCountFilter(att='surface')]
#token_filters = []
token_filters = [FootballCompoundNounFilter(), FootballNounFilter(), POSKeepFilter('名詞')]
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
                #print(token)

        elif feed.language == "en":
            words = word_tokenize(content)
        trainings.append(TaggedDocument(words, tags=[article.hash]))
    except Exception as e:
        print(e)

session.close()

f = open(script_dir + '/../../var/models/tokenized.pickle','wb')
pickle.dump(trainings, f)
f.close()
