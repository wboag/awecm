import sys
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
model = KeyedVectors.load_word2vec_format(sys.argv[1], binary=True)
model.wv.save_word2vec_format(sys.argv[2])
