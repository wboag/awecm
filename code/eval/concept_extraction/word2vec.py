
import os, sys
import re
import math
import cPickle as pickle
import shutil
import io
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
import pandas as pd
import datetime


#from tools import compute_stats_binary, compute_stats_multiclass
from concept_data import get_data
from tools import results, error_analysis



def main():

    try:
        filename = sys.argv[1]
        N = int(sys.argv[2])
    except Exception, e:
        print '\n\tusage: python %s <w2v.vec> <N>\n' % sys.argv[0]
        exit(1)

    #W = load_vectors(filename, dev=True)
    W = load_vectors(filename, dev=False)

    train_sents, train_iobs = get_data('train', N)
    test_sents ,  test_iobs = get_data('test' , N)

    train_X, train_labels = extract_features(train_sents, train_iobs, W)
    test_X ,  test_labels = extract_features( test_sents,  test_iobs, W)

    print train_X.shape

    # extract labels into list
    labels = ['O','B-problem','I-problem','B-test','I-test','B-treatment','I-treatment']
    labels_map = {y:i for i,y in enumerate(labels)}
    train_Y = np.array([labels_map[y] for y in train_labels])
    test_Y  = np.array([labels_map[y] for y in  test_labels])
    assert sorted(set(train_Y)) == range(max(train_Y)+1), 'need one of each example'

    # learn SVM
    clf = LinearSVC(C=1e-1)
    clf.fit(train_X, train_Y)
    print clf
    model = (labels_map, None, clf)

    with io.StringIO() as out_f:
        out_f.write(unicode('%s\n\n' % clf))

        # eval on dev data
        results(model,train_sents,train_X,train_Y,'TRAIN',out_f,official=False)
        results(model,test_sents,  test_X, test_Y,'TEST' ,out_f,official=True)

        output = out_f.getvalue()
    print output

    # error analysis
    #error_analysis(model, test_sents, test_X, test_Y, 'TEST')

    # serialize trained model
    vec_name = os.path.split(filename)[-1].split('.')[0]
    modelname = '../../../models/%s-%s-%s.model' % ('w2v',vec_name,N)
    M = {'labels_map':labels_map, 'clf':clf, 'output':output}
    with open(modelname, 'wb') as f:
        pickle.dump(M, f)



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


#_val = 12

def extract_features(sents, iobs, W, N=1):
    padded_s = ['start_pad_%d' % i for i in range(N)]
    padded_e = [  'end_pad_%d' % i for i in range(N)]

    dim = W.values()[0].shape[0]
    '''
    dim = 2
    def next_vec():
        global _val
        _val += 1
        return np.zeros(dim) + _val
    W = defaultdict(next_vec)
    '''

    print 'WARNING: need to normalize the tokens'

    X = []
    Y = []
    for lineno in range(len(sents)):
        sent = padded_s + sents[lineno] + padded_e
        tags = iobs[lineno]
        for i in range(len(tags)):
            features = np.zeros((2*N+1)*dim)

            # Get previous words
            for j in range(N):
                w = sent[N+i-1-j].lower()
                '''
                print 's:', w
                features[dim*j:dim*(j+1)] = W[w]
                '''
                if w in W:
                    features[dim*j:dim*(j+1)] = W[w]
                else:
                    #print 'BAD: [[%s]]' % w
                    pass


            # Get current word
            w = sent[N+i].lower()
            '''
            print 'w:', w
            features[dim*N:dim*(N+1)] = W[w]
            '''
            if w in W:
                features[dim*N:dim*(N+1)] = W[w]
            else:
                #print 'BAD: [[%s]]' % w
                pass

            # Get next words
            for j in range(N):
                w = sent[N+i+1+j].lower()
                '''
                features[dim*(j+N+1):dim*(N+j+2)] = W[w]
                '''
                if w in W:
                    features[dim*(j+N+1):dim*(N+j+2)] = W[w]
                else:
                    #print 'BAD: [[%s]]' % w
                    pass

            # Add datapoint and label
            X.append(features)
            Y.append(tags[i])

    return np.array(X), Y



if __name__ == '__main__':
    main()
