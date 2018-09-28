
import numpy as np
import glob

def readMatrixfiles(files, precision = 1000):
    """Extracts the tranistion matrix into a 3-d numpy array which can be used
    in the model.

    Parameters
    ----------
    files : str
        The location of the files
    precision : int, optional
        The precision factor. Is used to correct for mistakes in decimal number
        approximations in computer systems. The default will work fine.(the
        default is 1000)

    Returns
    -------
    np.array
        Numpy array containing the transition matrix.

    """
    def openFile(name, precision):
        with open(name, 'r') as ff:
            array = np.loadtxt(ff) * precision
            preciseArray = np.ceil(array) / precision
            return( preciseArray )


    arrays = [openFile(x, precision) for x in sorted(glob.glob(files))]
    transitionMatrix = np.stack(arrays, axis=2)
    return(transitionMatrix)


if __name__ == "__main__":
    """Extracts the tranistion matrix into a 3-d numpy array which can be used
    in the model.

    Example
    -------
        $ python3 extractFiles.py './*.txt' 1000
    """
    import sys
    files = sys.argv[1]
    precision = int(sys.argv[2])
    a = readMatrixfiles(files, precision)
    print(a)
    print("Shape of Matrix is " + str(a.shape[0]), str(a.shape[1]),
str(a.shape[2]))
