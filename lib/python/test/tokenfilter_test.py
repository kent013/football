import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../src/")
sys.path.append(script_dir + "/../../../")

import unittest

from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenfilter import POSKeepFilter
from filters import FootballCompoundNounFilter, FootballNounFilter, FootballAliasFilter
from neo4j_util import get_word_aliases

class TestFilters(unittest.TestCase):
    def setUp(self):
        #aliases = get_word_aliases()
        char_filters = [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter('&[^&]+;', '')]
        tokenizer = Tokenizer(mmap=True)
        token_filters = [FootballCompoundNounFilter(), FootballNounFilter(), POSKeepFilter('名詞')]
        self.analyzer = Analyzer(char_filters, tokenizer, token_filters)

    def test_CompoundNounFilter1(self):
        # test for "本田圭佑"
        content = "日本代表･本田圭佑はＷ杯で最もスタイリッシュ"
        
        tokens = self.analyze(content)
        self.assertTrue('本田圭佑' in tokens)
    
    def test_CompoundNounFilter2(self):
        # test for "さん"
        content = "【朗報】　本田圭佑さん、2試合で1ゴール1アシスト"
        
        tokens = self.analyze(content)
        self.assertTrue('本田圭佑' in tokens)

    def test_CompoundNounFilter3(self):
        # test for "ら"
        content = '親交の深いＭＦ香川真司らの得点で勝利を挙げた日本の戦いぶりには、試合はＦＩＦＡのジャンニ・インファンティノ会長らも座るＶＩＰ席で観戦。'

        tokens = self.analyze(content)
        self.assertTrue('香川真司' in tokens)
        self.assertFalse('香川真司ら' in tokens)
        self.assertTrue('ジャンニ・インファンティノ' in tokens)
        self.assertFalse('ジャンニ・インファンティノ会長ら' in tokens)

    def test_CompoundNounFilter4(self):
        # test for "ら"
        content = 'コーフェルト監督自らが直接口説き落とした大迫'

        tokens = self.analyze(content)
        self.assertTrue('コーフェルト監督' in tokens)

    def test_CompoundNounFilter5(self):
        # test for "ら"
        content = 'ジェノアの監督ダビデ・バッラルディーニは憮然とした表情で地元紙のインタビューに応えた&ldquo;超上から目線&rdquo;'

        tokens = self.analyze(content)
        self.assertTrue('ダビデ・バッラルディーニ' in tokens)

    def test_CompoundNounFilter6(self):
        # test for "ら"
        content = '南仏エクス・オン・プロバンス生まれのミシェルと、生粋のブルターニュ人'

        tokens = self.analyze(content)
        self.assertTrue('エクス・オン・プロバンス' in tokens)

    def analyze(self, content, debug = False):
        tokens = list(self.analyzer.analyze(content))
        retval = {}
        for token in tokens:
            if debug:
                print(token)
            retval[token.base_form] = token
        return retval

if __name__ == "__main__":
    unittest.main()
