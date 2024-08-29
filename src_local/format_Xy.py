import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import src_local.utils as utils

def build_regressor(stim_table, format_options, behavior_session):
    # Define columns of interest from the stimulus_presentations DataFrame
    columns = ['start_time','hits','misses',
        'aborts','is_change','omitted','licked','bout_start',
        'bout_end','num_bout_start','num_bout_end','in_lick_bout']

    # Create a new DataFrame with only the selected columns
    df = pd.DataFrame(data = stim_table[columns])

    # Rename the 'is_change' column to 'change' for clarity
    df = df.rename(columns={'is_change':'change'})

    # Process behavior annotations:

    # Create 'y' column: 1 if bout_start, 0 otherwise (target variable for prediction)
    df['y'] = np.array([1 if x else 0 for x in 
        stim_table.bout_start.values]) # predict bout start

    # Calculate the **number** of images since the last lick
    df['images_since_last_lick'] = stim_table.groupby(\
        stim_table['bout_end'].cumsum()).cumcount(ascending=True)

    # Create 'timing_input': shift 'images_since_last_lick' by 1 and add 1 to each value
    df['timing_input'] = [x+1 for x in df['images_since_last_lick'].shift(fill_value=0)]


    # Build Strategy regressors:

    # # Create various encodings for the 'change' variable
    # temp_series = pd.Series(df.change.values)
    # # Use rolling window to mark 1 for True and 4 frames after
    # window_size = 5  # 1 for the True value itself, and 4 more after
    # rolled = temp_series.rolling(window=window_size, min_periods=1).sum()

    # # Create the 'y' column: 1 if bout_start or within 3 frames after, 0 otherwise
    # df['task'] = np.where(rolled > 0, 1, 0)

    df['task'] = np.array([1 if x else 0 for x in 
            df.change.values]) 
    # Create encodings for omissions
    df['omissions']  = np.array([1 if x else 0 for x in df['omitted']]) # omission
    df['omissions1'] = np.array([x for x in np.concatenate([[0], # shift omission 
                        df['omissions'].values[0:-1]])]) 
    # Build timing strategy using average timing parameters
    df['timing1D']          = np.array(\
        [timing_sigmoid(x,format_options['timing_params']) 
        for x in df['timing_input']])
    
    # Build pure timing strategy using the image change frame distribution
    df['timingGeom'] = create_timing_geom(df)

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

    # Create the psydata dict object:
    inputDict ={'task': df['task'].values[:,np.newaxis],
            'omissions' : df['omissions'].values[:,np.newaxis],
            'omissions1' : df['omissions1'].values[:,np.newaxis],
            'timing1D': df['timing1D'].values[:,np.newaxis],
            'timingGeom': df['timingGeom'].values[:,np.newaxis],
            'bias':  df['bias'].values[:,np.newaxis]}
    
    # Normalize or centering features
    # inputDict = normalize_features(inputDict, format_options['preprocess'])

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
    
def timing_sigmoid(x, params, min_val=0, max_val=1, tol=1e-3):
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

def create_timing_geom(df):

    timing_geom = []
    current_distribution = []
    
    for timing_input in df['timing_input']:
        if timing_input == 0:
            # Start of a new distribution
            timing_geom.extend(current_distribution)
            current_distribution = [0]  # Reset distribution, starting with 0
        elif 1 <= timing_input <= 4:
            current_distribution.append(0)
        elif 5 <= timing_input <= 11:
            prob = utils.truncated_geometric_prob(timing_input)
            current_distribution.append(prob)
        else:  # timing_input >= 12
            current_distribution.append(0)
    
    # Add any remaining distribution
    timing_geom.extend(current_distribution)
    
    # Ensure the length matches the original DataFrame
    if len(timing_geom) < len(df):
        timing_geom.extend([0] * (len(df) - len(timing_geom)))
    elif len(timing_geom) > len(df):
        timing_geom = timing_geom[:len(df)]
    
    return timing_geom


def normalize_features(inputDict, format_options_preprocess):
    """
    Normalize features based on the specified option in format_options['preprocess'].
    
    1: Mean centering
    2: Standard normalization (z-score)
    """
    if format_options_preprocess == 1:
        # Option 1: Mean centering
        for key in inputDict.keys():
            inputDict[key] = inputDict[key] - np.mean(inputDict[key])
    elif format_options_preprocess == 2:
        # Option 2: Standard normalization (z-score)
        for key in inputDict.keys():
            mean = np.mean(inputDict[key])
            std = np.std(inputDict[key])
            if std != 0:  # Avoid division by zero
                inputDict[key] = (inputDict[key] - mean) / std
            else:
                print(f"Warning: Standard deviation is zero for {key}. Skipping normalization.")

    return inputDict

def visualize_design(df, strategy_list, save_name, t_start = 300):

    '''
    Note that we are visualizing a not normalized or centered, 
    nor within bout excluded 
    '''
    X = df[strategy_list].to_numpy().T
    y = df['y'].to_numpy()
    X = X[:, t_start:t_start+200]
    y = y[t_start:t_start+200]
    # Set up the figure and axes
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(12, 6), 
                                gridspec_kw={'height_ratios': [4, 1]}, sharex=True)

    # Create a color normalization object
    vmin = min(X.min(), y.min())
    vmax = max(X.max(), y.max())
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    # Plot heatmap for X
    sns.heatmap(X, ax=ax1, cmap='viridis', cbar=False, norm=norm)
    ax1.set_title('Strategy Matrix X', fontsize = 16)
    ax1.set_ylabel('Strategy', fontsize = 14)
    ax1.set_yticklabels(strategy_list)
    ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Plot 1D heatmap for y
    sns.heatmap(y.reshape(1, -1), ax=ax2, cmap='viridis', cbar=False, norm=norm)
    ax2.set_title('Lick start y', fontsize = 16)
    ax2.set_xlabel('Frame', fontsize = 14)
    ax2.set_yticks([])
    ax2.set_xticks(list(range(0, 200, 50)))
    ax2.set_xticklabels(list(range(t_start, t_start+200, 50)), rotation = 0)

    # Add a colorbar to the right of the figure
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(ax1.collections[0], cax=cbar_ax, label='Value')

    # Adjust layout and display
    plt.tight_layout(rect=[0, 0, 0.9, 1])
    plt.show()

    fig.savefig(f'{save_name}.pdf')
    plt.close(fig)

