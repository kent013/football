#! -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime, Time, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import football.settings
from pprint import pprint
import codecs
import os
from datetime import datetime


DeclarativeBase = declarative_base()

def db_connect():
    """Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance.
    """
    football.settings.DATABASE['query'] = {'charset': 'utf8'}
    url = URL(**football.settings.DATABASE)
    return create_engine(url, encoding='utf-8')


#def create_items_table(engine):
#    """"""
#    DeclarativeBase.metadata.create_all(engine)

#def drop_items_table(engine):
#    DeclarativeBase.metadata.drop_all(engine)

#def insert_items_data(engine):
#    for insert in codecs.open('sql/setup.sql', 'r', 'utf-8'):
#        insert = insert.strip()
#        if insert:
#            engine.engine.execute(sqlalchemy.text(insert))

class SiteCategories(DeclarativeBase):
    """Sqlalchemy model for site_categories table"""
    __tablename__ = "site_categories"

    id = Column(Integer, primary_key=True)
    display_name = Column(String,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class SiteTypes(DeclarativeBase):
    """Sqlalchemy model for site_types table"""
    __tablename__ = "site_types"

    id = Column(Integer, primary_key=True)
    display_name = Column(String,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class Feeds(DeclarativeBase):
    """Sqlalchemy model for feeds table"""
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    title = Column(String,nullable=False)
    language = Column(String,nullable=False)
    feed_url = Column(String,nullable=False)
    site_url = Column(String,nullable=False)
    description = Column(String,nullable=False)
    site_category_id = Column(Integer,nullable=False)
    site_type_id = Column(Integer,nullable=False)
    enabled = Column(Boolean,nullable=False,default=0)
    scraped_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class Articles(DeclarativeBase):
    """Sqlalchemy model for articles table"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String,nullable=False)
    summary = Column(String,nullable=False)
    creator = Column(String,nullable=False)
    url = Column(String,nullable=False)
    hash = Column(String,nullable=False)
    subject = Column(String,nullable=False)
    feed_id = Column(Integer,nullable=False)
    published_at = Column(DateTime,nullable=False)
    scraped_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class ArticleContents(DeclarativeBase):
    """Sqlalchemy model for article_contents table"""
    __tablename__ = "article_contents"

    id = Column(Integer, primary_key=True)
    content = Column(String,nullable=False)
    extracted_content = Column(String,nullable=False)
    primary_image_url = Column(String,nullable=False)
    article_hash = Column(String,nullable=False)
    content_hash = Column(String,nullable=False)
    similar_article_calculated = Column(Boolean,nullable=False,default=0)
    tweeted = Column(Boolean,nullable=False,default=0)
    token_extracted = Column(Boolean,nullable=False,default=0)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class Tokens(DeclarativeBase):
    """Sqlalchemy model for tokens table"""
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    base_form = Column(String,nullable=False)
    part_of_speech1 = Column(String,nullable=False)
    part_of_speech2 = Column(String,nullable=False)
    part_of_speech3 = Column(String,nullable=False)
    part_of_speech4 = Column(String,nullable=False)
    occurrence_count = Column(Integer,nullable=False,default=0)
    is_noise = Column(Boolean,nullable=False,default=0)
    hash = Column(String,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class TokenTypes(DeclarativeBase):
    """Sqlalchemy model for token_types table"""
    __tablename__ = "token_types"

    id = Column(Integer, primary_key=True)
    display_name = Column(String,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class TokenRelationshipTypes(DeclarativeBase):
    """Sqlalchemy model for token_relationship_types table"""
    __tablename__ = "token_relationship_types"

    id = Column(Integer, primary_key=True)
    display_name = Column(String,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())

class SimilarArticles(DeclarativeBase):
    """Sqlalchemy model for similar_articles table"""
    __tablename__ = "similar_articles"

    id = Column(Integer, primary_key=True)
    article_hash = Column(String,nullable=False)
    similar_article_hash = Column(String,nullable=False)
    score = Column(Float,nullable=False)
    created_at = Column(DateTime,nullable=False,default=datetime.now())
    updated_at = Column(DateTime,nullable=False,default=datetime.now())
