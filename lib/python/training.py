# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../")

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

import pickle

trainings = []
with open('models/tokenized.pickle', mode='rb') as f:
    trainings = pickle.load(f)

print('Start training')
m = Doc2Vec(documents=trainings, dm=1, vector_size=500, window=10, min_count=3, sample=10, alpha=0.1, epochs=55)
m.save("models/doc2vec.model")
