
1) Download data

    - Create i2b2 account
        - https://www.i2b2.org/NLP/DataSets/Main.php

    - Select "2010 Relations Challenge"
        - training sentences & labels
        - test sentences
        - test labels


2) The provided data has a few mis-annotations. Fix the following:

    - concept_assertion_relation_training_data/partners/concept/920798564.con 
        - Has two overlapping spans
            - c="bun" 30:6 30:6||t="test"
            - c="elevated bun" 30:5 30:6||t="problem"
        - remove c="bun" 30:6 30:6||t="test"

    - concept_assertion_relation_training_data/beth/concept/record-124.con
        - Has two overlapping spans
            - c="patient" 140:1 140:1||t="test"
            - c="the patient 's narcotic" 140:0 140:3||t="treatment"
        - remove c="patient" 140:1 140:1||t="test"


3) Put the data in the right spot

    - data/concept_extraction/original_i2b2/concept_assertion_relation_training_data
    - data/concept_extraction/original_i2b2/test_data
    - data/concept_extraction/original_i2b2/reference_standard_for_test_data


4) Run word2vec.py on your word vectors file
