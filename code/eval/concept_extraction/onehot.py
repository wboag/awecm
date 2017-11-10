
import sys
import cPickle as pickle
import io
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC


#from tools import compute_stats_binary, compute_stats_multiclass
from concept_data import get_data
from tools import results, error_analysis



def main():

    try:
        N = int(sys.argv[1])
    except Exception, e:
        print '\n\tusage: python %s <N>\n' % sys.argv[0]
        exit(1)

    train_sents, train_iobs = get_data('train', N)
    test_sents ,  test_iobs = get_data('test' , N)

    train_instances, train_labels = extract_features(train_sents, train_iobs)
    test_instances ,  test_labels = extract_features( test_sents,  test_iobs)

    # vecotrize notes
    train_X, vect  = vectorize_X(train_instances, vect=None)
    test_X , vect_ = vectorize_X( test_instances, vect=vect)
    assert vect == vect_

    print train_X.shape

    # extract labels into list
    labels = ['O','B-problem','I-problem','B-test','I-test','B-treatment','I-treatment']
    labels_map = {y:i for i,y in enumerate(labels)}
    train_Y = np.array([labels_map[y] for y in train_labels])
    test_Y  = np.array([labels_map[y] for y in  test_labels])
    assert sorted(set(train_Y))==range(max(train_Y)+1),'need one of each example'

    # learn SVM
    clf = LinearSVC(C=1e0)
    clf.fit(train_X, train_Y)
    model = (labels_map, vect, clf)

    with io.StringIO() as out_f:
        out_f.write(unicode('%s\n\n' % clf))

        # analysis
        analyze(model, out_f)

        # eval on dev data
        results(model,train_sents,train_X,train_Y,'TRAIN',out_f,official=False)
        results(model,test_sents, test_X, test_Y, 'TEST' ,out_f,official=True)

        output = out_f.getvalue()
    print output

    # error analysis
    #error_analysis(model, test_sents, test_X, test_Y, 'TEST')

    # serialize trained model
    modelname = '../../../models/%s_%s.model' % ('onehot',N)
    M = {'labels_map':labels_map, 'vect':vect, 'clf':clf, 'output':output}
    with open(modelname, 'wb') as f:
        pickle.dump(M, f)



def extract_features(sents, iobs, N=1):
    padded_s = ['start_pad_%d' % i for i in range(N)]
    padded_e = [  'end_pad_%d' % i for i in range(N)]

    X = []
    Y = []
    for lineno in range(len(sents)):
        sent = padded_s + sents[lineno] + padded_e
        tags = iobs[lineno]
        for i in range(len(tags)):
            features = {}

            # Get previous words
            for j in range(N):
                w = sent[N+i-1-j].lower()
                featname = ('prev_%d'%(j+1), w)
                features[featname] = 1

            # Get current word
            w = sent[N+i].lower()
            featname = ('word', w)
            features[featname] = 1

            # Get next words
            for j in range(N):
                w = sent[N+i+1+j].lower()
                featname = ('next_%d'%(j+1), w)
                features[featname] = 1

            # Add datapoint and label
            X.append(features)
            Y.append(tags[i])

    return X, Y



def vectorize_X(features, vect=None):
    # learn vectorizer on training data
    if vect is None:
        vect = DictVectorizer()
        vect.fit(features)

    X = vect.transform(features)

    return X, vect



def analyze(model, out_f):

    labels_map, vect, clf = model
    ind2feat =  { i:f for f,i in vect.vocabulary_.items() }
    labels = [label for label,i in sorted(labels_map.items(), key=lambda t:t[1])]

    # most informative features
    #"""
    out_f = sys.stdout
    out_f.write(unicode(clf.coef_.shape))
    out_f.write(unicode('\n\n'))
    num_feats = 15
    informative_feats = np.argsort(clf.coef_)

    for i,label in enumerate(labels):

        neg_features = informative_feats[i,:num_feats ]
        pos_features = informative_feats[i,-num_feats:]

        #'''
        # display what each feature is
        out_f.write(unicode('POS %s\n' % label))
        for feat in reversed(pos_features):
            val = clf.coef_[i,feat]
            word = ind2feat[feat]
            if val > 1e-4:
                out_f.write(unicode('\t%-25s: %7.4f\n' % (word,val)))
            else:
                break
        out_f.write(unicode('NEG %s\n' % label))
        for feat in reversed(neg_features):
            val = clf.coef_[i,feat]
            word = ind2feat[feat]
            if -val > 1e-4:
                out_f.write(unicode('\t%-25s: %7.4f\n' % (word,val)))
            else:
                break
        out_f.write(unicode('\n\n'))
        #'''
        #exit()
        #"""


if __name__ == '__main__':
    main()
