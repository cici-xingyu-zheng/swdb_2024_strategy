## "Trails":

On each trial of the task, a change time is selected from a geometric distribution between 4 and 12 flashes after the time of the last change or the last lick. On “go” trials, the image identity will change at the selected change time. If the mouse licks within the **750 ms** response window, the trial is considered a `hit` and a reward is delivered. If the mouse fails to lick after the change, the trial is considered a `miss`. **If the mouse licks prior to the scheduled change time, the trial is aborted and starts over again**, using the same change time for up to 5 trials in a row. This is to discourage `false alarm` licks and help shape the behavior, by requiring that mice wait until the change time to respond and get a reward.

On “catch” trials, a change time is drawn but the image identity does not change. If the mouse licks within the reward window following the sham change, the trial is considered a false alarm and no reward is delivered. Correctly witholding a lick on a catch trial is a `correct reject`. This definition of a catch trial is a conservative one, and only considers the non-change stimulus presentations that are drawn from the same distribution as the change times to be catch trials. A less restrictive definition could consider every non-change stimulus presentation as a catch. `aborted` trials can also be considered catch trials, as they represent false alarm licks prior to the scheduled change time.

On change trials, a **3 second** “grace period” occurs during which licking behavior does not influence the task flow, to allow time for mice to consume the reward. 

As a result of the above contingencies, the number of times a given image is shown is determined by two things:

- The distribution that the change times are drawn from
- Whether or not the mouse emits a false alarm lick before the image change is shown

Any false alarm licks (licks that occur outside of the 750 ms reward window and 3 second consumption window following an image change) will abort the trial and the same image will continue to be repeated for the designated number of presentations selected for that trial. 

As an example, if the change time drawn for a given trial is 8 flashes, and the mouse emits a false alarm lick after 4 flashes, the trial is aborted and the same image continues to be shown for 8 more flashes, giving a total of 16 image repetitions before a change will occur. This serves to discourage false alarms by requiring that mice withhold licking in order to see an image change and have an opportunity for a reward.

