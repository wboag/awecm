
import os, sys
import psycopg2
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import math
import datetime
import re
import random
import numpy as np


if '--cui' or '--cui_rel' in sys.argv:
    from umls.code.interface_umls import cui_lookup
    from umls.code.interface_umls import cui_relation_lookup


def extract_context_position(docs, contexts_filename, N=8):

    '''
    goal: do word2vec's preprocessing
        [x] dynamic context window
        [x] rare word removal
        [x] subsampling
    '''

    n_docs = len(docs)
    point = int(n_docs / 20.)

    # unigram counts (for filtering)
    counts = defaultdict(int)
    print 'unigram counts'
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        for w in toks:
            counts[w] += 1
    print
    Z = sum(counts.values())
    freq = { w:float(count)/Z for w,count in counts.items() }

    # remove rare words
    new_docs = []
    print 'removing rare words'
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        new_toks = [ w for w in toks if counts[w] >= 5 ]
        new_docs.append(new_toks)
    docs = new_docs
    print

    # subsample to remove frequent words
    subt = 1e-4
    new_docs = []
    print 'subsampling'
    def remove_prob(w):
        f = freq[w]
        return (f-subt)/f - math.sqrt(subt/f)
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        new_toks = [ w for w in toks if random.random() <= 1-remove_prob(w)]
        new_docs.append(new_toks)
    docs = new_docs
    print

    # build context pairs
    W = defaultdict(int)
    C = defaultdict(int)
    #docs = docs[:1]
    print 'building (w,c) pairs'
    # save context dict
    with open(contexts_filename, 'w') as f:
        for i,toks in enumerate(docs):
            if i%point == 0:
                print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)

            #toks = toks[:10]
            doc_len = len(toks)
            for i,w in enumerate(toks):
                W[w] += 1

                #print i, w
                n = random.randint(1,N)
                i_minus_n = max(i-n  , 0)
                i_plus_n  = min(i+n+1, doc_len)
                context = toks[i_minus_n:i] + toks[i+1:i_plus_n]
                for c in context:
                    # Unusre if I'm supposed to repeatedly count this for each center word
                    C[c] += 1

                    print >>f, '%s %s' % (w,c)
                    #print '\t%s %s' % (w,c)
        print

    return W, C



def extract_context_cuis(docs, contexts_filename, N=8,rel=False):

    '''
    goal: do word2vec's preprocessing
        [x] dynamic context window
        [x] rare word removal
        [x] subsampling
    '''

    n_docs = len(docs)
    point = int(n_docs / 20.)

    # unigram counts (for filtering)
    counts = defaultdict(int)
    print 'unigram counts'
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        for w in toks:
            counts[w] += 1
    print
    Z = sum(counts.values())
    freq = { w:float(count)/Z for w,count in counts.items() }

    # remove rare words
    new_docs = []
    print 'removing rare words'
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        new_toks = [ w for w in toks if counts[w] >= 5 ]
        new_docs.append(new_toks)
    docs = new_docs
    print

    # subsample to remove frequent words
    subt = 1e-4
    new_docs = []
    print 'subsampling'
    def remove_prob(w):
        f = freq[w]
        return (f-subt)/f - math.sqrt(subt/f)
    for i,toks in enumerate(docs):
        if i%point == 0:
            print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)
        new_toks = [ w for w in toks if random.random() <= 1-remove_prob(w)]
        new_docs.append(new_toks)
    docs = new_docs
    print

    # build context pairs
    W = defaultdict(int)
    C = defaultdict(int)
    #docs = docs[:1]
    print 'building (w,c) pairs'
    # save context dict
    with open(contexts_filename, 'w') as f:
        for i,toks in enumerate(docs):
            if i%point == 0:
                print '\t%.2f%% done (%d/%d)' % (float(i)/n_docs,i,n_docs)

            #toks = toks[:10]
            doc_len = len(toks)
            for i,w in enumerate(toks):
                W[w] += 1

                # position context
                n = random.randint(1,N)
                i_minus_n = max(i-n  , 0)
                i_plus_n  = min(i+n+1, doc_len)
                word_context = toks[i_minus_n:i] + toks[i+1:i_plus_n]

                # CUI context
                cui_context = [ c[0] for c in cui_lookup(w) ]
                cui_context = list(set(cui_context))
                context = word_context + cui_context

                if rel:

                    # CUI relationships context
                    cui_rel_context = []
                    for cui in cui_context:
                        cui_rel_context+= [c_r[0] for c_r in cui_relation_lookup(cui)]
                    cui_rel_context = list(set(cui_rel_context))
                    print cui_rel_context
                    context +=cui_rel_context

                for c in context:
                    # Unusre if I'm supposed to repeatedly count this for each center word
                    C[c] += 1

                    print >>f, '%s %s' % (w,c)
                    #print '\t%s %s' % (w,c)
        print

    return W, C



def main():
    try:
        corpus = sys.argv[1]
        window_size = int(sys.argv[2])
        contexts_filename = sys.argv[3]
        w_vocab = sys.argv[4]
        c_vocab = sys.argv[5]
        context_type = sys.argv[6]
        assert context_type in ['--word','--cui','--cui_rel']
    except Exception, e:
        print '\n\tusage: python %s <corpus> <window_size> <contexts_filename> <w_vocab> <c_vocab> <--word|--cui| --cui_rel>\n'%sys.argv[0]
        exit(1)

    # read tokens
    with open(corpus,'r') as f:
        text = f.read()
    doc_toks = [line.split() for line in text.split('\n')]

    # build contexts
    if context_type == '--word':
        W, C = extract_context_position(doc_toks, contexts_filename, N=window_size)
    elif context_type == '--cui':
        W, C = extract_context_cuis(doc_toks, contexts_filename, N=window_size)
    elif context_type == '--cui_rel':
        W, C = extract_context_cuis(doc_toks,contexts_filename, N=window_size, rel=True)
    else:
        print 'unknown context type "%s"' % context_type
        exit(1)

    # save vocabs
    with open(w_vocab, 'w') as f:
        for (w,count) in sorted(W.items(), key=lambda t:t[1]):
            print >>f, '%s %d' % (w,count)
    with open(c_vocab, 'w') as f:
        for (c,count) in sorted(C.items(), key=lambda t:t[1]):
            print >>f, '%s %d' % (c,count)



if __name__ == '__main__':
    main()
