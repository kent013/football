# -*- coding: utf-8 -*-

from neo4j.v1 import GraphDatabase
from football.settings import NEO4J_URL

import difflib
import time


def get_neo4j_connection():
    return GraphDatabase.driver(NEO4J_URL)

def get_word_aliases():
    neo4j = get_neo4j_connection()
    neo4j_session = neo4j.session()
    results = neo4j_session.run("MATCH (a)-[r:AliasOf]->(b) RETURN a, r, b")

    aliases = {}
    for record in results:
        relation = record.get("r")
        alias = relation.start_node.get('name')
        original = relation.end_node.get('name')
        aliases[alias] = original
    neo4j.close()
    return aliases

def get_all_tokens():
    neo4j = get_neo4j_connection()
    neo4j_session = neo4j.session()
    results = neo4j_session.run("MATCH (n) RETURN n")

    tokens = []
    for record in results:
        node = record.get("n")
        tokens.append({'name': node.get('name'), 'hash': node.get('hash')})
    neo4j.close()
    return tokens

def normalize_words(text, aliases):
    original_mark = "@!@---@##@----@!@"
    for original in aliases.keys():
        text = text.replace(original, original_mark)
        for alias in aliases[original]:
            text = text.replace(alias, original_mark)
        text = text.replace(original_mark, original)
    return text

def print_diff(text1, text2):
    g = difflib.unified_diff (text1.splitlines(),
                    text2.splitlines(),
                    'name-version.orig/test.txt',
                    'name-version/test.txt',
                    time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1212121212)),
                    time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1313131313)),
                    3,
                    '')
    for l in g:
        print (l)

def print_tokens(tokens):
    for token in tokens:
        print(token.base_form)