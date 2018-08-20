# -*- coding: utf-8 -*-
from janome.tokenfilter import TokenFilter
import re
from pprint import pprint
from text_utils import TextUtil

class FootballCompoundNounFilter(TokenFilter):
    def apply(self, tokens):
        _ret = None
        ret_parts = []
        for token in tokens:
            parts = token.part_of_speech.split(u',')
            if _ret:
                if ret_parts[0] == u'名詞' and not ret_parts[1] == u'固有名詞' and parts[0] == u'名詞' and parts[1] not in [u'接尾', u'副詞可能'] and not TextUtil.is_katakana_name(token.base_form):
                    _ret.surface += token.surface
                    _ret.part_of_speech = u'名詞,複合,*,*'
                    _ret.base_form += token.base_form
                    _ret.reading += token.reading
                    _ret.phonetic += token.phonetic
                else:
                    ret = _ret
                    if TextUtil.is_katakana_name(token.base_form):
                        yield token
                    elif parts[0] == u'名詞' and parts[1] == u'固有名詞':
                        yield token
                    else:
                        _ret = token
                        ret_parts = parts
                    yield ret
            else:
                _ret = token
                ret_parts = parts
        if _ret:
            yield _ret

class FootballNounFilter(TokenFilter):
    def apply(self, tokens):
        for token in tokens:
            parts = token.part_of_speech.split(u',')
            if re.match(u'^[0-9]+', token.surface):
                continue
            if parts[0] == u'名詞' and parts[1] == u'非自立':
                continue
            if parts[0] == u'名詞' and parts[1] == u'接尾':
                continue
            if re.search(u'[0-9一二三四五六七八九十壱弐参拾百千万萬億兆〇]+([年月日時分秒位]|ゴール)$', token.surface):
                continue
            if re.search(u'[0-9一二三四五六七八九十壱弐参拾百千万萬億兆〇]+$', token.surface):
                continue
            if re.search(u'[wー]{4,}$', token.surface):
                continue
            if token.surface in [u'次ページ']:
                continue
            yield token

class FootballAliasFilter(TokenFilter):
    def __init__(self, aliases):
        self.aliases = aliases
    
    def apply(self, tokens):
        for token in tokens:
            if token.base_form in self.aliases:
                token.base_form = self.aliases[token.base_form]
            yield token
