#! -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime, Time, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from pprint import pprint
import codecs
import os

DeclarativeBase = declarative_base()

#def create_items_table(engine):
#    """"""
#    DeclarativeBase.metadata.create_all(engine)

#def drop_items_table(engine):
    #DeclarativeBase.metadata.drop_all(engine)

#def insert_items_data(engine):
    #for insert in codecs.open('sql/setup.sql', 'r', 'utf-8'):
    #    insert = insert.strip()
    #    if insert:
    #        engine.engine.execute(sqlalchemy.text(insert))

class CrawlerJobs(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "crawler_jobs"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, nullable=True)
    target = Column(String, nullable=True)
    instruction = Column(String, nullable=True)
    type = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    additional_information = Column(String, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)


class CrawlerJobLogs(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "crawler_job_logs"

    id = Column(Integer, primary_key=True)
    crawler_job_id = Column(Integer, nullable=True)
    feed_id = Column(Integer, nullable=True)
    target = Column(String, nullable=True)
    instruction = Column(String, nullable=True)
    type = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    additional_information = Column(String, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retry_at = Column(DateTime, nullable=True)
    job_created_at = Column(DateTime, nullable=True)
    job_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)

class CurrentCrawlerJobs(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "current_crawler_jobs"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
