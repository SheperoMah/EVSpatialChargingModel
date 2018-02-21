
import numpy as np
import glob

def readMatrixfiles(files):
    """Extracts the tranistion matrix into a 3-d numpy array which can be used
    in the model.

    Parameters
    ----------
    files : str
        The location of the files

    Returns
    -------
    np.array
        Numpy array containing the transition matrix.

    """
    def openFile(name):
        with open(name, 'r') as ff:
            return( np.loadtxt(ff) )


    arrays = list(map(openFile
                      , [file for file in sorted(glob.glob(files))]))
    transitionMatrix = np.stack(arrays, axis=2)
    return(transitionMatrix)


if __name__ == "__main__":
    """Extracts the tranistion matrix into a 3-d numpy array which can be used
    in the model.

    Example
    -------
        $ python3 extractFiles.py ./*.txt
    """
    import sys
    files = sys.argv[1]
    print(readMatrixfiles(files))
