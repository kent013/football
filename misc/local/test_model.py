# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from gensim.models.doc2vec import Doc2Vec

m = Doc2Vec.load(script_dir + '/../../var/models/doc2vec.model')
results = m.most_similar(positive=sys.argv[1], topn=20)
for result in results:
    print(result[0], '\t', result[1])