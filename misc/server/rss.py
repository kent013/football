# -*- coding: utf-8 -*-
import feedparser
import sys
from pprint import pprint
import urllib.parse
import requests
import feedparser
from bs4 import BeautifulSoup as bs4

args = sys.argv
url = args[1]
result = feedparser.parse(url)

print("%s\t%s\t%s\t%s" % (result['feed']['title'], result['feed']['link'],result['href'], result['feed']['subtitle']))
