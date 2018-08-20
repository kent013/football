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

from filters import FootballCompoundNounFilter, FootballNounFilter, FootballCompoundNounFilter

import pickle
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
parser.add_argument("-c","--recount",
  action = "store_true"
)
parser.add_argument("-d","--dryrun",
  action = "store_true"
)

args = parser.parse_args()

engine=db_connect()

if args.renew:
    connection = engine.connect()
    result = connection.execute("TRUNCATE tokens")
    result = connection.execute("UPDATE article_contents SET token_extracted = FALSE")
    connection.close()
elif args.recount:
    connection = engine.connect()
    result = connection.execute("UPDATE tokens SET occurrence_count = 0")
    result = connection.execute("UPDATE article_contents SET token_extracted = FALSE")
    connection.close()


print('Start tokenize')

char_filters = [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter('&[^&]+;', '')]
tokenizer = Tokenizer(mmap=True)
token_filters = [FootballCompoundNounFilter(), FootballNounFilter(), POSKeepFilter('名詞')]
analyzer = Analyzer(char_filters, tokenizer, token_filters)

session_maker = sessionmaker(bind=db_connect())
session = session_maker()

article_contents = session.query(ArticleContents).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.token_extracted == False, ArticleContents.extracted_content != None, Feeds.language == 'ja').order_by(ArticleContents.id)#.limit(100).offset(400)

dbtokens = {}
count = 1;
total = article_contents.count()
print('There are %d contents to process' % total)
try:
    for article_content in article_contents:
        print('  %7d / %d, %s' % (count, total, article_content.article_hash))
        content = article_content.extracted_content
   
        words = []
        tokens = list(analyzer.analyze(content))
        for token in tokens:
            dbtoken = None
            if token.base_form in dbtokens:
                dbtoken = dbtokens[token.base_form]
            elif not args.renew:
                dbtoken = session.query(Tokens).filter(Tokens.base_form == token.base_form).one_or_none()

            if dbtoken:
                dbtoken.occurrence_count = dbtoken.occurrence_count + 1
            else:
                pos = token.part_of_speech.split(",")
                dbtoken = Tokens()
                dbtoken.base_form = token.base_form
                dbtoken.part_of_speech1 = None if pos[0] is '*' else pos[0]
                dbtoken.part_of_speech2 = None if pos[1] is '*' else pos[1]
                dbtoken.part_of_speech3 = None if pos[2] is '*' else pos[2]
                dbtoken.part_of_speech4 = None if pos[3] is '*' else pos[3]
                dbtoken.occurrence_count = 1
                dbtokens[token.base_form] = dbtoken
            
            if not args.dryrun: session.add(dbtoken)
          
        article_content.token_extracted = True
        if not args.dryrun: session.add(article_content)
        count += 1
    
    if not args.dryrun: session.commit()
except Exception as e:
    session.rollback()
    print(e)
finally:
    session.close()

print('  Done')