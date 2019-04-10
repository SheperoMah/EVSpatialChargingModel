import glob
import numpy as np
import re
import math

def extract_distances(filesLocation, maxTripDist = math.inf):
    """Extracts the trip distances files into a dictionary which can be used
    in the model.

    Parameters
    ----------
    filesLocation : str
        The location of the files
    maxTripDist : float, optional
        The maximum trip distance to filter at.( the default initial value is
        infintiy)

    Returns
    -------
    dict
        dictionary containting the length of trips between states.

    """
    def open_file(name):
        with open(name, 'r') as ff:
            array = np.loadtxt(ff)
            array = array[~np.isnan(array)]
            filteredArray = array[np.where( array <= maxTripDist )]
            return( filteredArray )
    dict = {}
    for file in glob.glob(filesLocation):
         data = open_file(file)
         dictStateCode = re.search(r'\d{2}',file)[0]
         dict.update({dictStateCode: data})

    return(dict)

if __name__ == "__main__":
    """Extracts the trip distances files into a dictionary which can be used
    in the model.

    Example
    -------
        $ python3 extractdistances.py ./*.txt 0.0
    """
    import sys
    filesLocation = sys.argv[1]
    maxTripDist = float(sys.argv[2])
    print(extract_distances(filesLocation, maxTripDist))