![Task Flow](https://allenswdb.github.io/_images/task_flow.png)

Note: 3 second: 3*600/750 = 4 image flashes + grey screen.



## `behavior trials table`:

Every row corresponds to one trial of the change detection task. Here is a quick summary of the columns:

`start_time`: Experiment time when this trial began in seconds.

`end_time`: Experiment time when this trial ended.

`initial_image_name`: Indicates which image was shown before the change (or sham change) for this trial

`change_image_name`: Indicates which image was **scheduled** to be the change image for this trial. Note that if the trial is aborted, a new trial will begin before this change occurs.

`stimulus_change`: Indicates whether an image change occurred for this trial.

`change_time_no_display_delay`: Experiment time when the task-control computer commanded an image change. This change time is used to determine the response window during which a lick will trigger a reward. Note that due to display lag, this is not the time when the change image actually appears on the screen. To get this time, you need the stimulus_presentations table (more about this below).

`go`: Indicates whether this trial was a 'go' trial. To qualify as a go trial, an image change must occur and the trial cannot be autorewarded.

`catch`: Indicates whether this trial was a 'catch' trial. To qualify as a catch trial, a 'sham' change must occur during which the image identity does not change. These sham changes are drawn to match the timing distribution of real changes and can be used to calculate the false alarm rate.

`lick_times`: A list indicating when the behavioral control software recognized a lick. Note that this is not identical to the lick times from the licks dataframe, which record when the licks were registered by the lick sensor. The licks dataframe should generally be used for analysis of the licking behavior rather than these times. (okay interesting... then let's focus on this dataframe)

`response_time`: Indicates the time when the first lick was registered by the task control software for trials that were not aborted (go or catch). NaN for aborted trials. For a more accurate measure of response time, the licks dataframe should be used.

`reward_time`: Indicates when the reward command was triggered for hit trials. NaN for other trial types.

`reward_volume`: Indicates the volume of water dispensed as reward for this trial.

`hit`: Indicates whether this trial was a 'hit' trial. To qualify as a hit, the trial must be a go trial during which the stimulus changed and the mouse licked within the reward window (150-750 ms after the change time).

`false_alarm`: Indicates whether this trial was a 'false alarm' trial. To qualify as a false alarm, the trial must be a catch trial during which a sham change occurred and the mouse licked during the reward window.

`miss`: To qualify as a miss trial, the trial must be a go trial during which the stimulus changed but the mouse did not lick within the response window.

`correct_reject`: To qualify as a correct reject trial, the trial must be a catch trial during which a sham change occurred and the mouse withheld licking.

`aborted`: A trial is aborted when the mouse licks before the scheduled change or sham change.

`auto_rewarded`: During autorewarded trials, the reward is automatically triggered after the change regardless of whether the mouse licked within the response window. These always come at the beginning of the session to help engage the mouse in behavior.

`change_frame`: Indicates the stimulus frame index when the change (on go trials) or sham change (on catch trials) occurred. This column can be used to link the trials table with the stimulus presentations table, as shown below.

`trial_length`: Duration of the trial in seconds.

### `stimulus presentation table`

`active`: Boolean indicating when the change detection task (with the lick spout available to the mouse) was run. This should only be TRUE for block 0.

`stimulus_block`: Index of stimulus as described as:

- **block 0**: Change detection task. Natural images are flashed repeatedly and the mouse is rewarded for licking when the identity of the image changes. You can find more info about this task [here](http://portal.brain-map.org/explore/circuits/visual-behavior-neuropixels?edit&language=en). Also see [here](https://www.frontiersin.org/articles/10.3389/fnbeh.2020.00104/full) for info about our general training strategy.

- **block 1**: Brief gray screen

- **block 2**: Receptive field mapping. Gabor stimuli used for receptive field mapping. For more details on this stimulus consult [this notebook](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_receptive_fields.html).

- **block 3**: Longer gray screen

- **block 4**: Full-field flashes, shown at 80% contrast. Flashes can be black (color = -1) or white (color = 1).

- **block 5**: Passive replay. Frame-for-frame replay of the stimulus shown during the change detection task (block 0), but now with the lick spout retracted so the animal can no longer engage in the task.


`stimulus_name`: Indicates the stimulus category for this stimulus presentation.

`contrast`: Stimulus contrast as defined [here](https://www.psychopy.org/api/visual/gratingstim.html#psychopy.visual.GratingStim.contrast)

`duration`: Duration of stimulus in seconds

`start_time`: Experiment time when stimulus started. This value is corrected for display lag and therefore indicates when the stimulus actually appeared on the screen.

`end_time`: Experiment time when stimulus ended, also corrected for display lag.

`start_frame`: Stimulus frame index when this stimulus started. This can be used to sync this table to the behavior trials table, for which behavioral data is collected every frame.

`end_frame`: Stimulus frame index when this stimulus ended.

#### Change detection task and Passive replay (blocks 0 and 5)

`flashes_since_change`: Indicates how many flashes of the same image have occurred since the last stimulus change.

`image_name`: Indicates which natural image was flashed for this stimulus presentation. To see how to visualize this image, check out [this tutorial](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/visual_behavior_neuropixels_data_access.html).

`is_change`: Indicates whether the image identity changed for this stimulus presentation. When both this value and 'active' are TRUE, the mouse was rewarded for licking within the response window.

`omitted`: Indicates whether the image presentation was omitted for this flash. Most image flashes had a 5% probability of being omitted (producing a gray screen). Flashes immediately preceding a change or immediately following an omission could not be omitted.

`rewarded`: Indicates whether a reward was given after this image presentation. During the passive replay block (5), this value indicates that a reward was issued for the corresponding image presentation during the active behavior block (0). No rewards were given during passive replay.

#### Receptive field mapping gabor stimulus (block 2)

`orientation`: Orientation of gabor.

`position_x`: Position of the gabor along azimuth. The units are in degrees relative to the center of the screen (negative values are nasal).

`position_y`: Position of the gabor along elevation. Negative values are lower elevation.

`spatial_frequency`: Spatial frequency of gabor in cycles per degree.

`temporal_frequency`: Temporal frequency of gabor in Hz.

### Full field flashes (block 4)

`color`: Color of the full-field flash stimuli. "1" is white and "-1" is black.


## "lick bouts":
First, licks were segmented into licking bouts based on an inter-lick interval of 700 ms (Figure S2A). The duration of bouts was largely governed by whether the mouse received and then consumed a water reward (Figure S2B). Therefore, we focused our analysis on predicting the start of each bout. Bout onsets were time- locked to image presentations, thus for each bout we identified the last image or omission presented before the bout started (Figure S2C). Because our model predicts the start of bouts, we ignore images when the mouse was already in a bout.

__Choice of 700 ms__: Bimodal histogram of interval between successive licks (n = 936,136 licks from 382 imaging sessions). Dashed line indicates 700 ms threshold used to separate licks within the same licking bout (< 700ms) and licks in separate licking bout (> 700 ms).