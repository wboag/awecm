
import os, sys
from os.path import dirname
from collections import defaultdict
import glob
import datetime
import re
import random



homedir = dirname(dirname(dirname(dirname(os.path.abspath(__file__)))))
datadir = os.path.join(homedir, 'data', 'concept_extraction')


def main():

    try:
        N = int(sys.argv[1])
    except Exception, e:
        print '\n\tusage: python %s <N>\n' % sys.argv[0]
        exit(1)

    train_sents, train_labels = get_data('train', N)
    train_sents, train_labels = get_data('test' , N)

    for sent,iobs in zip(train_sents, train_labels):
        print sent
        print iobs
        print


def get_data(datatype, N):
    # Get data files
    txt_map = {}
    con_map = {}
    if datatype == 'train':
        folder=os.path.join(datadir,'concept_assertion_relation_training_data')
        for hospital in os.listdir(folder):
            txt_hospdir = os.path.join(folder, hospital, 'txt')
            txt_map_ = map_files(glob.glob('%s/*' % txt_hospdir))
            txt_map.update(txt_map_)

            con_hospdir = os.path.join(folder, hospital, 'concept')
            con_map_ = map_files(glob.glob('%s/*' % con_hospdir))
            con_map.update(con_map_)
    elif datatype == 'test':
        txt_dir = os.path.join(datadir, 'test_data')
        txt_map = map_files(glob.glob('%s/*' % txt_dir))

        con_dir = os.path.join(datadir, 'reference_standard_for_test_data', 'concepts')
        con_map = map_files(glob.glob('%s/*' % con_dir))

    else:
        print '\n\tError: bad datatype "%s"\n' % datatype
        exit(1)

    # build parallel list of txt/con
    ids = list( set(txt_map.keys()) & set(con_map.keys()) )
    txt_list = []
    con_list = []
    for fid in ids:
       txt_list.append( txt_map[fid] )
       con_list.append( con_map[fid] )

    # Read files
    sents  = []
    labels = []
    for txtfile,confile in zip(txt_list,con_list):
        txt = read_txt(txtfile)
        con = read_con(txt, confile)
        sents  += txt
        labels +=  con

    sents  = sents[:N]
    labels = labels[:N]
    
    return sents, labels



def map_files(files):
    mapped = {}
    for path in files:
        name = os.path.split(path)[-1].split('.')[0]
        mapped[name] = path
    return mapped



def read_txt(txtfile):
    with open(txtfile, 'r') as f:
        lines = f.read().rstrip().split('\n')
    sents = [ tokenize(line) for line in lines ]
    return sents



def tokenize(text):
    if text.startswith(' '):
        toks = ['']
    else:
        toks = []
    return toks + text.split()



i2b2_regex = re.compile('c="(.*?)" (\d+):(\d+) (\d+):(\d+)\|\|t="(\w+)"')
def read_con(sents, confile):
    # Start off with a 'O' label for every word (& fix the wrong ones later)
    tags = [ ['O' for word in sent] for sent in sents ]

    # edit the tags in-place from 'O' to real annotations (IOB format)
    with open(confile, 'r') as f:
        annotations = f.readlines()

    # eliminates the couple of duplicates in the provided i2b2 data
    for line in set(annotations):
        ann = re.search(i2b2_regex, line).groups()
        phrase = ' '.join(ann[0].split())
        lineno       = int(ann[1])
        start_ind    = int(ann[2])
        lineno_      = int(ann[3])
        end_ind      = int(ann[4])
        concept_type = ann[5]

        # ensure this went as expected
        assert lineno == lineno_
        source = ' '.join(sents[lineno-1][start_ind:end_ind+1]).lower()
        assert phrase == source, (phrase, source, sents[lineno-1])

        assert tags[lineno-1][start_ind] == 'O', (phrase, sents[lineno-1])
        tags[lineno-1][start_ind] = 'B-%s' % concept_type
        for i in range(end_ind-start_ind):
            assert tags[lineno-1][start_ind+1+i] == 'O', (phrase, sents[lineno-1])
            tags[lineno-1][start_ind+1+i] = 'I-%s' % concept_type

    return tags



if __name__ == '__main__':
    main()
