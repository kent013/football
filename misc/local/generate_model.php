<?php
require_once(__DIR__ . "/../../lib/php/Inflect.php");

function camelize($str) {
    return ucfirst(strtr(ucwords(strtr($str, ['_' => ' '])), [' ' => '']));
}

$sql = file_get_contents(__DIR__ . "/../../sql/setup.sql");

preg_match_all('/CREATE TABLE (.+?) \(.+?\);/ms', $sql, $tables);
$items = [];
$models = [];
foreach($tables[0] as $index => $table){
    $name = $tables[1][$index];
    $camel_name = camelize($name);
    $single_name = Inflect::singularize($camel_name);
    $plural_name = $camel_name;

    if(preg_match('/crawl/i', $name)){
        continue;
    }

    preg_match_all('/^\s*`([^`]+)` ([^ ]+)( (NOT NULL|NULL))?( DEFAULT ([^ ,]+))?/ms', $table, $defs);

    $model = <<<EOS
class $plural_name(DeclarativeBase):
    """Sqlalchemy model for $name table"""
    __tablename__ = "$name"

    id = Column(Integer, primary_key=True)

EOS;
    $item = <<<EOS
class Football{$single_name}Item(scrapy.Item):

EOS;
    foreach($defs[0] as $k => $def){
        $property = $defs[1][$k];
        $type = $defs[2][$k];
        $nullable = empty($defs[3][$k]);
        $default = !empty($defs[5][$k]);
        $attributes = [];
        if($property != "id"){
            $column_type = "";
            if($type == "TEXT" || preg_match('/VARCHAR/', $type) || $type == "MEDIUMTEXT"){
                $column_type = "String";
            }else if($type == "INT"){
                $column_type = "Integer";
            }else if($type == "TIMESTAMP"){
                $column_type = "DateTime";
            }else if($type == "FLOAT"){
                $column_type = "Float";
            }else if($type == "BOOLEAN"){
                $column_type = "Boolean";
            }
            $attributes[] = $column_type;

            $nullable_bool = $nullable ? "True" : "False";
            $attributes[] = "nullable=$nullable_bool";

            if($default){
                $defval = $defs[6][$k];
                if($defval == "current_timestamp"){
                    $attributes[] = "default=datetime.now()";
                }else{
                    $attributes[] = "default=" . $defval;
                }
            }

            $model .= "    $property = Column(" . implode(",", $attributes) . ")\n";
        }
        $item .= "    $property = scrapy.Field()\n";
    }
    $models[] = $model;
    $items[] = $item;
}

$out = <<<EOS
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


EOS;

$out .= implode("\n", $models);
file_put_contents(dirname(__FILE__) . "/../../football/models.py", $out);

$out = <<<EOS
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

EOS;
$out .= implode("\n", $items);
file_put_contents(dirname(__FILE__) . "/../../football/items.py", $out);
