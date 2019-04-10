import numpy as np
import math
import pandas as pd
import itertools as iter

def correct_time(time, resolution):
    """ Corrects time from HHMM format to 0:end scale, where end is dependent
    on the resolution.

    Parameters
    ----------
    time : float, int
        Time in HHMM format. Example: 1530 to represent 15:30.

    resolution : int
        Minute resolution used for the time-step, i.e., how many minutes
        represent one time-step.

    Returns
    -------
    float, int
        Time in new format. If time is indivisable by the scale it floors it.

    Examples
    --------
    Change time to minute-scale.
    >>> correct_time(1530, 1)
    929

    Change time to 15-min-scale.
    >>> correct_time(1530, 15)
    61

    Change time to 15-min-scale.
    >>> correct_time(1529, 15) == correct_time(1515, 15) == 60

    """
    assert resolution >= 1 and resolution <= 60 and type(resolution) == int, \
    "Resolution ranges between 1 and 60 minutes, i.e., resolution in \
    {1, 2, 3, ..., 60}"
    hour = math.floor(time/100)
    minute = time % 100

    timeNewScale = hour * 60 / resolution  + math.floor(minute/resolution)

    return(int(timeNewScale))


def condition_on_column(dictionary, cond, column):
    """ Returns a function applying the condition on the column of a
    dataFrame. Both the condition and column are stored in a dictionary.

    Parameters
    ----------


    Returns
    -------
    function
        A funtion applying the condition on a column of the dataframe.


    Examples
    --------
    This example applies a function on a column of a dataframe. Both the function
    and the coulumn are stored in the dictionary.

    >>> df = pd.DataFrame(data = {'col1': [1, 2, 3], 'col2': [3, 4, 4]})
    >>> f = condition_on_column({'conditionFunc': lambda x: x.isin([1, 3]), \
                                 'columnName': 'col2'},
                                'conditionFunc',
                                'columnName')
    >>> f(df)

    """
    function = dictionary[cond]
    columnID = dictionary[column]
    return(lambda x: function(x[columnID]))


def arrange_data(dataFrame,
         dictionaryData):
    """ Arranges the data into a dictionary of results

    Examples
    --------
    >>> dictionaryData = {'weekday_ColName' : "UEDAG",
        'weekend_Condition' : lambda x: x in [6,7],
        'vehicle_ColName' : 'D_FORD',
        'vehicle_Condition' : lambda x: x >= 500,
        'departure_ColName' : "D_A_KL",
        'arrival_ColName' : "D_B_KL",
        'distance_ColName' : "D_KM",
        'departure_locationColName' : "D_A_PKT",
        'arrival_locationColName' : "D_B_PKT",
        'home_locationCondition' : lambda x: x.isin([1,2,3,9,7]),
        'work_locationCondition' : lambda x: x.isin([4,5,6,8]),
        'other_locationCondition' : lambda x: x == 10,
        'unique_locationsNames' :  {'home', 'work', 'other'},
        'unique_dataTypes' : {'arrival', 'departure', 'distance'}
        }
    >>> arrange_data(df, dictionaryData)

    """

    result = {}
    setOfLocations = dictionaryData['unique_locationsNames']
    setOfDataTypes = dictionaryData['unique_dataTypes']

    # All permutations of source,destination,setOfDataTypes
    permutations = [(s, d, dt) for s in setOfLocations for d in setOfLocations for dt in setOfDataTypes if s != d]

    # Loop through the permutations and organize the data into dictionary.
    for (source,destination,dataType) in permutations:

            result[source + destination + dataType] = dataFrame.loc[ \
                (condition_on_column(dictionaryData, source + '_locationCondition', 'departure_locationColName')(dataFrame)) & \
                (condition_on_column(dictionaryData, destination + '_locationCondition', 'arrival_locationColName')(dataFrame))
                ][dictionaryData[ dataType + '_ColName']].dropna().tolist()
    return(result)


