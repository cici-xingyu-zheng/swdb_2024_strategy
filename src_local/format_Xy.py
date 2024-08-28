import numpy as np
import pandas as pd
import copy

def build_regressor(stim_table, format_options, behavior_session):
    # Define columns of interest from the stimulus_presentations DataFrame
    columns = ['start_time','hits','misses',
        'aborts','is_change','omitted','licked','bout_start',
        'bout_end','num_bout_start','num_bout_end','in_lick_bout']

    # Create a new DataFrame with only the selected columns
    df = pd.DataFrame(data = stim_table[columns])

    # Rename the 'is_change' column to 'change' for clarity
    df = df.rename(columns={'is_change':'change'})

    # Process behavior annotations
    # Create 'y' column: 2 if bout_start, 1 otherwise (target variable for prediction)
    df['y'] = np.array([2 if x else 1 for x in 
        stim_table.bout_start.values]) # predict bout start

    # Calculate the **number** of images since the last lick
    df['images_since_last_lick'] = stim_table.groupby(\
        stim_table['bout_end'].cumsum()).cumcount(ascending=True)

    # Create 'timing_input': shift 'images_since_last_lick' by 1 and add 1 to each value
    df['timing_input'] = [x+1 for x in df['images_since_last_lick'].shift(fill_value=0)]


    # Build Strategy regressors
    # Create various encodings for the 'change' variable
    df['task']      = np.array([1 if x else 0 for x in df['change']]) 
    # Create encodings for omissions
    df['omissions']  = np.array([1 if x else 0 for x in df['omitted']]) # omission
    df['omissions1'] = np.array([x for x in np.concatenate([[0], # shift omission 
                        df['omissions'].values[0:-1]])]) 
    # Build timing strategy using average timing parameters
    df['timing1D']          = np.array(\
        [timing_sigmoid(x,format_options['timing_params']) 
        for x in df['timing_input']])

    # Add a bias term (constant feature)
    df['bias'] = 1

    # Create 'included' column: True if not in a lick bout
    df['included'] = ~df['in_lick_bout']

    # Make a copy before trimming data
    full_df = copy.copy(df) 
    # Segment out consumption trials
    df = df[df['included']] # this excusion is becaouse the 'in_lick_bout' state has only to do with consumption
    # Numer of trails that we leave out:
    df['missing_trials'] = np.concatenate([np.diff(df.index)-1,[0]])

    inputDict ={'task': df['task'].values[:,np.newaxis],
            'omissions' : df['omissions'].values[:,np.newaxis],
            'omissions1' : df['omissions1'].values[:,np.newaxis],
            'timing1D': df['timing1D'].values[:,np.newaxis],
            'bias':  df['bias'].values[:,np.newaxis]}
    
    # Pack up data into format for psytrack
    psydata = { 'y': df['y'].values, 
                'inputs':inputDict, 
                'hits': df['hits'].values,
                'misses':df['misses'].values,
                'aborts':df['aborts'].values,
                'start_times':df['start_time'].values,
                'image_ids': df.index.values,
                'df':df,
                'full_df':full_df }

    psydata['session_label'] = [behavior_session.metadata['session_type']]
    
    return psydata
    
def timing_sigmoid(x, params, min_val=-1, max_val=0, tol=1e-3):
    '''
    param[0]: exponent
    param[1]: mean point
    '''
    if np.isnan(x):
        x = 0 
    y = min_val + (max_val - min_val) / (1 + (x / params[1])**params[0])
    if (y - min_val) < tol:
        y = min_val
    if (max_val - y) < tol:
        y = max_val
    return y


def normalize_features(inputDict, format_options):
    """
    Normalize features based on the specified option in format_options['mean_center'].
    
    1: Mean centering
    2: Standard normalization (z-score)
    """
    if format_options['mean_center'] == 1:
        # Option 1: Mean centering
        for key in inputDict.keys():
            inputDict[key] = inputDict[key] - np.mean(inputDict[key])
    elif format_options['mean_center'] == 2:
        # Option 2: Standard normalization (z-score)
        for key in inputDict.keys():
            mean = np.mean(inputDict[key])
            std = np.std(inputDict[key])
            if std != 0:  # Avoid division by zero
                inputDict[key] = (inputDict[key] - mean) / std
            else:
                print(f"Warning: Standard deviation is zero for {key}. Skipping normalization.")
    
    return inputDict

def visualize_design():
    pass


