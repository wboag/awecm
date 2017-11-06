
import os
from os.path import dirname

from build_corpus import tokenize


def main():

    homedir = dirname(dirname(dirname(os.path.abspath(__file__))))
    datadir = os.path.join(homedir, 'data', 'public_discharges')
    for i in range(25):
        for disch in os.listdir(datadir):
            filename = os.path.join(datadir, disch)
            with open(filename, 'r') as f:
                text = f.read()
            toks = tokenize(text)
            print ' '.join(toks)



if __name__ == '__main__':
    main()
