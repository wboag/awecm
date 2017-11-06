
import os, sys
from collections import defaultdict
import numpy as np
from scipy.stats.stats import pearsonr, spearmanr


from read_data import get_srs



def main():

    try:
        filename = sys.argv[1]
    except Exception, e:
        print '\n\tusage: python %s <w2v.vec>\n' % sys.argv[0]
        exit(1)

    #W = load_vectors(filename, dev=True)
    W = load_vectors(filename, dev=False)
    dim = W.values()[0].shape[0]

    print 'W:', len(W)

    srs = get_srs()
    for task,scores in srs.items():

        xs,ys = scores
        preds = []
        for x in xs:
            phrase1,phrase2 = x
            v1 = embed(phrase1, dim, W)
            v2 = embed(phrase2, dim, W)
            cos = cosine(v1, v2)
            preds.append(cos)

        # compute correlation
        #c,p = pearsonr(preds, ys)
        c,p = spearmanr(preds, ys)
        print '%-15s: pearson=%.3f p=%.3f' % (task,c,p)




def cosine(u, v):
    return np.dot(u, v)



def norm(v):
    return np.dot(v,v)**0.5



def embed(phrase, dim, W):
    words = phrase.split()
    vectors = [ W[w] for w in words if (w in W) ]
    v = sum(vectors, np.zeros(dim))
    '''
    if len(vectors) == 0:
        print 'BAD:', phrase
        exit()
    '''
    return v / (norm(v) + 1e-9)


def load_vectors(filename, dev=False):
    W = {}
    with open(filename, 'r') as f:
        for i,line in enumerate(f.readlines()):
            if i==0: continue
            if dev and i >= 50: break
            '''
            if sys.argv[1]=='small' and i>=50:
                break
            '''
            toks = line.strip().split()
            w = toks[0]
            vec = np.array(map(float,toks[1:]))
            W[w] = vec
    return W



if __name__ == '__main__':
    main()
