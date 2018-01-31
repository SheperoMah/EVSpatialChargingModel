#!/Users/mahmoudshepero/anaconda3/bin/python3

import random as rn
import numpy as np
from timeit import default_timer as timer

start = timer()

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
        assert (isinstance(self.batteryCharge, float)), "battery charge should be float"
        assert (isinstance(self.batteryCapcity, float)), "batteryCapacity should be float"

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




ll = [EV("id=1",1, 0.0, 0.0) for i in range(1000000)] # million cars

for time in range(1000): # million timesteps
    list(map(lambda x, distance = rn.random()*10000: x.driveEV(distance,1.0), ll))

# squared = list(map(lambda x: x.batteryCharge, ll))



# items = [1, 2, 3, 4, 5]
# squared = list(map(lambda x: x**2, items))

end = timer()
print(end - start)