def event_time_to_rates(listOfEvents, length):
    """ Converts a list of event times to a list of number of events for every
    time-step within the length.
    count(x == time), for every time-step.

    Examples
    --------
    >>> eventTime = [0, 1, 1, 2, 3]
    >>> event_time_to_rates(eventTime, 4)
    [1, 2, 1, 1]

    """
    if len(listOfEvents) == 0:
        # Empty list of  events == zero rate
        return([0 for i in range(length)])
    else:
        assert max(listOfEvents) < length, ("There are arrivals after the " +
        f"end of the time. Last arrival at {max(listOfEvents)} is before " +
        "time {length-1}. Note the last time-step = {length} - 1, we count from 0.")

        eventsOnTime = [[1 for x in listOfEvents if x == i]
                                for i in range(length)]
        numberOfEvents = [sum(l) for l  in eventsOnTime]
        return(numberOfEvents)


def from_arrivals_to_accumulated_rates(listOfEventTimes, length):
    """ Converts the list of event times to a list of events occuring before or at
    every time-step.
    count(x <= time), for every time-step.

    Examples
    --------
    >>> eventTime = [0, 1, 1, 2, 3]
    >>> from_arrivals_to_accumulated_rates(eventTime, 4)
    [1, 3, 4, 5]

    """
    eventRates = event_time_to_rates(listOfEventTimes, length)
    accumulated_rates = list(iter.accumulate(eventRates))
    return(accumulated_rates)


def estimate_occupancy(arrivalsTimes,
                       departureTimes,
                       length = 1440,
                       initialOcc = 0):
    """ Returns the temporal occupancy given some arrivals and departures.

    Examples
    --------
    >>> estimate_occupancy([0,1,1,1])

    """
    occupancy = [initialOcc for i in range(length)]

    arrivals = from_arrivals_to_accumulated_rates(arrivalsTimes, length)
    departures = from_arrivals_to_accumulated_rates(departureTimes, length)

    for i in range(length):
        occupancy[i] = occupancy[i] + arrivals[i] - departures[i]

    return(occupancy)


def occupancy_for_location(data, location, initialOcc, length):
    """ Returns the occupancy in a certain location.

    """
    arrivalKeys = [ii for ii in data.keys() if ii.endswith(location +
                   'arrival')]
    departureKeys = [ii for ii in data.keys()
                     if ii.startswith(location) and ii.endswith('arrival')]

    arrivalDataDict =   [data[i] for i in arrivalKeys]
    departureDataDict = [data[i] for i in departureKeys]
    arrivalTimes = list(iter.chain(*arrivalDataDict))
    departureTimes = list(iter.chain(*departureDataDict))
    occupancy = estimate_occupancy(arrivalTimes, departureTimes, \
        length, initialOcc)
    return(occupancy)


def string_filter_start_end_contain(string, prefix, suffix, content):
    """ Retruns true when a string starts with the prefix, ends with the suffix
    and contains the content.

    Examples
    --------
    >>> string_filter_start_end_contain("string", "str", "ring", "ing")
    True
    >>> string_filter_start_end_contain("string", "str", "", "")
    True

    """
    bool = content in string and string.startswith(prefix) and \
    string.endswith(suffix)
    return(bool)


def estimate_occupancy_for_locations(arrivalDataLocations,
                                     unique_locationsNames,
                                     occKeyNameWeekday,
                                     resolution):
    """ Estimates the occupancy for a set of locations. Each location has a name
    and occupancy
    """
    occupancyLocations = {}
    for i in unique_locationsNames:
        occupancyLocations[i] = occupancy_for_location(arrivalDataLocations,
                                              location = i,
                                              initialOcc=occKeyNameWeekday[i],
                                              length=resolution)
    return(occupancyLocations)


def sort_and_correct_time(data,
                          dataDict,
                          resolution=1):
    """ Returns the sorted and correct time data.
    """
    sortedData = arrange_data(data, dataDict)

    # Correct the arrival and departure times
    filterOfTimeKeys = [i for i in sortedData.keys() if 'distance' not in i]
    for i in filterOfTimeKeys:
        sortedData[i] = [correct_time(x,resolution) for
                          x in sortedData[i]]
    return(sortedData)


def estimate_transition_probability_location(occupancyData,
                                             timeData,
                                             timeOfEvent,
                                             originStr,
                                             destinationStr,
                                             codeStr = 'arrival'):
    keyOfTimeData = originStr + destinationStr + codeStr
    countEventsAtTime = len([x for x in timeData[keyOfTimeData] if x == timeOfEvent])
    probability = countEventsAtTime / occupancyData[originStr][timeOfEvent]
    return(probability)


