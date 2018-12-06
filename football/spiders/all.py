# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule
from scrapy.spiders import Spider
from scrapy.utils.serialize import ScrapyJSONEncoder

import logging

import json
import re
import hashlib
import urllib
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import ResultProxy
from sqlalchemy import or_, desc
from pprint import pprint
from datetime import datetime
from time import mktime
import random

import slackweb

from football.items import FootballFeedItem, FootballArticleItem, FootballArticleContentItem
from football.models import Feeds, Articles, db_connect
from common_models import CrawlerJobs
from common_spider import CommonSpider

import feedparser

def process_link(value):
    rep = re.sub(r'\?s=.+$', '', value)
    return rep

class AllSpider(CommonSpider):
    name = 'all'

    crawl_date = None
    crawl_instruction = {}

    def __init__(self, *a, **arguments):
        super(AllSpider, self).__init__(*a, **arguments)
        self.service_id = 1 #Football

        if 'create_db' in self.arguments:
            #drop_items_table(self.engine)
            #create_items_table(self.engine)
            #insert_items_data(self.engine)
            exit()

        session = self.Session()
        try:
            self.crawler_job = self.get_crawler_job(session)
            if not self.crawler_job:
                return
            print (self.crawler_job.id, self.crawler_job.type, self.crawler_job.target)

            if self.crawler_job.instruction:
                self.crawl_instruction = json.loads(self.crawler_job.instruction)

            if self.crawler_job.type == 'initial':
                feeds = session.query(Feeds).filter(Feeds.enabled == 1)
                for feed in feeds:
                    self.insert_feed_job(session, 'feed', feed, 0)
                self.mark_job_as_completed_with_session(session)
            else:
                url = None
                if self.crawler_job.type == 'feed':
                    url = self.crawler_job.target
                elif self.crawler_job.type == 'article':
                    url = self.crawler_job.target

                if not url:
                    msg = 'type:' + self.crawler_job.type + ' is not implemented'
                    print(msg)
                    self.mark_job_as_failed_with_session(session, msg, False)
                self.start_urls += (url,)

            session.flush()
            session.expunge(self.crawler_job)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_feed_job(self, session, job_type, feed, offset):
        job_count = session.query(CrawlerJobs).filter(CrawlerJobs.type == job_type, CrawlerJobs.feed_id == feed.id, CrawlerJobs.started_at == None).count()

        if job_count:
            return

        job = self.clone_job()
        job.type = job_type
        job.priority = 100
        job.target = feed.feed_url
        job.feed_id = feed.id
        encoder = ScrapyJSONEncoder()
        job.instruction = encoder.encode({'feed_id': feed.id, 'offset': offset})
        session.add(job)

    def parse_feed(self, response):
        if not self.validate_response(self.crawler_job.target, response):
            return

        rawdata = response.text
        if not rawdata:
            self.mark_job_as_failed('No response, feed', True)
            return

        rss = feedparser.parse(rawdata)

        session = self.Session()
        try:
            date = datetime.now()
            for entry in rss.entries:
                article_hash = hashlib.sha256(entry.link.encode('utf-8')).hexdigest()

                article_count = session.query(Articles).filter(Articles.hash == article_hash).count()

                if article_count:
                    continue

                article = FootballArticleItem()
                article['title'] = entry.title
                article['summary'] = entry.summary if 'summary' in entry else ""
                article['creator'] = entry.author if 'author' in entry else ""

                article['url'] = entry.link
                article['hash'] = article_hash
                article['subject'] = " ".join(map(str, entry.tags)) if 'tags' in entry else ""
                article['feed_id'] = self.crawler_job.feed_id
                if 'updated_parsed' in entry:
                    article['published_at'] = datetime.fromtimestamp(mktime(entry.updated_parsed))
                elif 'published_parsed' in entry:
                    article['published_at'] = datetime.fromtimestamp(mktime(entry.published_parsed))
                article['scraped_at'] = self.crawler_job.started_at

                if 'published_at' in article and article['published_at'] > datetime.now():
                    article['published_at'] = datetime.now()

                yield article

                job = self.clone_job()
                job.type = 'article'
                job.priority = 10000
                job.target = entry['link']
                session.add(job)
            self.mark_job_as_completed_with_session(session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def parse_article(self, response):
        if not self.validate_response(self.crawler_job.target, response):
            return

        content = FootballArticleContentItem()
        content['article_hash'] = hashlib.sha256(self.crawler_job.target.encode('utf-8')).hexdigest()
        content['content_hash'] = hashlib.sha256(response.text.encode('utf-8')).hexdigest()
        content['content'] = response.text

        return content

    #指定されたURLからrequestを作成。
    def make_requests_from_url(self, url):
        request = super(AllSpider, self).make_requests_from_url(url)
        request.meta['start_url'] = url
        request.meta['handle_httpstatus_list'] = list(range(400, 499)) + list(range(500, 599))
        request.meta['dont_cache'] = True
        if self.crawler_job.type == 'feed':
            request.callback = self.parse_feed
        elif self.crawler_job.type == 'article':
            request.callback = self.parse_article
        else:
            raise NotImplementedError('parser implementation for url is not found')
        return request

    #validate response and clear/refresh/markas_failed the job
    def validate_response(self, expected_url, response):
        if response.status >= 400 and response.status < 500 and not response.status in [403, 420]:
            self.logger.warning('%s: %s', (str(response.status), response.url))
            self.mark_job_as_failed('failed with ' + str(response.status), False)
            return False;
        if not response.status == 200:
            self.logger.warning('%s: %s', (str(response.status), response.url))
            self.mark_job_as_failed('failed with ' + str(response.status), True)
            return False
        self.logger.info('%s', response.url)
        return True

    #get one crawler job from queue
    def get_crawler_job_worker(self, session):
        results = session.query(CrawlerJobs).filter(CrawlerJobs.started_at == None).filter(or_(CrawlerJobs.retry_at == None, CrawlerJobs.retry_at < datetime.now())).order_by(desc(CrawlerJobs.priority)).with_entities(CrawlerJobs.id).limit(5).all()
        crawler_job = None
        if len(results) > 0:
            index = random.randint(0, len(results) - 1)
            job = results[index]
            crawler_job = session.query(CrawlerJobs).filter(CrawlerJobs.id == job.id, CrawlerJobs.started_at == None).with_lockmode('update').one()
        else:
            print('Job not found')
            return None

        crawler_job.started_at = datetime.now()
        crawler_job.updated_at = datetime.now()
        session.add(crawler_job)
        session.flush()

        self.crawler_job_id = crawler_job.id
        return crawler_job
