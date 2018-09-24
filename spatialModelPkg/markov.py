import numpy as np

class Markov:
    '''Class for the Markov chain.

    This class represents the transition martices.

    Attributes
    ----------
    chain : np.array(floats)
        The transition matrix as 3-d array. Square matrix in both the first two
        dimensions, where the row represents the current state, and the coulumn
        represents the following state. The z-axis represents the inhomogenous
        factor, which is the dependancy on the transition time.
    dim : int
        The dimention at which the sum of the transition matrix add to oneself.
        Default 1.
    '''
    def __init__(self, chain, dim = 1):
        self.chain = chain
        assert (self.chain.shape[0] == self.chain.shape[1]), "the transition \
            matrix should be square in the first two dimensions"
        self.cumulativeSum = np.cumsum(self.chain, axis = dim)


    def extract_transition_probability(self, currentState, time_step = None):
        '''Extracts the transition probability from the current state.

        Parameters
        ----------
        currentState : int
            The current state of the Markov chain.
        time_step : int
            The time step of the inhomegenous Markov chain.

        Returns
        -------
        np.array(float)
            The row of the tranistion probabilty matrix for the current state
            and time.

        '''
        if time_step is not None:
            return( self.cumulativeSum[currentState, :, time_step] )
        else:
            return( self.cumulativeSum[currentState, :] )


    def next_state(self, currentState, rnd, time_step = None):
        '''Estimates the future state of the Markov chain.

        Parameters
        ---------
        currentState : int
            The current state of the Markov chain.
        rnd : float
            A random number.
        time_step : int
            The time step of the inhomegenous Markov chain.

        Returns
        -------
        int
            The future state of the Markov chain.

        '''

        transitionProbCumSum = self.extract_transition_probability(currentState, time_step)
        nextState = np.where(transitionProbCumSum >= rnd)[0][0]
        return(nextState)
