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

from football.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

import json, settings
from requests_oauthlib import OAuth1Session


session_maker = sessionmaker(bind=db_connect())
session = session_maker()

result = session.query(ArticleContents.title, Articles.hash, ArticleContents.primary_image_url).filter(Articles.hash == ArticleContents.article_hash, Articles.feed_id == Feeds.id, ArticleContents.extracted_content != None, ArticleContents.primary_image_url != None, ArticleContents.tweeted == False, ArticleContents.similar_article_calculated = True).order_by(desc(Article.published_at)).limit(1)

twitter = OAuth1Session(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

files = {"media" : open(result.primary_image_url, 'rb')}
req_media = twitter.post(url_media, files = files)

if req_media.status_code != 200:
    print ("Image upload failed: %s", req_media.text)
    exit()

media_id = json.loads(req_media.text)['media_id']
print ("Media ID: %d" % media_id)

params = {'status': result.title + " https://the-football-spot.com/related/" + result.article_hash , "media_ids": [media_id]}
req_media = twitter.post(url_text, params = params)

if req_media.status_code != 200:
    print ("Text upload failed: %s", req_text.text)
    exit()

print ("OK")
