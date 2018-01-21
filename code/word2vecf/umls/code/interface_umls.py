#
# Interface to UMLS Databases 
#


import copy
import sqlite3
import create_sqliteDB
import os

import sys


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
umls_tables = os.path.join(parent_dir, 'umls_tables')



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

    db = sqlite3.connect( db_path )
    return db.cursor()




############################################
###      Global reource connections      ###
############################################


# Global database connection
c = SQLConnect()



############################################
###           Query Operations           ###
############################################

def cui_lookup( string ):
    """ get cui for a given string """
    try:
        # Get cuis
        c.execute( "SELECT cui FROM MRCON WHERE str = ?;" , (string,) )
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []

def cui_relation_lookup (cui_string):
    try:
        #Get Rel from cui 
        c.execute( "SELECT * FROM mrrel WHERE cui1 = ?;", (cui_string,))
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []

print "cui_lookup('blood'):   ", cui_lookup('blood')



