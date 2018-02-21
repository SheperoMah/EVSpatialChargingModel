import numpy as np

class Markov:
    '''Class for the Markov chain.

    Attributes
    ----------
    chain : (np.array(floats))
        The transition matrix as 3-d array. Square matrix in both the first two
        dimensions, where the row represents the current state, and the coulumn
        represents the following state. The z-axis represents the inhomogenous
        factor, which is the dependancy on the transition time.
    '''
    def __init__(self, chain):
        self.chain = chain
        assert (self.chain.shape[0] == self.chain.shape[1]), "the transition \
            matrix should be square in the first two dimensions"


    def extract_transition_probability(self, currentState, time_step = None):
        '''Extracts the transition probability from the current state.

        Parameters
        ----------
        currentState : (int)
            The current state of the Markov chain.
        time_step : (int)
            The time step of the inhomegenous Markov chain.

        Returns
        -------
        np.array(float)
            The row of the tranistion probabilty matrix for the current state
            and time.

        '''
        if time_step is None:
            return( self.chain[currentState, :] )
        else:
            return( self.chain[currentState, :, time_step] )

    def next_state(self, currentState, time_step = None):
        '''Estimates the future state of the Markov chain.

        Arguments
        ---------
        currentState : (int)
            The current state of the Markov chain.
        time_step : (int)
            The time step of the inhomegenous Markov chain.

        Returns
        -------
        (int)
            The future state of the Markov chain.

        '''

        transitionProb = self.extract_transition_probability(currentState, time_step)
        cumulativeSum = transitionProb.cumsum(0)
        rndNumber = np.random.random_sample()
        nextState = np.where(cumulativeSum >= rndNumber)[0][0]
        return(nextState)
