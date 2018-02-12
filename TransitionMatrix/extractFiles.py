#!/Users/mahmoudshepero/anaconda3/bin/python3

import numpy as np
import glob

def readMatrixfiles(files):
    def openFile(name):
        with open(name, 'r') as ff:
            return( np.loadtxt(ff) )

    arrays = list(map(openFile
                      , [file for file in glob.glob(files)]))
    transitionMatrix = np.stack(arrays, axis=2)
    return(transitionMatrix)


if __name__ == "__main__":
    import sys
    files = sys.argv[1]
    print(readMatrixfiles(files))
