

import glob
import numpy as np
import re
import math

def extractDistances(filesLocation, maxTripDist=math.inf, scale=1.0):
    """Extracts the trip distances files into a dictionary which can be used
    in the model.

    Parameters
    ----------
    filesLocation : str
        The location of the files. The file names have to include the origin state
        and the destination state in the end of the file name, just before the
        extension. Example ABC01.txt, ABC10.csv.
    maxTripDist : float, optional
        The maximum trip distance to filter at.( the default initial value is
        infintiy)
    scale : float, optional
        A scale to multiply the distances with. Used to simulate various scenarios
        of daily driving distances.

    Returns
    -------
    dict
        dictionary containting the length of trips between states.

    """
    def openFile(name, scale):
        with open(name, 'r') as ff:
            array = np.loadtxt(ff)
            array = array[~np.isnan(array)]
            filteredArray = array[np.where( array <= maxTripDist )]
            return(filteredArray*scale)
    dict = {}
    for file in glob.glob(filesLocation):
         data = openFile(file, scale)
         dictStateCode = re.search(r'\d{2}(?=\.*)',file)[0]
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
