***
## INFO

We document in this repo the progress of modeling and inferring lick behavior in the Allen Visual Behavior Neuropixel Dataset. 

This will be the behavior focused branch in the group project. 


### Data
- here I load from a local hard drive; 
- but one can be alternatively obtained from the cloud server (Amzn S3 bucket);
- noticed that I don't seem to be able to modify some session attributes, like the `stimulus_presentations` df

***

### Useful resourses

#### The experiment:

- [change_detetion_task](https://allenswdb.github.io/physiology/stimuli/visual-behavior/VB-Behavior.html#change-detection-task)


####  Alex Piet's work:
<!-- -[Licking Behavior Ecephys](https://github.com/AllenInstitute/licking_behavior_NP) -->


- [Licking Behavior Ophys](https://github.com/alexpiet/licking_behavior/tree/master)

Note that both repos use some internal/local load paths that are a bit hard to parse what they really are... we also have different permission to access files.

####  `psytrack` package:
- [psytrack repo](https://github.com/nicholas-roy/psytrack/blob/master/psytrack/examples/ExampleNotebook.ipynb)
- We have installed it;
- the example ran very smoothly; see the `/psytrack_example` folder

***

### Logistics:

| Time | Event |
|------|-------|
| Saturday Aug 24 10:00 – 12:00 | Project proposal presentations |
| Saturday Aug 21 9:00 – 12:00 | Project presentations |

***
## Log of progress

### 08/25/24

1. Get familiarized with `stim_table` and `trials` dataFrames. 
2. Ran the most basic inference for a ecephys session in a very quick dirty manner;

![first dirty fit](piet_modelfit/first_weights.png)

- ignored: 
    1. one defination QC check (`licked`, but the variable was undefined somehow);
    2. the regression model for timing should be re fitted; 
    3. the detailed logic of defining the `bouts`, which is probably why 1 occured;
    4. I didn't pay attention at all how the exact choice of `y`'s set up, not something I expected. 

#### TO-DOs: 
1. fix the ignored problems;
2. model evidence, CV, etc;
3. keep brainstorming new strategies; "regret" (the first false alarm lick) was an idea through talking to my roomate 
4. ways to get behaviral data direction without getting ecepyhs session? 
5. any ways to change file write permission? 
6. go through in more detail `psytrack`'s usage

### 08/26/24
Fixed the directly loading behaviral session issue;
Michael and Saskia said they don't recommending re-writing the attribute, and some files are fetched (?) which is fair;

#### General qestions: 
1. why we see `> 5` consecutive aborted trails? 
_Answer (from Marina):_  that is very likely; as the 5 trials specify the fixed number of frames, but after 5, same image will still be flashed 
![aborted](plots/explore/aborted_entire_session.pdf) 

2. is start of trail right after the change, or right after 3 sec grace period if hit trial?
![example trial](plots/explore/example_session_period.pdf)
_Answer (from Marina):_ no matter hit or miss, the mice will get a 4-flashes grace period; then the draw specify the # of frames from:
![the geometric dist](https://allenswdb.github.io/_images/change_time_trial_types.png)

3. clarification from Marina about the logic behind the timing strategy:
It more like serving the minimum wait time the mouse is oaky to bear, against it's lick urge, as 4 frames is the most frequent and also the least amount of time its willing to bear.

