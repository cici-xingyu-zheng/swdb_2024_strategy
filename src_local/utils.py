import numpy as np

def moving_mean(values, window,mode='valid'):
    '''
        Computes the moving mean of the series in values, with a square window 
        of width window
    '''
    weights = np.repeat(1.0, window)/window
    mm = np.convolve(values, weights, mode)
    return mm

def truncated_geometric_prob(k, p = .25, start=5, end=11):
    '''
        The true image transition probability 
        (ignoring the recurrence from the sham change...)
    '''
    if k < start or k > end:
        return 0
    
    unnormalized = p * (1-p)**(k-start)
    normalization = sum(p * (1-p)**(i-start) for i in range(start, end+1))
    return unnormalized / normalization

def calculate_index(full_evidence, reduced_evidence):
    percent_change = (reduced_evidence - full_evidence) / full_evidence
    return np.abs(percent_change) * 100  # Convert to percentage