def estimate_tranisiton_matrix(occupancyData,
         timeData,
         locationsList,
         codeStr = 'arrival',
         lengthOfDay = 1440):

    numberOfStates = len(locationsList)
    transitionMatrix = np.zeros((numberOfStates, numberOfStates, lengthOfDay))
    perm = [(i,ii) for i in enumerate(locationsList) for \
            ii in enumerate(locationsList) if i != ii]

    for t in range(lengthOfDay):
        # Pij(t) = Nij(t) / \sum_{\forall j} Nij(t)
        # Note that \sum_{\forall j} Nij(t) = occupancy_{i}(t)

        # Calculate Pjj(t) where i != j
        for ((iOrigin, origin),(iDestination, destination)) in perm:
                transitionMatrix[iOrigin, iDestination, t] = \
                estimate_transition_probability_location(occupancyData,
                                                         timeData,
                                                         t,
                                                         origin,
                                                         destination,
                                                         'arrival')
        # Calculate Pii(t) = 1 - \sum_{\forall j where j != i} Pij(t)
        complementary = np.eye(numberOfStates) * \
                        (1 - transitionMatrix[:,:,t].sum(1))
        for i, ii in enumerate(locationsList):
            transitionMatrix[i, :, t] += complementary[i,:]

    return(transitionMatrix)


def main():

    dataDict = {'weekday_ColName' : "UEDAG",
    'weekday_Condition' : lambda x: x < 6,
    'vehicle_ColName' : "D_FORD",
    'vehicle_Condition' : lambda x: x >= 500,
    'departure_ColName' : "D_A_KL",
    'arrival_ColName' : "D_B_KL",
    'distance_ColName' : "D_KM",
    'departure_locationColName' : "D_A_PKT",
    'arrival_locationColName' : "D_B_PKT",
    'home_locationCondition' : lambda x: x.isin([1,2,3,9,7]),
    'work_locationCondition' : lambda x: x.isin([4,5,6,8]),
    'other_locationCondition' : lambda x: x == 10,
    'unique_locationsNames' :  {'home', 'work', 'other'},
    'unique_dataTypes' : {'arrival', 'departure', 'distance'},
    'occupancyWeekday': {'home': 12000, 'work' : 37, 'other' : 156},
    'occupancyWeekend': {'home': 12000, 'work' : 7, 'other' : 151}
    }

    simulationTimeResoultion = 1 # 1 minute
    lengthOfDay = 1440 # 1440 minutes
    folder = "../transitionMatrixPython/" # where to store results
    dataFrame = pd.read_csv("../Data/Data_travel data.csv", sep = ';') # which file to read

    ##### Code #####

    # Filter the dataframe to based on vehicle condition. (Should be done outside)
    dfCars = dataFrame.loc[condition_on_column(dataDict, 'vehicle_Condition',
    'vehicle_ColName')(dataFrame)]

    # Weekday
    weekdayDf = dfCars.loc[condition_on_column(dataDict, 'weekday_Condition',
    'weekday_ColName')(dataFrame)]
    # Weekend (not a weekday)
    weekendDf = dfCars.loc[~(condition_on_column(dataDict, 'weekday_Condition',
    'weekday_ColName')(dataFrame))]


    sortedWeekday = sort_and_correct_time(weekdayDf,
                                          dataDict,
                                          simulationTimeResoultion)
    sortedWeekend = sort_and_correct_time(weekendDf,
                                          dataDict,
                                          simulationTimeResoultion)

    occupancyWeekday = estimate_occupancy_for_locations(sortedWeekday,
                                     dataDict['unique_locationsNames'],
                                     dataDict['occupancyWeekday'],
                                     lengthOfDay)
    occupancyWeekend = estimate_occupancy_for_locations(sortedWeekend,
                                     dataDict['unique_locationsNames'],
                                     dataDict['occupancyWeekend'],
                                     lengthOfDay)

    transitionMatrixWeekday = estimate_tranisiton_matrix(occupancyWeekday, sortedWeekday,
                                ['home', 'work', 'other'])
    transitionMatrixWeekend = estimate_tranisiton_matrix(occupancyWeekend, sortedWeekend,
                                ['home', 'work', 'other'])

    for i in range(lengthOfDay):
        np.savetxt(folder + f"weekday{i:04d}.txt", transitionMatrixWeekday[:,:,i])
        np.savetxt(folder + f"weekend{i:04d}.txt", transitionMatrixWeekend[:,:,i])











if __name__ == "__main__":
        main()
