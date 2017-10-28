
import os, sys
import psycopg2
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import datetime
import re
import random
import numpy as np

def extract_context(word_list,window_size=2,context_dic={}): 
    '''Given a list of word, map each word to its list of left and right neighboring window_size word
       Returns context dictionary
    '''
    min_index = 0 
    max_index = max(0,len(word_list)-1)
    for current_word in range(len(word_list)):
	indices = filter(lambda x: x!=0, range(-window_size,window_size+1))
        for index in indices:
            if min(current_word+index,0)>=min_index and max(current_word+index,max_index)<=max_index:
                context_word = word_list[current_word+index]
                if word_list[current_word] in context_dic.keys():
                    context_dic[word_list[current_word]].append(context_word)
                else:
                    context_dic[word_list[current_word]]=[context_word]
    return context_dic

def main():
    try:
        size = sys.argv[1]
        window_size = int(sys.argv[2]) #window size has now become a parameter
        context_dictionary_name = sys.argv[3] # context dictionary name becomes a parameter
        if size not in ['small', 'medium', 'all']:
            raise Exception('bad')
    except Exception, e:
        print '\n\tusage: python %s <small|medium|all>\n' % sys.argv[0]
        exit(1)
    if size == 'small':
        min_id = 0
        max_id = 10
    elif size == 'medium':
        min_id = 0
        max_id = 100
    elif size == 'all':
        min_id = 0
        max_id = 1e20
    else:
        raise Exception('bad size "%s"' % size)

    # connect to the mimic database
    con = psycopg2.connect(dbname='mimic')

    #initialize context dictionary
    context_dic= {}

    # Query mimic for notes
    notes_query = \
    """
    select n.subject_id,n.text
    from mimiciii.noteevents n
    where iserror IS NULL --this is null in mimic 1.4, rather than empty space
    and subject_id > %d
    and subject_id < %d
    ;
    """ % (min_id,max_id)
    notes = pd.read_sql_query(notes_query, con)
    text = ''
    for i,row in notes.iterrows():
        toks = tokenize(row.text)
        text += ' '.join(toks)+'\n'
        extract_context(toks,window_size,context_dic)
    with open('context_small.txt','w') as f:
        f.write(text)
    f.close()
    context_dictionary_filename = str(context_dictionary_name)+'.npy'
    np.save(context_dictionary_filename,context_dic) #Save context dictionary after having read all the notes


regex_punctuation  = re.compile('[\',\.\-/\n]')
regex_alphanum     = re.compile('[^a-zA-Z0-9_ ]')
regex_num          = re.compile('\d[\d ]+')
regex_sectionbreak = re.compile('____+')
def tokenize(text):
    text = text.strip()

    # remove phi tags
    tags = re.findall('\[\*\*.*?\*\*\]', text)
    for tag in set(tags):
        text = text.replace(tag, ' ')

    # collapse phrases (including diagnoses) into single tokens
    if text != text.upper():
        caps_matches = set(re.findall('([A-Z][A-Z_ ]+[A-Z])', text))
        for caps_match in caps_matches:
            caps_match = re.sub(' +', ' ', caps_match)
            if len(caps_match) < 35:
                replacement = caps_match.replace(' ','_')
                text = text.replace(caps_match,replacement)
    year_regexes = ['(\d+) years? old', '\s(\d+) ?yo ', '(\d+)[ -]year-old',
                    '\s(\d+) yr old', '\s(\d+) yo[m/f]', '(\d+) y/o ']
    year_text = ' ' + text.lower()
    for year_regex in year_regexes:
        year_matches = re.findall(year_regex, year_text)
        for match in set(year_matches):
            binned_age = ' %s ' % bin_age(match)
            text = text.replace(match, binned_age)
    text = re.sub('_+', '_', text)
    text = text.lower()
    text = re.sub(regex_punctuation , ' '  , text)
    text = re.sub(regex_alphanum    , ''   , text)
    text = re.sub(regex_num         , ' 0 ', text)
    return text.strip().split()


def bin_age(age):
    age = int(age)
    if age < 20:
        return 'AGE_LESS_THAN_TWENTY'
    if age < 30:
        return 'AGE_BETWEEN_TWENTY_AND_THIRTY'
    if age < 40:
        return 'AGE_BETWEEN_THIRTY_AND_FOURTY'
    if age < 50:
        return 'AGE_BETWEEN_FOURTY_AND_FIFTY'
    if age < 60:
        return 'AGE_BETWEEN_FIFTY_AND_SIXTY'
    if age < 70:
        return 'AGE_BETWEEN_SIXTY_AND_SEVENTY'
    if age < 80:
        return 'AGE_BETWEEN_SEVENTY_AND_EIGHTY'
    if age < 90:
        return 'AGE_BETWEEN_EIGHTY_AND_NINETY'
    if age > 90:
        return 'AGE_OVER_NINETY'
    raise Exception('shouldnt get here')



if __name__ == '__main__':
    main()
