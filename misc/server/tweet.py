# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_, desc

from football.models import Feeds, Articles, ArticleContents, db_connect
from pprint import pprint

from football.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

import json
import requests
from requests_oauthlib import OAuth1Session


session_maker = sessionmaker(bind=db_connect())
session = session_maker()

result = session.query(Articles.title, Articles.hash, ArticleContents.primary_image_url).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.extracted_content != None, ArticleContents.primary_image_url != None, ArticleContents.tweeted == False, ArticleContents.similar_article_calculated == True).order_by(desc(Articles.published_at)).limit(1).one()

twitter = OAuth1Session(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

if not result:
    print('Article not found')
    exit()

article_title, article_hash, primary_image_url = result

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

files = {"media" : requests.get(primary_image_url).content}
req_media = twitter.post(url_media, files = files)

if req_media.status_code != 200:
    print ("Image upload failed: %s", req_media.text)
    exit()

media_id = json.loads(req_media.text)['media_id']
print ("Media ID: %d" % media_id)

params = {'status': article_title + " https://the-football-spot.com/related/" + article_hash , "media_ids": [media_id]}
req_media = twitter.post(url_text, params = params)

if req_media.status_code != 200:
    print ("Text upload failed: %s", req_text.text)
    exit()

try:
    session.query(ArticleContents).filter(ArticleContents.article_hash == article_hash).update({"tweeted": True})
    session.commit()
except Exception as e:
    print(e)
    session.rollback()
    raise
finally:
    session.close()

print ("OK")
