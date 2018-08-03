from janome.tokenfilter import *
import re
from pprint import pprint

class FootballCompoundNounFilter(TokenFilter):
    def apply(self, tokens):
        _ret = None
        re_katakana = re.compile(r'[\u30A1-\u30F4]+')
        for token in tokens:
            parts = token.part_of_speech.split(',')
            if _ret:
                ret_parts = _ret.part_of_speech.split(',')
                if parts[0] == u'名詞' and not parts[1] == 'u固有名詞' and ret_parts[0] == u'名詞' and not ret_parts[1] == u'接尾':
                    _ret.surface += token.surface
                    _ret.part_of_speech = u'名詞,複合,*,*'
                    _ret.base_form += token.base_form
                    _ret.reading += token.reading
                    _ret.phonetic += token.phonetic
                else:
                    ret = _ret
                    if parts[0] == u'名詞' and parts[1] == u'固有名詞':
                        yield token
                    else:
                        _ret = token
                    yield ret
            else:
                _ret = token
        if _ret:
            yield _ret

class FootballNounFilter(TokenFilter):
    def apply(self, tokens):
        for token in tokens:
            parts = token.part_of_speech.split(',')
            if re.match('[0-9]+', token.surface):
                continue
            if parts[0] == u'名詞' and parts[1] == u'非自立':
                continue
            if parts[0] == u'名詞' and parts[1] == u'接尾':
                continue
            if re.search('[0-9一-十百千万]+([年月日時分秒位]|ゴール)$', token.surface):
                continue
            if re.search('[0-9一-十百千万]+$', token.surface):
                continue
            if re.search('[wー]{4,}$', token.surface):
                continue
            if token.surface in [u'次ページ']:
                continue
            yield token
