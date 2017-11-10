
import os, sys
import io
import shutil
import commands
import tempfile
import numpy as np


def results(model, sents, X, Y, description, out_f, official=False):
    labels_map, vect, clf = model

    # for AUC
    P = clf.decision_function(X)
    train_pred = P.argmax(axis=1)

    # what is the predicted vocab without the dummy label?
    V = labels_map.keys()

    out_f.write('%s' % (unicode(description)))
    out_f.write(unicode('\n'))
    compute_stats_multiclass(train_pred, P, Y, labels_map, out_f)
    out_f.write(unicode('\n\n'))

    # official eval script?
    if official:
        pred_iobs = make_iobs(train_pred, sents, labels_map)
        pred_concepts = make_concept_annotations(sents, pred_iobs)

        ref_iobs  = make_iobs(Y         , sents, labels_map)
        ref_concepts = make_concept_annotations(sents, ref_iobs)

        official_eval(sents, pred_concepts, ref_concepts, out_f)



def make_iobs(Y, sents, labels_map):
    ind2label = {v:k for k,v in labels_map.items()}
    iobs = []
    for sent in sents:
        n = len(sent)
        line = Y[:n]
        Y = Y[n:]
        tags = [ ind2label[y] for y in line ]
        iobs.append(tags)

    # make sure this is correctly formatted
    assert len(iobs) == len(sents)
    for sent,tags in zip(sents,iobs):
        assert len(sent) == len(tags)

    # Ensure all predictions conform to IOB standards
    for i in range(len(sents)):
        if len(sents[i]):
            # first token cannot be I-
            if iobs[i][0][0] == 'I':
                iobs[i][0] = 'B%s' % iobs[i][0][1:]

        # cannot have I- following an O
        for j in range(1,len(sents[i])):
            if iobs[i][j-1] == 'O' and iobs[i][j][0] == 'I':
                iobs[i][j] = 'B%s' % iobs[i][j][1:]
            if iobs[i][j][0] == 'I' and iobs[i][j][1:] != iobs[i][j-1][1:]:
                iobs[i][j] = 'I%s' % iobs[i][j-1][1:]


    return iobs



def make_concept_annotations(sents, iobs):

    # make sure this is correctly formatted
    assert len(iobs) == len(sents)
    for sent,tags in zip(sents,iobs):
        assert len(sent) == len(tags), (sent, tags)

    # Ensure all predictions conform to IOB standards
    for i in range(len(sents)):
        # first token cannot be I-
        if len(sents[i]):
            assert iobs[i][0][0] != 'I'
        # cannot have I- following an O
        for j in range(1,len(sents[i])):
            assert not (iobs[i][j-1] == 'O' and iobs[i][j][0] == 'I')
            assert not (iobs[i][j][0] == 'I' and iobs[i][j][1:] != iobs[i][j-1][1:])

    # Make i2b2 concept annotation
    concepts = []
    for i,(sent,tags) in enumerate(zip(sents,iobs)):
        #if set(tags) == set(['O']): continue
        if len(set(tags)) < 4: continue
        bs = [ ind for ind,y in enumerate(tags) if y[0]=='B']

        # one ind per concept
        for start in bs:
            # figure out how long this concept's span is
            end = start + 1
            ctype = tags[start][2:]
            while (end < len(tags)) and (tags[end][0] == 'I') and \
                  (tags[end][2:] == ctype):
                end += 1
            end -= 1

            # add this concept
            phrase = ' '.join(sent[start:end+1]).lower()
            concept = (ctype, i, start, end, phrase)
            concepts.append(concept)

    return concepts



def compute_stats_multiclass(pred, P, ref, labels_map, out_f):
    # santiy check
    assert all(map(int,P.argmax(axis=1)) == pred)

    # get rid of that final prediction dimension
    #pred = pred[1:]
    #ref  =  ref[1:]

    V = labels_map.keys()
    n = len(V)
    conf = np.zeros((n,n), dtype='int32')
    for p,r in zip(pred,ref):
        conf[p][r] += 1

    labels = [label for label,i in sorted(labels_map.items(), key=lambda t:t[1])]

    out_f.write(unicode(conf))
    out_f.write(unicode('\n'))

    precisions = []
    recalls = []
    f1s = []
    out_f.write(unicode('\t prec  rec    f1   label\n'))
    for i in range(n):
        label = labels[i]

        tp = conf[i,i]
        pred_pos = conf[i,:].sum()
        ref_pos  = conf[:,i].sum()

        precision   = tp / (pred_pos + 1e-9)
        recall      = tp / (ref_pos + 1e-9)
        f1 = (2*precision*recall) / (precision+recall+1e-9)

        out_f.write(unicode('\t%.3f %.3f %.3f %s\n' % (precision,recall,f1,label)))

        # Save info
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    avg_precision = sum(precisions) / len(precisions)
    avg_recall    = sum(recalls   ) / len(recalls   )
    avg_f1        = sum(f1s       ) / len(f1s       )
    out_f.write(unicode('\t--------------------------\n'))
    out_f.write(unicode('\t%.3f %.3f %.3f avg\n' % (avg_precision,avg_recall,avg_f1)))




def official_eval(sents, pred_concepts, ref_concepts, out_f):
    # tmp directory to store files
    tmp = tempfile.mkdtemp(prefix='/tmp/clinical_vector_')
    ref_dir  = os.path.join(tmp, 'ref' )
    pred_dir = os.path.join(tmp, 'pred')
    os.mkdir( ref_dir)
    os.mkdir(pred_dir)

    # write outout to file
    write_i2b2(os.path.join(pred_dir, 'all.con'), pred_concepts)
    write_i2b2(os.path.join( ref_dir, 'all.con'),  ref_concepts)

    # call eval
    thisdir = os.path.dirname(os.path.abspath(__file__))
    eval_jar = os.path.join(thisdir, 'i2b2va-eval.jar')

    cmd = 'java -jar %s -rcp %s/ -scp %s/ -ft con -ex all' % (eval_jar,ref_dir,pred_dir)
    status,output = commands.getstatusoutput(cmd)
    out_f.write(unicode('\n\n%s\n\n' % output))

    # clean up
    shutil.rmtree(tmp)




def write_i2b2(filename, concepts):
    with open(filename, 'w') as f:
        for ctype,lineno,start,end,phrase in concepts:
            s = 'c="%s" %d:%d %d:%d||t="%s"' % (phrase,lineno,start,lineno,end,ctype)
            print >>f, s



def error_analysis(model, sents, X, Y, description):
    labels_map, vect, clf = model

    V = {v:k for k,v in labels_map.items()}
    V[len(V)] = '**wrong**'

    # for confidence
    P = clf.decision_function(X)
    pred = clf.predict(X)

    # convert predictions to right vs wrong
    confidence = []
    for i,scores in enumerate(P.tolist()):
        prediction = pred[i]
        ind = Y[i]
        confidence.append( (scores[ind], scores, prediction, ind) )

    # order predictions by confidence
    for conf in sorted(confidence)[:5]:
        if conf[2] == conf[3]:
            success = ''
        else:
            success = '_'

        print conf



if __name__ == '__main__':
    main()
