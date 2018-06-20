# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from football.models import Articles, ArticleContents, db_connect
from pprint import pprint
import re
from datetime import datetime
from datetime import timedelta
from datetime import date
from football.items import FootballArticleItem, FootballArticleContentItem
from scrapy import log
import dateutil.parser

class FootballPipeline(object):
    def __init__(self):
        engine = db_connect()
        #engine.echo = True
        #create_items_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        if isinstance(item, FootballArticleItem):
            return self.process_article(item, spider)
        elif isinstance(item, FootballArticleContentItem):
            return self.process_article_content(item, spider)

    def process_article(self, item, spider):
        session = self.Session()
        try:
            result = session.query(Articles).filter(Articles.hash == item['hash']).count()

            if result:
                spider.mark_job_as_failed_with_session(session, 'hash exists in db', False)
                session.commit()
                return

            article = Articles()
            article.title = item['title']
            article.summary = item['summary']
            article.creator = item['creator']
            article.url = item['url']
            article.hash = item['hash']
            article.subject = item['subject']
            article.feed_id = item['feed_id']
            article.published_at = item['published_at'] if 'published_at' in item else datetime.now()
            article.scraped_at = item['scraped_at']

            session.add(article)

            spider.mark_job_as_completed()
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            spider.mark_job_as_failed_with_session(session, 'Error at Pipeline, saving article', True)
            session.commit()
            raise
        finally:
            session.close()

    def process_article_content(self, item, spider):
        session = self.Session()
        try:
            result = session.query(ArticleContents).filter(ArticleContents.article_hash == item['article_hash']).count()

            if result:
                spider.mark_job_as_failed_with_session(session, 'hash exists in db', False)
                session.commit()
                return

            content = ArticleContents()
            content.content = item['content']
            content.article_hash = item['article_hash']
            content.content_hash = item['content_hash']

            session.add(content)

            spider.mark_job_as_completed()
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            spider.mark_job_as_failed_with_session(session, 'Error at Pipeline, saving article_content', True)
            session.commit()
            raise
        finally:
            session.close()
