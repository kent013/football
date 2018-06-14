# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import hashlib
import urllib
import time
import atexit
import subprocess
import random
from pprint import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging

import dateutil.parser

import scrapy
from scrapy import log
from scrapy import signals
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import Rule
from scrapy.spider import Spider
from scrapy.http.request import Request
from scrapy.http import FormRequest
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.xlib.pydispatch import dispatcher
from http.cookies import SimpleCookie

from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from sqlalchemy.engine import ResultProxy
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_

from common_models import CrawlerJobs, CrawlerJobLogs, CurrentCrawlerJobs
from football.models import db_connect
from football.settings import BOT_NAME, SLACK_WEBHOOK, SLACK_MSG_ROOM_PARSER_NOT_FOUND, SLACK_MSG_ROOM_PARSER_ERROR, SLACK_NOTIFY_USERS

import slackweb

try:
    from ota.settings import SQL_DEBUG_MODE
    if SQL_DEBUG_MODE:
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
except:
    pass


class CommonSpider(Spider):
    service_id = None
    start_urls = ()
    engine = None
    Session = None
    arguments = []
    crawler_job = None
    crawler_job_id = None

    slack = None
    last_slack_message = None

    def __init__(self, *a, **arguments):
        super(CommonSpider, self).__init__(*a, **arguments)
        self.arguments = arguments

        #if self.is_other_spider_running():
        #    sys.exit('There is another running spider')
        #    return
        #self.write_pid_file()
        atexit.register(self.remove_pid_file)

        self.engine = db_connect()
        self.Session = sessionmaker(bind=self.engine)

    #指定されたURLからrequestを作成。crawl_idとaddress_idの設定をする
    def make_requests_from_url(self, url):
        return super(CommonSpider, self).make_requests_from_url(url)

    #validate response and clear/refresh/markas_failed the job
    def validate_response(self, expected_url, response):
        raise NotImplementedError

    def cookie_list(self, cookiestr):
        cookie = SimpleCookie()
        cookie.load(cookiestr)
        cookies = []
        for key, morsel in cookie.items():
            cookies.append({"name": key, "value": morsel.value, "expires": morsel["expires"], "path": morsel["path"], "domain": morsel["domain"], "secure": morsel["secure"], "max-age": morsel["max-age"]})
            #cookies.append(morsel)
        return cookies

    def cookie_dict(self, cookiestr):
        cookie = SimpleCookie()
        cookie.load(cookiestr)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

    def cookie_array(self, cookiestrs):
        C = SimpleCookie()
        for cookiestr in cookiestrs:
            C.load(cookiestr)
        cookies = []
        for key, morsel in C.items():
            expiry = None
            if morsel['expires']:
                parsed_expires = dateutil.parser.parse(morsel['expires'])
                expiry = int(time.mktime(parsed_expires.timetuple()))
            cookies.append({
                'name':     morsel.key,
                'value':    morsel.value,
                'expires':  morsel['expires'],
                'expiry':   expiry,
                'path':     morsel['path'],
                'domain':   morsel['domain'],
                'secure':   True if morsel['secure'] else False,
                'httponly': True if morsel['httponly'] else False
            })
        return cookies

    def get_crawler_job(self, session, retry = 3):
        job = None
        for i in range(0, retry):
            try:
                return self.get_crawler_job_worker(session)
            except NoResultFound as e:
                print('missed')
                pass
            except OperationalError as e:
                print(e)
                self.print_error('Deadlock detected...' + str(e), False)
                pass
            time.sleep(0.5)
        return None

    #get one crawler job from queue
    def get_crawler_job_worker(self, session):
        raise NotImplementedError

    def add_current_crawler_job(self, session):
        try:
            current_job = CurrentCrawlerJobs()
            current_job.feed_id = self.crawler_job.feed_id
            current_job.type = 'refresh_cookies'
            session.add(current_job)
            session.flush()
            return True
        except (InvalidRequestError, IntegrityError):
            session.rollback()
            pass
        return False

    def save_crawler_job_log(self, job, session):
        log = CrawlerJobLogs()
        log.crawler_job_id = job.id
        log.feed_id = job.feed_id
        log.target = job.target
        log.instruction = job.instruction
        log.type = job.type
        log.retry_count = job.retry_count
        log.priority = job.priority
        log.error_message = job.error_message
        log.additional_information = job.additional_information
        log.failed_at = job.failed_at
        log.completed_at = job.completed_at
        log.retry_at = job.retry_at
        log.job_created_at = job.created_at
        log.job_updated_at = job.updated_at
        log.started_at = job.started_at
        log.created_at = datetime.now()
        session.add(log)

    #jobを成功としてマークする
    def mark_job_as_completed(self):
        session = self.Session()
        try:
            self.mark_job_as_completed_with_session(session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_job_as_completed_with_session(self, session):
        self.crawler_job.updated_at = datetime.now()
        self.crawler_job.completed_at = datetime.now()
        self.save_crawler_job_log(self.crawler_job, session)
        session.delete(self.crawler_job)

    #jobを失敗としてマークするやつのsessionあり
    def mark_job_as_failed(self, message, retry):
        session = self.Session()
        try:
            self.mark_job_as_failed_with_session(session, message, retry)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    #jobを失敗としてマークする。retryフラグが立っていれば、jobをクローンして再作成
    def mark_job_as_failed_with_session(self, session, message, retry):
        self.crawler_job.updated_at = datetime.now()
        self.crawler_job.failed_at = datetime.now()
        self.crawler_job.error_message = message
        self.save_crawler_job_log(self.crawler_job, session)
        session.delete(self.crawler_job)

        if not retry:
            return

        results = session.query(CrawlerJobs).filter(CrawlerJobs.feed_id == self.crawler_job.feed_id, CrawlerJobs.type == self.crawler_job.type, CrawlerJobs.started_at == None)
        if results.count() > 0:
            return

        job = self.clone_job()
        if job.priority <= 0:
            job.priority = 1
        else:
            job.priority *= 2
        job.retry_count += 1
        job.retry_at = job.created_at + timedelta(seconds=job.retry_count * 30)
        session.add(job)

        return job

    #jobを元に戻す
    def mark_job_notstarted(self, session):
        self.crawler_job.updated_at = datetime.now()
        self.crawler_job.started_at = None
        session.add(self.crawler_job)

    #jobをクローン
    def clone_job(self, retry = False):
        job = CrawlerJobs()
        job.feed_id = self.crawler_job.feed_id
        job.type = self.crawler_job.type
        job.target = self.crawler_job.target
        job.instruction = self.crawler_job.instruction
        job.additional_information = self.crawler_job.additional_information
        job.target = self.crawler_job.target
        job.priority = self.crawler_job.priority
        job.created_at = datetime.now()
        job.updated_at = datetime.now()
        job.started_at = None
        job.retry_count = self.crawler_job.retry_count
        return job

    def get_text_by_css(self, css, response):
        element = self.get_element_by_css(css, response)
        if not element:
            return
        texts = element.xpath('text()')
        if len(texts) > 0:
            return texts[0].extract().split()
        return None

    def get_element_by_css(self, css, response):
        element = response.css(css)
        if len(element) > 0:
            return element[0]
        return None

    def get_attribute_by_css(self, css, attribute_name, response):
        element = self.get_element_by_css(css, response)
        if not element:
            return None
        attributes = element.xpath('@' + attribute_name)
        if len(attributes) > 0:
            return attributes[0].extract().split()
        return None

    def xstr(s):
        if s is None:
            return ''
        return str(s)

    def is_other_spider_running(self):
        pid = self.read_pid_file()
        if not pid:
            return False
        return True

    def remove_pid_file(self):
        pid = self.read_pid_file()
        if pid:
            pid_path = self.pid_file_path()
            os.remove(pid_path)

    def write_pid_file(self):
        pid = os.getpid()
        pid_path = self.pid_file_path()
        f = open(pid_path, 'w')
        try:
            f.write(str(pid))
        except Exception as e:
            print(e)
            sys.exit('pid file exist. but it is not writable' + pid_path)
        finally:
            f.close()

    def read_pid_file(self):
        pid_path = self.pid_file_path()
        if not os.path.exists(pid_path):
            return None
        f = open(pid_path)
        try:
            pid = f.read()
            return pid
        except Exception as e:
            print(e)
            sys.exit('pid file exist. but it is not readable.' + pid_path)
        finally:
            f.close()

    def pid_file_path(self):
        if not 'pid_path' in self.arguments:
            sys.exit('argument pid_path is needed')
        pid_path = self.arguments['pid_path']
        pid_dir = os.path.dirname(pid_path)
        if not os.path.exists(pid_dir):
            sys.exit('directory not found in pid_path :' + pid_path)
        if not os.access(pid_dir, os.W_OK):
            sys.exit('directory is not writable : ' + pid_path)
        return pid_path

    def model_to_item(self, model, item):
        for attr in item.fields:
            if not hasattr(model, attr):
                continue
            item[attr] = getattr(model, attr)
        return item

    def print_error(self, message, notify_message_to_slack):
        self.logger.info(message)
        if not notify_message_to_slack or not 'notify' in self.arguments or not self.arguments['notify'] == '1':
            return
        self.notify_slack(message)

    def print_scraping_error(self, message, response, notify_message_to_slack = False):
        if self.crawler_job:
            message += ' crawler_job.id:' + str(self.crawler_job_id)
        if response:
            message += ', url:' + response.url
        self.print_error(message, notify_message_to_slack)

    def notify_slack(self, message):
        hostname = os.uname()[1]
        if 'NICKNAME' in os.environ:
            hostname = os.environ['NICKNAME']
        message += ' at ' + hostname
        if self.last_slack_message == message:
            return

        self.last_slack_message = message
        slack = self.get_slack()
        slack.notify(text=SLACK_NOTIFY_USERS + ' ' + message, username="pms_crawler", icon_emoji=":house", mrkdwn=True)

    def get_slack(self):
        if not self.slack:
            self.slack = slackweb.Slack(url = SLACK_WEBHOOK)
        return self.slack
