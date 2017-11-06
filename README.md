# AWE-CM
Augmented Word Embeddings with a Clinical Metathesaurus


# Meetings
https://docs.google.com/document/d/12jRvXR_I-AuEdjUovERnVne71Ei1dbhgo-UTiImeZnM/edit


# Writeup
https://www.overleaf.com/11188799yhjcmxphgpjm#/42196701/


# Usage


[Pretrained word embeddings (baseline)](https://drive.google.com/file/d/0B7XkCwpI5KDY)


Build official word2vec vectors

    resources/word2vec/word2vec -train data/txt/small_padded_mimic.txt -output data/vectors/w2v_small_padded_mimic.vec -size 300 -window 8 -sample 1e-4 -hs 0 -negative 8 -threads 12 -iter 5 -min-count 5 -alpha 0.025 -binary 0 -cbow 0


Building word vectors from word2vecf (in theory, equal to official word2vec)

    python code/word2vecf/generate_context_windows.py data/txt/small_padded_mimic.txt 8 data/contexts/small_padded_mimic_word.contexts data/vocabs/small_padded_mimic_word.w data/vocabs/small_padded_mimic_word.c --word

    resources/word2vecf/word2vecf -train data/contexts/small_padded_mimic_word.contexts -output data/vectors/w2vf_small_padded_mimic_word.vec -size 300 -sample 0 -hs 0 -negative 8 -threads 12 -iters 5 -alpha 0.025 -binary 0 -wvocab data/vocabs/small_padded_mimic_word.w -cvocab data/vocabs/small_padded_mimic_word.c


Building CUI-enhanced word vectors from word2vecf (AWE-CM)

    python code/word2vecf/generate_context_windows.py data/txt/small_padded_mimic.txt 8 data/contexts/small_padded_mimic_cui.contexts data/vocabs/small_padded_mimic_cui.w data/vocabs/small_padded_mimic_cui.c --cui

    resources/word2vecf/word2vecf -train data/contexts/small_padded_mimic_cui.contexts -output data/vectors/w2vf_small_padded_mimic_cui.vec -size 300 -sample 0 -hs 0 -negative 8 -threads 12 -iters 5 -alpha 0.025 -binary 0 -wvocab data/vocabs/small_padded_mimic_cui.w -cvocab data/vocabs/small_padded_mimic_cui.c


Evaluating word vectors with SRS (correlation with experts)

     python code/eval/srs/srs_eval.py data/vectors/w2v_small_padded_mimic.vec


