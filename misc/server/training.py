# -*- coding: utf-8 -*-
import sys
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir + "/../../lib/python/")
sys.path.append(script_dir + "/../../")

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

import pickle

trainings = []
with open(script_dir + '/../../var/models/tokenized.pickle', mode='rb') as f:
    trainings = pickle.load(f)

print('Start training')
m = Doc2Vec(documents=trainings.values(), dm=1, vector_size=500, window=5, min_count=10, alpha=0.01, epochs=55, workers=2)
m.save(script_dir + "/../../var/models/doc2vec.model")
print('  Done')
