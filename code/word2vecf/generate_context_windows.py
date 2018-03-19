
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


if '--cui' or '--cui_rel' or '--cui_rel_separate' or '--cui_rel_only_separate' or '--cui_rel_only' or '--cui_only' in sys.argv:
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


def get_cui_context(word):
    ''' Given a word, returns a list of CUIs it is mapped to in the UMLS knowledge graph'''
    cui_context = [c[0] for c in cui_lookup(word)]
    cui_context = list(set(cui_context))
    return cui_context

def get_relationships_cui(cui):
    ''' Given a cui, returns a list of all the cui it is related to in the UMLS knowledge graph'''
    relationships = [c_r[0] for c_r in cui_relation_lookup(cui)]
    return relationships

def get_relationships_word(word):
    ''' Given a word, returns a dictionary of cuis it's related to and their relationships'''
    cui_context = [c[0] for c in cui_lookup(w)]
    relationships = {}
    if len(cui_context)>0:
        for cui in cui_context:
            relationships[cui] = get_relationships_cui(cui)
    return relationships


def extract_context_cuis(docs, contexts_filename, N=8,rel=False, cui_only = False, separate_rel= False):

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
                context = []
                #Step 1 : Build cui context
                cui_context = get_cui_context(w)
                if len(cui_context)>0:
                    W[w] += 1
                    if rel : #Relationships in the knowledge graph are also leveraged in that case neighboring
                            ''' Relationships are to be leveraged in 2 ways. In the most intuitive way, 
                                you have (W,CUI_1) and (CUI_1, CUI_NEIGH) pairs. This is separate_rel
                                Otherwise, you have (W,CUI_1) + (W,CUI_NEIGH) pairs. This is not separate_rel
                            '''
                            if separate_rel: #Separate info from CUI and Neighbor
                                cui_rel_context = []
                                for cui in cui_context:
                                    C[cui] +=1
                                    print >>f, '%s %s' % (w,cui)
                                    cui_rel_context = [c_r[0] for c_r in cui_relation_lookup(cui)]
                                    for cui_rel in cui_rel_context:
                                        C[cui_rel] +=1
                                        print >>f, '%s %s' % (cui,cui_rel)
                            else:
                                # Word gets matched to CUI + Neighboring CUI
                                cui_rel_context = []
                                for cui in cui_context:
                                    cui_rel_context+= [c_r[0] for c_r in cui_relation_lookup(cui)]
                                cui_rel_context = list(set(cui_rel_context))
                                context +=cui_context
                                context +=cui_rel_context
                                for c in context:
                                    # Unusre if I'm supposed to repeatedly count this for each center word
                                    C[c] += 1

                                    print >>f, '%s %s' % (w,c)
                                        #print '\t%s %s' % (w,c)
                #Step 2: Build Word context if specified
                    if cui_only: #The only word,context pairs built in this case are (w,CUI) pairs
                        pass 

                    else: #Now we include neighboring word as well in the context
                        #position context
                        n = random.randint(1,N)
                        i_minus_n = max(i-n  , 0)
                        i_plus_n  = min(i+n+1, doc_len)
                        word_context = toks[i_minus_n:i] + toks[i+1:i_plus_n]
                        for con in word_context:
                            C[con] += 1
                            print >>f, '%s %s' % (w,con)
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
        assert context_type in ['--word','--cui','--cui_rel', '--cui_rel_separate','--cui_rel_only_separate','--cui_rel_only', '--cui_only']
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
    elif context_type == '--cui_rel_separate':
        W, C = extract_context_cuis(doc_toks,contexts_filename, N=window_size, rel=True, separate_rel= True)
    elif context_type == '--cui_rel_only_separate':
        W, C = extract_context_cuis(doc_toks,contexts_filename, N=window_size, rel=True, cui_only=True, separate_rel= True)
    elif context_type == '--cui_rel_only':
        W, C = extract_context_cuis(doc_toks,contexts_filename, N=window_size, rel=True, cui_only=True)
    elif context_type == '--cui_only':
        W, C = extract_context_cuis(doc_toks,contexts_filename, N=window_size, cui_only=True)
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
