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
                    batteryCapacity = 0.0):

        self.batteryCapcity = batteryCapacity
        self.currentLocation = currentLocation
        self.batteryCharge = batteryCharge
        self.currentState = currentState


    def chargeEV(self, power, duration):
        ''' Charges an EV.

            Arguments:
                power (float): the power in the charging station in (kW).
                duration (float): the charging duration in (h).

            Returns:
                (float): update to the batteryCharge

        '''
        self.batteryCharge += power * duration

    def driveEV(self, distance, mpg):
        ''' Disharges an EV.

            Arguments:
                distance (float): the distance driven by the electric vehicle in (km).
                mpg (float): the consumption of the the electric vehicle for
                every unit of distance in (kWh/km).

            Returns:
                (float): update to the batteryCharge

        '''
        self.batteryCharge -= distance * mpg

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


    def extractTransitionProbability(self, currentState, time_step = None):
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

    def nextState(self, currentState, time_step = None):
        ''' Estimates the future state of the Markov chain.

            Arguments:
                currentState (int): the current state of the Markov chain.
                time_step (int): the time step of the inhomegenous Markov chain.

            Returns:
                (int): the future state of the Markov chain.

        '''

        transitionProb = self.extractTransitionProbability(currentState, time_step)
        cumulativeSum = transitionProb.cumsum(0)
        rndNumber = np.random.random_sample()
        nextState = np.where(cumulativeSum >= rndNumber)[0][0]
        return(nextState)


# class parkingLot:

    # def __init__(self, chargingStatus = True, chargingPower, numberOfParkingLots):
    #     self.chargingStatus = chargingStatus
    #     self.chargingPower = chargingPower
    #     self.numberOfParkingLots = numberOfParkingLots




chain = ex.readMatrixfiles("../TransitionMatrix/*weekend*.txt")
a = Markov(chain)
# print(chain)
# print(a.nextState(1))

bb = list(iter.accumulate(range(525600), lambda x, y: a.nextState(x,y%1440) ))
np.asarray(bb)
print(getsizeof(bb)*10**-6)
cc = np.copy(bb)
print(getsizeof(cc)*10**-6)
cc = np.reshape(cc, (365,1440))
print(getsizeof(cc)*10**-6)


#plt.plot(bb)
# def count_occurences(array,value):
#     occurence = cc == value
#     return(np.sum(occurence, axis = 0)/np.size(occurence, 0))
#
# home = count_occurences(cc,0)
# work = count_occurences(cc,1)
# other = count_occurences(cc,2)
#
# plt.plot(range(1440), home, 'r')
# plt.plot(range(1440), work, 'b')
# plt.plot(range(1440), other, 'm')
# plt.show()
