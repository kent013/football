# -*- coding: utf-8 -*-
import re
from pprint import pprint

class TextUtil(object):
    re_katakana = None

    @classmethod
    def is_katakana_name(cls, text):
        if not cls.re_katakana:
            cls.re_katakana = re.compile(r'[\u30A1-\u30FE]+')
        return cls.re_katakana.fullmatch(text)