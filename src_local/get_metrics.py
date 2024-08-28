import numpy as np
import pandas as pd
from scipy.stats import norm

'''
This is a set of functions for calculating and analyzing model free behavioral 
metrics on a image by image basis

Instead of modifying attributes, we direct use those dfs as inputs, 
and the extended version as outputs.

Code author: Alex Piet, alexpiet@gmail.com
Code modification: CiCi Xingyu Zheng, ceciliazheng01@gmail.com
'''

bout_threshold = .7

def annotate_licks(licks, behavior_session):

    '''
    Appends several columns to licks. Calculates licking bouts based on a
    interlick interval (ILI) of bout_threshold. Default of 700ms based on examining 
    histograms of ILI distributions

    Adds to licks:
    
        pre_ili,        (seconds)
        post_ili,       (seconds)
        bout_start,     (boolean) Whether this lick triggered a new licking bout
        bout_end,       (boolean) Whether this lick ended a licking bout
        bout_number,    (int) The label for the licking bout that contained
                        this lick
        rewarded,       (boolean) Whether this lick triggered a reward
        num_rewards,    (int) The number of rewards triggered to this lick. This is
                        only greater than 1 for auto-rewards, which are assigned
                        to the nearest lick. 
        bout_rewarded,  (boolean) Whether this bout triggered a reward.
        bout_num_rewards,(int) The number of rewards triggered to this bout. This is
                        only greater than 1 for auto-rewards. 
    '''

    # Filter out omitted stimulus presentations
    non_omitted = behavior_session.stimulus_presentations[~behavior_session.stimulus_presentations['omitted']]

    # Get the start time of the first non-omitted stimulus
    stim_start = non_omitted['start_time'].values[0]
    # Get the end time of the last stimulus presentation plus 0.75 seconds
    stim_end = behavior_session.stimulus_presentations['start_time'].values[-1]+0.75

    # Filter licks to only those within the stimulus period
    licks.query('(timestamps > @stim_start) and (timestamps <= @stim_end)',
        inplace=True)
    # Reset the index of the filtered licks dataframe
    licks.reset_index(drop=True,inplace=True)

    # Calculate pre-lick intervals, setting first to 2*bout_threshold as an offset with save value
    licks['pre_ili'] = np.concatenate([
        [bout_threshold*2],np.diff(licks.timestamps.values)])
    
    # Calculate post-lick intervals, setting last to 2*bout_threshold    
    licks['post_ili'] = np.concatenate([
        np.diff(licks.timestamps.values),[bout_threshold*2]])

    # Mark licks as bout starts if pre_ili is greater than bout_threshold
    licks['bout_start'] = licks['pre_ili'] > bout_threshold

    # Mark licks as bout ends if post_ili is greater than bout_threshold
    licks['bout_end'] = licks['post_ili'] > bout_threshold

    # Assign bout numbers by cumulative sum of bout starts
    licks['bout_number'] = np.cumsum(licks['bout_start']) # as licks are ordered by time

    # Initialize 'rewarded' column to False for all licks
    licks['rewarded'] = False 

    # Initialize 'num_rewards' column to 0 for all licks
    licks['num_rewards'] = 0 
    
    # Iterate through each reward
    for index, row in behavior_session.rewards.iterrows():
        # If the reward is auto-rewarded
        if row.auto_rewarded:
            # Find the index of the nearest lick to the reward time 
            # so we assue the mice just get it
            mylick = np.abs(licks.timestamps - row.timestamps).idxmin()
        
        # If it's not an auto-reward
        else:
            # Find all licks that occurred before or at the reward time
            this_reward_lick_times=np.where(licks.timestamps<=row.timestamps)[0]    
            # If no licks occurred before the reward
            if len(this_reward_lick_times) == 0:
                raise Exception('First lick was after first reward')
                # Raise an exception
            else:
                # Get the index of the last lick before or at the reward time
                mylick = this_reward_lick_times[-1]

        # Mark the identified lick as rewarded
        licks.at[mylick,'rewarded'] = True 

        # Increment the number of rewards for the identified lick
        licks.at[mylick,'num_rewards'] +=1  

    # Groupby functions: 
    # Group licks by bout number and check if any lick in each bout was rewarded
    x = licks.groupby('bout_number').any('rewarded').\
        rename(columns={'rewarded':'bout_rewarded'})  
    # Group licks by bout number and sum the number of rewards for each bout
    y = licks.groupby('bout_number')['num_rewards'].sum().\
        rename('bout_num_rewards')
    
    # Initialize 'bout_rewarded' column to False for all licks
    licks['bout_rewarded'] = False

    # Create a temporary dataframe with bout_number as index
    temp = licks.reset_index().set_index('bout_number')

    # Update the temporary dataframe with bout reward information
    temp.update(x)

    # Add bout_num_rewards to the temporary dataframe
    temp['bout_num_rewards'] = y

    # Reset index of temporary dataframe
    temp = temp.reset_index().set_index('index')

    # Update bout_rewarded in the original dataframe
    licks['bout_rewarded'] = temp['bout_rewarded']

    # Update bout_num_rewards in the original dataframe
    licks['bout_num_rewards'] = temp['bout_num_rewards'] 

    # Count the total number of rewarded licks
    num_lick_rewards = licks['rewarded'].sum()

    # Get the total number of rewards
    num_rewards = len(behavior_session.rewards)

    # Calculate the number of double rewards (Not sure why this could even happen)
    double_rewards = np.sum(licks.query('num_rewards >1')['num_rewards']-1)

    # Check if the total rewards match the sum of lick rewards and double rewards
    assert num_rewards == num_lick_rewards+double_rewards, \
        "Lick Annotations don't match number of rewards"
    
    # Count the number of rewarded bouts
    num_rewarded_bouts=np.sum(licks['bout_rewarded']&licks['bout_start'])

    # Calculate the number of double rewarded bouts
    double_rewarded_bouts = np.sum(licks[licks['bout_rewarded']&\
        licks['bout_start']&\
        (licks['bout_num_rewards']>1)]['bout_num_rewards']-1)
    
    # Check if the total rewards match the sum of rewarded bouts and double rewarded bouts
    assert num_rewards == num_rewarded_bouts+double_rewarded_bouts, \
        "Bout Annotations don't match number of rewards"
    
    # Count the number of bout starts
    num_bout_start = licks['bout_start'].sum()

    # Count the number of bout ends
    num_bout_end = licks['bout_end'].sum()

    # Get the total number of bouts
    num_bouts = licks['bout_number'].max()

    # Check if the number of bout starts equals the number of bout ends
    assert num_bout_start==num_bout_end, "Bout Starts and Bout Ends don't align"

    # Check if the number of bout starts equals the total number of bouts
    assert num_bout_start == num_bouts, "Number of bouts is incorrect"

    return licks





