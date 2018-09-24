

import glob
import numpy as np
import re
import math

def extractDistances(filesLocation, maxTripDist = math.inf):
    """Extracts the trip distances files into a dictionary which can be used
    in the model.

    Parameters
    ----------
    filesLocation : str
        The location of the files
    maxTripDist : float
        The maximum trip distance to filter at.

    Returns
    -------
    dict
        dictionary containting the length of trips between states.

    """
    def openFile(name):
        with open(name, 'r') as ff:
            array = np.loadtxt(ff)
            array = array[~np.isnan(array)]
            filteredArray = array[np.where( array <= maxTripDist )]
            return( filteredArray )
    dict = {}
    for file in glob.glob(filesLocation):
         data = openFile(file)
         dictStateCode = re.search(r'\d{2}',file)[0]
         dict.update({dictStateCode: data})

    return(dict)

if __name__ == "__main__":
    """Extracts the trip distances files into a dictionary which can be used
    in the model.

    Example
    -------
        $ python3 extractDistances.py ./*.txt 0.0
    """
    import sys
    filesLocation = sys.argv[1]
    maxTripDist = float(sys.argv[2])
    print(extractDistances(filesLocation, maxTripDist))
