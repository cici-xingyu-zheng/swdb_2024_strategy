## "Trails":

On each trial of the task, a change time is selected from a geometric distribution between 4 and 12 flashes after the time of the last change or the last lick. On “go” trials, the image identity will change at the selected change time. If the mouse licks within the **750 ms** response window, the trial is considered a `hit` and a reward is delivered. If the mouse fails to lick after the change, the trial is considered a `miss`. **If the mouse licks prior to the scheduled change time, the trial is aborted and starts over again**, using the same change time for up to 5 trials in a row. This is to discourage `false alarm` licks and help shape the behavior, by requiring that mice wait until the change time to respond and get a reward.

On “catch” trials, a change time is drawn but the image identity does not change. If the mouse licks within the reward window following the sham change, the trial is considered a false alarm and no reward is delivered. Correctly witholding a lick on a catch trial is a `correct reject`. This definition of a catch trial is a conservative one, and only considers the non-change stimulus presentations that are drawn from the same distribution as the change times to be catch trials. A less restrictive definition could consider every non-change stimulus presentation as a catch. `aborted` trials can also be considered catch trials, as they represent false alarm licks prior to the scheduled change time.

On change trials, a `3 second` “grace period” occurs during which licking behavior does not influence the task flow, to allow time for mice to consume the reward. 

As a result of the above contingencies, the number of times a given image is shown is determined by two things:

- The distribution that the change times are drawn from
- Whether or not the mouse emits a false alarm lick before the image change is shown

Any false alarm licks (licks that occur outside of the 750 ms reward window and 3 second consumption window following an image change) will abort the trial and the same image will continue to be repeated for the designated number of presentations selected for that trial. As an example, if the change time drawn for a given trial is 8 flashes, and the mouse emits a false alarm lick after 4 flashes, the trial is aborted and the same image continues to be shown for 8 more flashes, giving a total of 16 image repetitions before a change will occur. This serves to discourage false alarms by requiring that mice withhold licking in order to see an image change and have an opportunity for a reward.

![Task Flow](https://allenswdb.github.io/_images/task_flow.png)

