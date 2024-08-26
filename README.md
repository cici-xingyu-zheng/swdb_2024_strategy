## Info

We document in this repo the progress of modeling and inferring lick behavior in the Allen Visual Behavior Neuropixel Dataset.

### Data
- here we load from a local hard drive; 
- but can be alternatively obtained from the cloud server (Amzn S3 bucket)

### Useful resourses

#### The experiment:

- [change_detetion_task](https://allenswdb.github.io/physiology/stimuli/visual-behavior/VB-Behavior.html#change-detection-task)


####  Alex Piet's work:
1.  [Licking Behavior Ecephys](https://github.com/AllenInstitute/licking_behavior_NP)
2.  [Licking Behavior Ophys](https://github.com/alexpiet/licking_behavior/tree/master)

Note that both use some internal/local load paths that are a bit hard to parse what they really are.

####  `psytrack` package:
- [repo](https://github.com/nicholas-roy/psytrack/blob/master/psytrack/examples/ExampleNotebook.ipynb)
- We have installed it; the example ran very smoothly in `/psytrack_example` folder

### Logistics:

| Time | Event |
|------|-------|
| Saturday 9:00 – 12:00 | Project presentations |

## Log of progress

### 08/25/24

1. Get familiarized with `stim_table` and `trials` dataFrames. 
2. Ran the most basic inference for a ecephys mouse in a very quick dirty manner;

![first dirty fit](piet_modelfit/first_weights.png)

- ignored: 
    1. one defination QC check (`licked`, but the variable was undefined somehow);
    2. the regression model for timing should be re fitted; 
    3. the detailed logic of defining the `bouts`, which is probably why 1 occured;

#### TO-DOs: 
1. fix the ignored problems;
2. model evidence, CV, etc;
3. keep brainstorming new strategies; "regret" (the first false alarm lick) was an idea through talking to my roomate 
4. ways to get behaviral data direction without getting ecepyhs session? 

#### General qestions: 
1. why we see `> 5` consecutive aborted trails?
![aborted](plots/explore/aborted_entire_session.pdf)

2. is start of trail right after the change, or right after 3 sec grace period if hit trial?
![example trial](plots/explore/example_session_period.pdf)

