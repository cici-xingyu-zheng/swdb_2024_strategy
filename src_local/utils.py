import numpy as np

def moving_mean(values, window,mode='valid'):
    '''
        Computes the moving mean of the series in values, with a square window 
        of width window
    '''
    weights = np.repeat(1.0, window)/window
    mm = np.convolve(values, weights, mode)
    return mm