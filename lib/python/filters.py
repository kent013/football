from janome.tokenfilter import *
import re
from pprint import pprint

class FootballCompoundNounFilter(TokenFilter):
    def apply(self, tokens):
        _ret = None
        for token in tokens:
            if _ret:
                pprint(token.part_of_speech)
                if token.part_of_speech.startswith(u'名詞') and _ret.part_of_speech.startswith(u'名詞'):
                    _ret.surface += token.surface
                    _ret.part_of_speech = u'名詞,複合,*,*'
                    _ret.base_form += token.base_form
                    _ret.reading += token.reading
                    _ret.phonetic += token.phonetic
                else:
                    ret = _ret
                    _ret = token
                    yield ret
            else:
                _ret = token
        if _ret:
            yield _ret
