# -*- coding: utf-8 -*-
import feedparser
import sys
from pprint import pprint
import urllib.parse
import requests
import feedparser
from bs4 import BeautifulSoup as bs4

def findfeed(site):
    raw = requests.get(site).text
    result = []
    possible_feeds = []
    html = bs4(raw, "lxml")
    feed_urls = html.findAll("link", rel="alternate")
    for f in feed_urls:
        t = f.get("type",None)
        if t:
            if "rss" in t or "xml" in t:
                href = f.get("href",None)
                if href:
                    possible_feeds.append(href)
    parsed_url = urllib.parse.urlparse(site)
    base = parsed_url.scheme+"://"+parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href",None)
        if href:
            if "xml" in href or "rss" in href or "feed" in href:
                possible_feeds.append(base+href)
    for url in list(set(possible_feeds)):
        f = feedparser.parse(url)
        if len(f.entries) > 0:
            if url not in result:
                result.append(url)
    return(result)

args = sys.argv
url = args[1]
feeds = findfeed(url)
result = feedparser.parse(feeds[0])

print("%s\t%s\t%s\t%s" % (result['feed']['title'], result['feed']['link'],result['href'], result['feed']['subtitle']))
