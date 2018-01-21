import sqlite3
import os
import string
import pickle
from os.path import dirname

import create_sqliteDB
import cache
import numpy as np
import sys

# find where umls tables are located
homedir = dirname(dirname(os.path.abspath(__file__)))
umls_tables = os.path.join(homedir, 'umls_tables')
print homedir
print umls_tables

############################################
###          Setups / Handshakes         ###
############################################


#connect to UMLS database
def SQLConnect():
    #try to connect to the sqlite database.
    # if database does not exit. Make one.
    db_path = os.path.join(umls_tables, "umls.db")
    if not os.path.isfile(db_path):
        print "\n\tdb doesn't exist (creating one now)\n"
        create_sqliteDB.create_db()

    db = sqlite3.connect(db_path)
    return db.cursor()




############################################
###      Global reource connections      ###
############################################


# Global database connection
conn = SQLConnect()

# cache for UMLS queries
C = cache.UmlsCache()



############################################
###           Query Operations           ###
############################################


def str_lookup(string):
    """ Get sty for a given string """
    key = ('str_lookup',string)
    if key in C:
        return C[key]
    try:
        conn.execute( "SELECT distinct sty FROM MRCON a, MRSTY b WHERE a.cui = b.cui AND str = ?; " , (string,) )
        results = conn.fetchall()
    except sqlite3.ProgrammingError, e:
        results = []
    C[key] = results
    return results


def cui_lookup(string):
    """ get cui for a given string """
    key = ('cui_lookup',string)
    if key in C:
        return C[key]
    try:
        # Get cuis
        conn.execute( "SELECT distinct cui FROM MRCON WHERE str = ?;" , (string,) )
        results = conn.fetchall()
    except sqlite3.ProgrammingError, e:
        results = []
    C[key] = results
    return results


def abr_lookup(string):
    """ searches for an abbreviation and returns possible expansions for that abbreviation"""
    key = ('abr_lookup',string)
    if key in C:
        return C[key]
    try:
        conn.execute( "SELECT distinct str FROM LRABR WHERE abr = ?;", (string,))
        results = conn.fetchall()
    except sqlite3.ProgrammingError, e:
        results = []
    C[key] = results
    return results



def tui_lookup(string):
    """ takes in a concept id string (ex: C00342143) and returns the TUI of that string which represents the semantic type is belongs to """
    key = ('tui_lookup',string)
    if key in C:
        return C[key]
    try:
        conn.execute( "SELECT distinct tui FROM MRSTY WHERE cui = ?;", (string,))
        results = conn.fetchall()
    except sqlite3.ProgrammingError, e:
        results = []
    C[key] = results
    return results



def strip_punct(stringArg):
    for c in string.punctuation:
        stringArg = string.replace(stringArg, c, "")
    return stringArg



if __name__ == '__main__':
    print "str_lookup('blood'):   ", str_lookup('blood')
    print "cui_lookup('blood'):   ", cui_lookup('blood')
    print "abr_lookup('p.o.'):    ", abr_lookup('p.o.')
    print "tui_lookup('C0005767'):", tui_lookup('C0005767')
    print "cui_lookup('male'):", cui_lookup('male')
    print "cui_lookup('inexistant'):   ",str_lookup('inexistant')
    try: 
        context_dict_filename = sys.argv[1] #Context dictionary filename becomes a parameter
        context_dict_filename = str(context_dict_filename)
        np.load(context_dict_filename).item()
        word_context_txt_name = sys.argv[2] #Context file becomes a parameter
        word_context_txt = open(word_context_txt_name,'w')
        for word in context_dict.keys():
        	for neighbor in context_dict[word]:
        	    word_context_txt.write(word+' '+str(neighbor)+'\n')
        	try:
                     cui_w= cui_lookup(word)
                     if len(cui_w)>0:
                        for cui in cui_w:
        	 	    word_context_txt.write(word+' '+str(cui[0])+'\n')
                except:
                    pass
        word_context_txt.close()
        print 'Done'
    except:
        pass

