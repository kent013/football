# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/src/")
sys.path.append(script_dir + "/../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_

from football.models import Feeds, Articles, ArticleContents, Tokens, db_connect
from pprint import pprint

from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenfilter import POSKeepFilter

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from nltk.tokenize import word_tokenize

from filters import FootballCompoundNounFilter, FootballNounFilter
from neo4j_util import get_all_tokens

import pickle
import argparse

old_noise_tokens = []
engine=db_connect()
try:
    connection = engine.connect()
    results = connection.execute("SELECT * FROM old_tokens WHERE is_noise = true")
    for result in results:
        old_noise_tokens.append(result[1])
except Exception as e:
    print(e)
finally:
    connection.close()

session_maker = sessionmaker(bind=db_connect())
session = session_maker()
tokens = get_all_tokens()
try:
    for token in tokens:
        print(token)
        dbtoken = session.query(Tokens).filter(Tokens.base_form == token['name']).one_or_none()
        if dbtoken:
            dbtoken.hash = token['hash']
            session.add(dbtoken)
    for token in old_noise_tokens:
        dbtoken = session.query(Tokens).filter(Tokens.base_form == token).one_or_none()
        if dbtoken:
            dbtoken.is_noise = 1
            session.add(dbtoken)
    session.commit()
except Exception as e:
    session.rollback()
    print(e)
finally:
    session.close()

print('  Done')