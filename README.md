# AWE-CM
Augmented Word Embeddings with a Clinical Metathesaurus


# Meetings
https://docs.google.com/document/d/12jRvXR_I-AuEdjUovERnVne71Ei1dbhgo-UTiImeZnM/edit


# Writeup
https://www.overleaf.com/11188799yhjcmxphgpjm#/42196701/



# Sample Data

[Public discharge summaries](https://sites.google.com/site/medicaltranscriptionsamples/discharge-summary-medical-transcription-sample-report) were used to create a small amount of text used to demonstrate how to build and evaluate the vectors.


# Usage

[Pretrained word embeddings (baseline)](https://drive.google.com/file/d/0B7XkCwpI5KDY)

NOTE: This code requires Python 2.


Build **word2vec** and **word2vecf** tools

    cd resources/word2vec ; make ; cd ../../

    cd resources/word2vecf ; make ; cd ../../


Download the [UMLS tables](https://www.nlm.nih.gov/research/umls/) and put them in the right folder. The code automatically checks this directory.

    wboag@gray:/scratch/wboag/awecm$ ls code/word2vecf/umls/umls_tables/
    .gitignore   LRABR        MRCONSO.RRF  MRREL.RRF    MRSTY.RRF



Build corpus (starting from the sample data above)

    python code/corpus/build_fake_corpus.py > data/txt/fake_discharge.txt


Build official word2vec vectors

    resources/word2vec/word2vec -train data/txt/fake_discharge.txt -output data/vectors/w2v_fake_discharge.vec -size 300 -window 8 -sample 1e-4 -hs 0 -negative 8 -threads 12 -iter 5 -min-count 5 -alpha 0.025 -binary 0 -cbow 0


Building word vectors from word2vecf (in theory, equal to official word2vec)

    python code/word2vecf/generate_context_windows.py data/txt/fake_discharge.txt 8 data/contexts/fake_discharge_word.contexts data/vocabs/fake_discharge_word.w data/vocabs/fake_discharge_word.c --word

    resources/word2vecf/word2vecf -train data/contexts/fake_discharge_word.contexts -output data/vectors/w2vf_fake_discharge_word.vec -size 300 -sample 0 -hs 0 -negative 8 -threads 12 -iters 5 -alpha 0.025 -binary 0 -wvocab data/vocabs/fake_discharge_word.w -cvocab data/vocabs/fake_discharge_word.c


Building CUI-enhanced AWE-CM vectors from word2vecf (**requires UMLS tables**) (only CUI)

    python code/word2vecf/generate_context_windows.py data/txt/fake_discharge.txt 8 data/contexts/fake_discharge_cui.contexts data/vocabs/fake_discharge_cui.w data/vocabs/fake_discharge_cui.c --cui

    resources/word2vecf/word2vecf -train data/contexts/fake_discharge_cui.contexts -output data/vectors/w2vf_fake_discharge_cui.vec -size 300 -sample 0 -hs 0 -negative 8 -threads 12 -iters 5 -alpha 0.025 -binary 0 -wvocab data/vocabs/fake_discharge_cui.w -cvocab data/vocabs/fake_discharge_cui.c

Building CUI_REL-enhanced AWE-CM vectors from word2vecf (**requires UMLS tables**) (CUI + Related CUI)

    python code/word2vecf/generate_context_windows.py data/txt/fake_discharge.txt 8 data/contexts/fake_discharge_cui_rel.contexts data/vocabs/fake_discharge_cui_rel.w data/vocabs/fake_discharge_cui_rel.c --cui_rel

    resources/word2vecf/word2vecf -train data/contexts/fake_discharge_cui_rel.contexts -output data/vectors/w2vf_fake_discharge_cui_rel.vec -size 300 -sample 0 -hs 0 -negative 8 -threads 12 -iters 5 -alpha 0.025 -binary 0 -wvocab data/vocabs/fake_discharge_cui_rel.w -cvocab data/vocabs/fake_discharge_cui_rel.c


Evaluating word vectors with SRS (correlation with experts)

     python code/eval/srs/srs_eval.py data/vectors/w2vf_fake_discharge_word.vec


