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
7. plot inter lick interval as well!!! 

### 08/26/24

Fixed the directly loading behaviral session issue;
Michael and Saskia said they don't recommending re-writing the attribute, and some files are fetched (?) fair.. I don't understand everything but it doesn't affect us too much.

Will use compare cross-validated log-likelihood to compare across models; but why there's such a big difference between cv and whole model fit?

I ran into push issue but this helped (maybe loading sessions? but how come?)

```
git config http.postBuffer 524288000
```

#### A quick quick summary for how the Inference is set up (Roy 2018a):

Actually it's pretty smart; maybe it's just my first time seeing this time diff trick. All weights, concatinated, can be expressed as a function of eta, and thus gaussian (eta = DW, where D is a banded matrix calculating time differece). Then the log posterior \propto log evidence + log prior can be written out, and that has a sparse Hessian, and thus inference can use 2nd order method with sparse operation.

After getting wMAP, updated hyperparams by Laplace approximation, and then update log-evidence.
  
(Back to logging)
- I read the psytrack Roy 2021 paper, method and notebook, read the Roy 2018a NeurIPS paper [first pass, read the function docs];
- Went through the bout definition, plot inter-bout-interval; now I decide to focus on the `wt/wt` mice, plot their licks during H session. (_Correction:_ realize that I plotted for every one before I kill the kernel! so can continue to do it... and bin it...)

Visualize design matrix, for some frames in the example session:
![Xy](plots/explore/design_mat.png) 


#### TO-DOs:
1. How to tease different senario's licks apart?
    - ICI for only after a bout-ish lick! is it 4-5 flashes you'll wait for? will we see a shift?
    - ICI for only after the first abortion lick! will that be substentially longer?
    - plot distribution plot but not 
2. Compare model evidence
3. Email Alex

### 08/27/24

__Information from Andrew__: for `false alarm` trials, trials actualy continues but not early stopped! Licks would lead to no reward, and next one will be another drawn! I was very wrong about it

__Information from Yoni__: the hard drive DOES NOT contain: behavior session not realted to Ecephys! so for scale up plot I would need to use a capsule; or download it from S3.

```
if stand alone behavior:
    - go fetch it; 
if included in ecephys:
    - load it from the ecephys session
```

I fetched all `wt/wt` from `allensdk` following [totorial 1](https://allensdk.readthedocs.io/en/latest/visual_behavior_optical_physiology.html#tutorials) here.

Start migrating the code (to `src_local`) the meantime when my data is loading ... est: in 3 hrs, so by dinner, I will be setting up the system for bigger scale work.

Turn out that input must be either [1 or 2](https://github.com/nicholas-roy/psytrack/blob/master/psytrack/getMAP.py) or if 0 or 1 will be fixed; don't know why but fine

#### Some illustration for annotations (Alex's):
![anno](/plots/graphics/annot.png)



***

### General qestions: 
1. why we see `> 5` consecutive aborted trails? 

_Answer (from Marina):_  that is very likely; as the 5 trials specify the fixed number of frames, but after 5, same image will still be flashed 
![aborted](plots/explore/aborted_entire_session.png) 

2. is start of trail right after the change, or right after 3 sec grace period if hit trial?

![example trial](plots/explore/example_session_period.png)
_Answer (from Marina):_ no matter hit or miss, the mice will get a 4-flashes grace period; then the draw specify the # of frames from:
![the geometric dist](https://allenswdb.github.io/_images/change_time_trial_types.png)

3. clarification from Marina about the logic behind the timing strategy:

It more like serving the minimum wait time the mouse is oaky to bear, against it's lick urge, as 4 frames is the most frequent and also the least amount of time its willing to bear.