# Define the function that takes a 'session' parameter
def annotate_bouts(licks, stimulus_presentations):
    '''
    Uses the bout annotations in licks to annotate stimulus_presentations
    Adds several columns to session.stimulus_presentations:
    bout_start, num_bout_start, bout_number, bout_end, num_bout_end

    Input: 
        licks: lick df that has been annotated;
        stimulus_presentations: df to be extended

    Output: 
        stimulus_presentations with additional columns:

        bout_start,     (boolean) Whether a licking bout started during this image
        num_bout_start, (int) The number of licking bouts that started during this
                        image. This can be greater than 1 because the bout duration
                        is less than 750ms. 
        bout_number,    (int) The label of the licking bout that started during this
                        image
        bout_end,       (boolean) Whether a licking bout ended during this image
        num_bout_end,   (int) The number of licking bouts that ended during this
                        image. 

    '''

    # Select all licks that start a bout
    bout_starts = licks[licks['bout_start']]

    # Initialize 'bout_start' column in stimulus_presentations to False
    stimulus_presentations['bout_start'] = False
    # Initialize 'num_bout_start' column in stimulus_presentations to 0
    stimulus_presentations['num_bout_start'] = 0

    # Iterate through each bout start
    for index, x in bout_starts.iterrows():
        # Find all stimuli that started before this bout
        filter_start = stimulus_presentations.query('start_time < @x.timestamps')
        
        # If there are stimuli before this bout
        if len(filter_start) > 0:
            # Get the index of the last stimulus before the bout
            start_index = filter_start.index[-1]
            
            # Mark this stimulus as the start of a bout
            stimulus_presentations.at[start_index,'bout_start'] = True
            
            # Increment the number of bouts starting at this stimulus
            stimulus_presentations.at[start_index,'num_bout_start'] += 1
            
            # Assign the bout number to this stimulus
            stimulus_presentations.at[start_index,'bout_number'] = x.bout_number
        
        # If the bout started before the first stimulus
        elif x.timestamps <= stimulus_presentations.iloc[0].start_time:
            # Mark the first stimulus as the start of a bout
            stimulus_presentations.at[0,'bout_start'] = True
            
            # Increment the number of bouts starting at the first stimulus
            stimulus_presentations.at[0,'num_bout_start'] += 1
        
        # If we couldn't annotate the bout start, raise an exception
        else:
            raise Exception('couldnt annotate bout start (bout number: {})'.format(index))

    # Select all licks that end a bout
    bout_ends = licks[licks['bout_end']]

    # Initialize 'bout_end' column in stimulus_presentations to False
    stimulus_presentations['bout_end'] = False
    # Initialize 'num_bout_end' column in stimulus_presentations to 0
    stimulus_presentations['num_bout_end'] = 0

    # Iterate through each bout end
    for index,x in bout_ends.iterrows():
        # Find all stimuli that started before this bout ended
        filter_end = stimulus_presentations.query('start_time < @x.timestamps')
        
        # If there are stimuli before this bout ended
        if len(filter_end) > 0:
            # Get the index of the last stimulus before the bout ended
            end_index = filter_end.index[-1]
            
            # Mark this stimulus as the end of a bout
            stimulus_presentations.at[end_index,'bout_end'] = True
            
            # Increment the number of bouts ending at this stimulus
            stimulus_presentations.at[end_index,'num_bout_end'] += 1   
        
        # If the bout ended before the first stimulus
        elif x.timestamps <= stimulus_presentations.iloc[0].start_time:
            # Mark the first stimulus as the end of a bout
            stimulus_presentations.at[0,'bout_end'] = True
            
            # Increment the number of bouts ending at the first stimulus
            stimulus_presentations.at[0,'num_bout_end'] += 1
        
        # If we couldn't annotate the bout end, raise an exception
        else:
            raise Exception('couldnt annotate bout end (bout number: {})'.format(index))

    # Annotate In-Bout: True if cumulative bout starts > cumulative bout ends
    # (Yes a very clever way!)
    stimulus_presentations['in_lick_bout'] = \
        stimulus_presentations['num_bout_start'].cumsum() > \
        stimulus_presentations['num_bout_end'].cumsum()

    # Shift in_lick_bout by 1, filling first value with False
    stimulus_presentations['in_lick_bout'] = \
        stimulus_presentations['in_lick_bout'].shift(fill_value=False)

    # Find overlapping cases where a stimulus is marked as in_lick_bout, bout_start, and has at least one bout end
    overlap_index = (stimulus_presentations['in_lick_bout']) &\
                    (stimulus_presentations['bout_start']) &\
                    (stimulus_presentations['num_bout_end'] >=1)

    # Set in_lick_bout to False for these overlapping cases
    stimulus_presentations.loc[overlap_index,'in_lick_bout'] = False

    # if this presentation is within, inclusively, a lick bout:
    stimulus_presentations['licked'] = stimulus_presentations['bout_start'] | stimulus_presentations['bout_end'] | stimulus_presentations['in_lick_bout']

    # Quality Control checks
    # Count total number of bout starts in stimulus_presentations
    num_bouts_sp_start = stimulus_presentations['num_bout_start'].sum()
    # Count total number of bout ends in stimulus_presentations
    num_bouts_sp_end = stimulus_presentations['num_bout_end'].sum()
    # Count total number of bout starts in licks table
    num_bouts_licks = licks.bout_start.sum()

    # Assert that bout starts in stimulus_presentations match bout starts in licks table
    assert num_bouts_sp_start == num_bouts_licks, \
        "Number of bouts doesnt match between licks table and stimulus table"

    # Assert that number of bout starts equals number of bout ends
    assert num_bouts_sp_start == num_bouts_sp_end, \
        "Mismatch between bout starts and bout ends"

    # Assert that all stimuli marked as bout_start have licks
    assert stimulus_presentations.query('bout_start')['licked'].all(),\
        "All licking bout start should have licks" 

    # Assert that all stimuli marked as bout_end have licks
    assert stimulus_presentations.query('bout_end')['licked'].all(),\
        "All licking bout ends should have licks" 

    # Assert that each stimulus either has no licks, is in a lick bout, or is a bout start
    assert np.all(stimulus_presentations['in_lick_bout'] |\
        stimulus_presentations['bout_start'] |\
        ~stimulus_presentations['licked']), \
        "must either not have licked, or be in lick bout, or bout start"

    # Assert that no stimulus is both in a lick bout and a bout start
    assert np.all(~(stimulus_presentations['in_lick_bout'] &\
        stimulus_presentations['bout_start'])),\
        "Cant be in a bout and a bout_start"
    
    return stimulus_presentations
    