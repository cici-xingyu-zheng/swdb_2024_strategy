
# Model related:

(From Roy et al 2018a)


## S1 Variable standardization, model selection, and non-identifiability


__Standard transformation needed:__ It is important that the variables used in g are standardized such that the magnitudes of different weights are comparable. 

For continuous variables (Stimuli A & B), we normalize the values such that they reflect a standard normal distribution. (i.e., subtract the mean and divide by the standard deviation). 

For categorical variables (previous answer, history, reward dependencies), we constrain values to be {-1, 0, +1}.

Specifically, the __answer variable__ is coded as a -1 if the correct answer on the previous trial was left, +1 if right; __the choice variable__ is -1 if the animal’s choice on the previous trial was left, +1 if right; and __the reward variable__ is -1 if a reward was not received on the previous trial, +1 if a reward was received. For these variables depending on the previous trial, they are set to 0 if the previous trial was a mistrial. Mistrials (instances where the animal did not complete the trial, e.g., by breaking center fixation before the end of the trial) are otherwise omitted from the analysis. The choice bias is fixed to be a constant +1.

The decision as to what variables to include when modeling a particular data set can be determined solely using the log-evidence — the model with the highest log-evidence is considered to be best (though this comparison could also be swapped with a more expensive comparison of cross-validated log-likelihood, see Sec. S4 and Fig. S1). Unfortunately, there is no way to make this comparison between models without first running a model with every combination of variables and choosing after the fact. However, the fitting can be parallelized across models (i.e., with 3 optional history variables, there are 8 possible models, which can each be fit in parallel).

Finally, we address a concern about __non-identifiability in our model__. This occurs __if one variable is a linear combination of some subset of other variables__, in which case there are many weight values that all correspond to a single identical model. Fortunately, the posterior confidence intervals discussed in Sec. S2 will indicate that a model is in a non- identifiable regime — since the weights can take a wide range of values to represent the same model, the confidence intervals will be very large on the weights creating the non-identifiability.

## S2 Calculation of posterior credible intervals (haven't read but will revisit)

In order to estimate the extent to which our recovered weights wMAP are constrained by the data, we adapted a fast method for inverting block-tridiagonal matrices to calculate central blocks of the inverse of our (extremely large) Hessian, providing a Gaussian approximate marginal posterior over the time-varying weight trajectories (as shown in Fig. 3). The algorithm is taken from Appendix B of [S2] which discusses calculating the diagonal elements of the inverse of a tridiagonal matrix, then describes how the approach can be generalized to block-tridiagonal matrices. The algorithm requires order NK3 scalar operations for calculating the central blocks of our inverse Hessian. If H is the Hessian matrix of our weights corresponding to the model with the highest log-evidence (returned at the end of the optimization procedure outlined in Algorithm1 in the main text), then this calculation yields:

$A = diag(H^{-1})$ (S1)

Using the diagonal of the inverse Hessian, we can take pA to estimate a one standard deviation interval on either side of each weight on every trial. By using two standard deviations, we approximate the 95% posterior credible interval shown throughout the paper.


(from Piet 2024)

## "Strategy Index":

__Visual index__: The absolute value of the percentage change in model evidence after removing the visual strategy
__Timing index__: The absolute value of the percentage change in model evidence after removing the timing strategy

The __strategy index__ is then defined as the difference between the visual index and the timing index:

Strategy index = Visual index - Timing index

A positive strategy index indicates the session was better described by the visual strategy, while a negative strategy index indicates the session was better described by the timing strategy.

## AUROC:
Forgot how exactly this is calculated; will come back to this.