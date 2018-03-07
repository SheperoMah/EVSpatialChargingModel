

class ParkingLot:
    """A class representing parking lots.

    Attributes
    ----------
    ID : (-)
        ID of the station, ususally string.
    state : int
        The state of the station. What is the station used for.
    chargingPower : float
        The charging power of the station. Set it to 0.0 if the station does not
        charge the vehicle.
    maximumOccupancy : int
        The number of charging ports available in the parking lot.
    chargingStatus : bool
        Boolean, true if charging is enabled in this parking lot.
    currentLoad : float
        The current load of the station in the unit of power.

    """

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
        """Occupies the parking lot, increases the occupancy by one.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.currentOccupancy += 1


    def leave_station(self):
        """Leaves the parking lot, decreases the occupancy by one.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.currentOccupancy -= 1

    def charge_EV(self, power):
        """Charges the EV and updates the load of the station.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # current load is in unit of power * unit of time, in other words, it is
        # energy. For example, if we work with kW for power and time in minutes,
        # then the current load will be in kWmin/min, thus to aggregate to one hour
        # you need to average the values which results in kWh/h.

        self.currentLoad += power
