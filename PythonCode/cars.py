#!/Users/mahmoudshepero/anaconda3/bin/python3

import random as rn
import numpy as np
from timeit import default_timer as timer
import itertools as iter
import extractFiles as ex
import matplotlib.pyplot as plt
from sys import getsizeof

class EV:
    '''Class representing electric vehicles

        Attributes:
            currentLocation (-): location of the electric vehicle.
            currentState (-): the current Markov state of the electric vehicle.
            batteryCharge (float): the charge in the battery of the electric vehicle (kWh).
            batteryCapacity (float): the battery capacity of the electric vehicle (kWh).

    '''
    def __init__(self, currentLocation, currentState, batteryCharge = 0.0,
                    batteryCapacity = 0.0, trips= 0):

        self.batteryCapcity = batteryCapacity
        self.currentLocation = currentLocation
        self.batteryCharge = batteryCharge
        self.currentState = currentState
        self.trips = trips

    def charge_EV(self, duration, stations):
        ''' Charges an EV.

            Arguments:
                power (float): the power in the charging station in (kW).
                duration (float): the charging duration in (h).

            Returns:
                (float): update to the batteryCharge

        '''
        if (self.batteryCharge < 0.0 and
            self.find_station(stations).chargingStatus == True):
            self.batteryCharge += self.find_station(stations).chargingPower * duration
            self.find_station(stations).charge_EV()
            return(True)
        else:
            return(False)

    def drive_EV(self, distance, mpg):
        ''' Disharges an EV.

            Arguments:
                distance (float): the distance driven by the electric vehicle in (km).
                mpg (float): the consumption of the the electric vehicle for
                every unit of distance in (kWh/km).

            Returns:
                (float): update to the batteryCharge

        '''
        self.batteryCharge -= distance * mpg
        return(True)

    def find_state(self, chain, time_step, stations):
        futureState = chain.next_state(self.currentState, time_step)
        if (futureState != self.currentState):
            self.currentState = futureState
            self.change_location(stations)
            self.trips += 1
            self.drive_EV(10, 0.2)
            return(True)
        else:
            return(False)

    def change_location(self, stations):
        previousStation = self.find_station(stations)
        previousStation.leave_station()

        freeStations = list(iter.filterfalse(lambda x:
                                    not(x.state == self.currentState
                                    and x.currentOccupancy < x.maximumOccupancy)
                                    , stations))
        self.currentLocation = rn.choice(freeStations).ID

        newStation = self.find_station(stations)
        newStation.occupy_station()

    def find_station(self, stations):
        station = list(iter.filterfalse(lambda x:
                                    not (x.ID == self.currentLocation)
                                    , stations))
        return(station[0])

class Markov:
    ''' Extracts the transition probability from the current state

        Attributes:
            chain (np.array(floats)): the transition matrix as 3-d array.
            Square matrix in both the x and y axis, where the row represents the
            current state, and the coulumn represents the following state. The
            z-axis represents the inhomogenous factor, which is the dependancy on
            on the transition time.
    '''
    def __init__(self, chain):
        self.chain = chain
        # assert (self.chain.sum(0) == np.ones((self.chain.shape[0],1)) ), "the sum \
        # of each row in the transition matrix should  be one"
        assert (self.chain.shape[0] == self.chain.shape[1]), "the transition \
            matrix should be square in the first two dimensions"


    def extract_transition_probability(self, currentState, time_step = None):
        ''' Extracts the transition probability from the current state.

            Arguments:
                currentState (int): the current state of the Markov chain.
                time_step (int): the time step of the inhomegenous Markov chain.

            Returns:
                np.array(float): the row of the tranistion probabilty matrix for
                the current state and time
        '''
        if time_step is None:
            return( self.chain[currentState, :] )
        else:
            return( self.chain[currentState, :, time_step] )

    def next_state(self, currentState, time_step = None):
        ''' Estimates the future state of the Markov chain.

            Arguments:
                currentState (int): the current state of the Markov chain.
                time_step (int): the time step of the inhomegenous Markov chain.

            Returns:
                (int): the future state of the Markov chain.

        '''

        transitionProb = self.extract_transition_probability(currentState, time_step)
        cumulativeSum = transitionProb.cumsum(0)
        rndNumber = np.random.random_sample()
        nextState = np.where(cumulativeSum >= rndNumber)[0][0]
        return(nextState)

class parkingLot:

    def __init__(self,
                 ID,
                 state,
                 chargingPower,
                 maximumOccupancy,
                 currentOccupancy,
                 chargingStatus = True,
                 currentLoad = 0.0):
        self.ID = ID
        self.state = state
        self.chargingStatus = chargingStatus
        self.chargingPower = chargingPower
        self.currentLoad = currentLoad
        self.maximumOccupancy = maximumOccupancy
        self.currentOccupancy = currentOccupancy

    def occupy_station(self):
        self.currentOccupancy += 1
        return( True )

    def leave_station(self):
        self.currentOccupancy -= 1

    def charge_EV(self):
        self.currentLoad += self.chargingPower


# chage state, find location,


weekdayChain = ex.readMatrixfiles("../TransitionMatrix/*weekday*.txt")
weekday = Markov(weekdayChain)
weekendChain = ex.readMatrixfiles("../TransitionMatrix/*weekend*.txt")
weekend = Markov(weekendChain)

car = [EV(currentLocation = 1, currentState = 0, batteryCharge = 0.0,
                batteryCapacity = 0.0, trips = 0) for i in range(100)]


stations = [parkingLot(ID = 1, state = 0, chargingPower = 3.7, maximumOccupancy = 100, currentOccupancy = 100, chargingStatus = True, currentLoad = 0.0),
            parkingLot(ID = 2, state = 1, chargingPower = 3.7, maximumOccupancy = 100, currentOccupancy = 0, chargingStatus = True, currentLoad = 0.0),
            parkingLot(ID = 3, state = 2, chargingPower = 3.7,maximumOccupancy =  100, currentOccupancy = 0, chargingStatus = True, currentLoad = 0.0)]



def model_function(timestep, chain, car, stations):
    stations[0].currentLoad = 0.0
    stations[2].currentLoad = 0.0
    stations[1].currentLoad = 0.0

    def function_on_car(x,chain, timestep, stations):
        x.find_state(chain, timestep, stations)
        x.charge_EV(1/60, stations)

    list(map(lambda x: function_on_car(x, chain, timestep, stations), car))
    return(list(map(lambda x: x.currentLoad, stations)))



bb = list(iter.accumulate(range(-1,10080), lambda x, y: model_function( y % 1440, weekday, car, stations) ))

cc = np.asarray(bb[1 : len(bb)])
cc = cc[:,2]
# iterate time
# bb = list(iter.accumulate(range(525600), lambda x, y: weekday.next_state(x,y % 1440) ))
# np.asarray(bb)
# # print(getsizeof(bb)*10**-6)
# cc = np.copy(bb[:,0])
# # print(getsizeof(cc)*10**-6)
cc = np.reshape(cc, (7,1440))
# # print(getsizeof(cc)*10**-6)
#
# # Testing code
plt.plot(np.mean(cc, axis = 0))
# # def count_occurences(array,value):
# #     occurence = cc == value
# #     return(np.sum(occurence, axis = 0)/np.size(occurence, 0))
# #
# # home = count_occurences(cc,0)
# # work = count_occurences(cc,1)
# # other = count_occurences(cc,2)
#
# # plt.plot(range(1440), home, 'r')
# # plt.plot(range(1440), work, 'b')
# # plt.plot(range(1440), other, 'm')
plt.show()
