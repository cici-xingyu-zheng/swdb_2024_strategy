import numpy as np
import psytrack as psy
import matplotlib.pyplot as plt
import src_local.utils as utils
import copy

from psytrack.helper.crossValidation import split_data
from psytrack.helper.crossValidation import xval_loglike

colors = {
        'bias':'dimgray',
        'omissions':'forestgreen',
        'omissions1':'orchid',
        'task':'tomato',
        'timing1D':'royalblue',
        'timingGeom':'teal'
        }

def fit_weights(psydata, strategy_list, fit_overnight=False):
    '''
        does weight and hyper-parameter optimization on the data in psydata
        Args: 
            psydata is a dictionary with key/values:
            psydata['y'] = a vector of no-licks (1) and licks(2) for each images
            psydata['inputs'] = a dictionary with each key an input 
                ('random','timing', 'task', etc) each value has a 2D array of 
                shape (N,M), where N is number of imagees, and M is 1 unless 
                you want to look at history/image interaction terms

        RETURNS:
            hypa: dictionary of the optimized hyperparameters
            evd: the approximate log-evidence of the optimized model
            wMode : the weight trajectories of the optimized model
            credibleInt: the posterior credible intervals on the weights, 
                under the key `W_std`, computed from inverse Hessian
            weights: names of the strategies
    '''
    # Set up number of regressors
    weights = {}
    for strat in strategy_list:
        weights[strat] = 1
    print(weights)
    K = np.sum([weights[i] for i in weights.keys()])

    # Set up initial hyperparameters
    hyper = {'sigInit': 2**4.,
            'sigma':[2**-4.]*K,
            'sigDay': 2**4}

    # Only used if we are fitting multiple sessions
    # where we have a different prior
    if fit_overnight:
        optList=['sigma','sigDay']
    else:
        optList=['sigma']
    
    # Do the fit
    hyp,evd,wMode,hess =psy.hyperOpt(psydata,hyper,weights, optList)
    credibleInt = hess['W_std']
    
    return hyp, evd, wMode, credibleInt, weights


def compute_ypred(psydata, wMode, weights):
    '''
        Makes a full model prediction from the wMode
        Returns:
        pR, the probability of licking on each image
        pR_each, the contribution of licking from each weight. These contributions 
            interact nonlinearly, so this is an approximation. 
    '''
    g = psy.read_input(psydata, weights)
    gw = g*wMode.T
    total_gw = np.sum(gw,axis=1)
    pR = transform(total_gw)
    pR_each = transform(gw) 
    return pR, pR_each

def transform(series):
    '''
        passes the series through the logistic function
    '''
    return 1/(1+np.exp(-(series)))


def plot_weights(wMode,weights,psydata,errorbar=None, ypred=None,START=0, END=0,
    plot_trials=True,session_labels=None, seedW = None,ypred_each = None,
    filename=None,smoothing_size=50):
    '''
        Plots the fit results by plotting the weights in linear and probability space. 
        wMode, the weights
        weights, the dictionary of strategyes
        psydata, the dataset
        errorbar, the std of the weights
        ypred, the full model prediction
        START, the image number to start on
        END, the image number to end on
     
    '''
    # Determine x axis limits
    K,N = wMode.shape    
    if START <0: START = 0
    if START > N: raise Exception(" START > N")
    if END <=0: END = N
    if END > N: END = N
    if START >= END: raise Exception("START >= END")

    # initialize 
    # weights_list = pgt.get_clean_string(get_weights_list(weights))
    weights_list =get_weights_list(weights)


    if 'dayLength' in psydata:
        dayLength = np.concatenate([[0],np.cumsum(psydata['dayLength'])])
    else:
        dayLength = []

    # Determine which panels to plot
    if (ypred is not None) & plot_trials:
        fig,ax = plt.subplots(nrows=4,ncols=1, figsize=(10,10))
        trial_ax = 2
        full_ax = 3
        
    elif plot_trials:
        fig,ax = plt.subplots(nrows=3,ncols=1, figsize=(10,8))  
        
        trial_ax = 2
    elif (ypred is not None):
        fig,ax = plt.subplots(nrows=3,ncols=1, figsize=(10,8))
        
        full_ax = 2
    else:
        fig,ax = plt.subplots(nrows=2,ncols=1, figsize=(10,6))
        

    # Axis 0, plot weights
    for i,weight in enumerate(weights_list):

        ax[0].plot(wMode[i,:], linestyle="-", lw=3, color=colors[weight],
            label=weights_list[i])        
        ax[0].fill_between(np.arange(len(wMode[i])), wMode[i,:]-2*errorbar[i], 
            wMode[i,:]+2*errorbar[i],facecolor=colors[weight], alpha=0.1)    
        if seedW is not None:
            ax[0].plot(seedW[i,:], linestyle="--", lw=2, color=colors[weight], 
                label= "seed "+weights_list[i])
    ax[0].plot([0,np.shape(wMode)[1]], [0,0], 'k--',alpha=0.2)
    ax[0].set_ylabel('Weight',fontsize=12)
    ax[0].set_xlabel('Image #',fontsize=12)
    ax[0].set_xlim(START,END)
    ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[0].tick_params(axis='both',labelsize=12)
    for i in np.arange(0, len(dayLength)-1):
        ax[0].axvline(dayLength[i],color='k',alpha=0.2)
        if session_labels is not None:
            ax[0].text(dayLength[i],ax[0].get_ylim()[1], session_labels[i],rotation=25)

    # Axis 1, plot nonlinear weights (approximation)
    for i, weight in enumerate(weights_list):
        ax[1].plot(transform(wMode[i,:]), linestyle="-", lw=3, color=colors[weight],
            label=weights_list[i])
        ax[1].fill_between(np.arange(len(wMode[i])),transform(wMode[i,:]-2*errorbar[i]),
            transform(wMode[i,:]+2*errorbar[i]),facecolor=colors[weight], alpha=0.1)             
        if seedW is not None:
            ax[1].plot(transform(seedW[i,:]), linestyle="--", lw=2, color=colors[weight],
                label= "seed "+weights_list[i])
    ax[1].set_ylim(0,1)
    ax[1].set_ylabel('Lick Prob',fontsize=12)
    ax[1].set_xlabel('Image #',fontsize=12)
    ax[1].set_xlim(START,END)
    ax[1].tick_params(axis='both',labelsize=12)
    for i in np.arange(0, len(dayLength)-1):
        ax[1].plot([dayLength[i], dayLength[i]],[0,1], 'k-',alpha=0.2)

    # scatter plot of trials
    if plot_trials:
        jitter = 0.025   
        for i in np.arange(0, len(psydata['hits'])):
            if psydata['hits'][i]:
                ax[2].plot(i, 1+np.random.randn()*jitter, 'bo',alpha=0.2)
            elif psydata['misses'][i]:
                ax[2].plot(i, 2+np.random.randn()*jitter, 'ro',alpha = 0.2)   
            elif psydata['aborts'][i]:
                ax[2].plot(i, 3+np.random.randn()*jitter, 'ko',alpha=0.2)  
   
        ax[2].set_ylim([0,4]) 
        ax[2].set_yticks([1,2,3])
        ax[2].set_yticklabels(['hits','miss','abort'],
            fontdict={'fontsize':12})
        ax[2].set_xlim(START,END)
        ax[2].set_xlabel('Image #',fontsize=12)
        ax[2].tick_params(axis='both',labelsize=12)

    # Plot Full Model prediction and comparison with data
    if (ypred is not None):
        ax[full_ax].plot(utils.moving_mean(ypred,smoothing_size), 'k',alpha=0.3,
            label='Full Model (n='+str(smoothing_size)+ ')')
        if ypred_each is not None:
            for i in np.arange(0, len(weights_list)):
                ax[full_ax].plot(ypred_each[:,i], linestyle="-", lw=3, 
                    alpha = 0.3,color=colors[i],label=weights_list[i])        
        ax[full_ax].plot(utils.moving_mean(psydata['y']-1,smoothing_size), 'b',
            alpha=0.5,label='data (n='+str(smoothing_size)+ ')')
        ax[full_ax].set_ylim(0,1)
        ax[full_ax].set_ylabel('Lick Prob',fontsize=12)
        ax[full_ax].set_xlabel('Image #',fontsize=12)
        ax[full_ax].set_xlim(START,END)
        ax[full_ax].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax[full_ax].tick_params(axis='both',labelsize=12)
   
    # Save
    plt.tight_layout()
    if filename is not None:
        plt.savefig(filename+"_weights.png")

def get_weights_list(weights):
    '''
    Return a sorted list of the weights in the model
    '''
    weights_list = []
    for i in sorted(weights.keys()):
        weights_list += [i] * weights[i]
    return weights_list 


def compute_cross_validation(psydata, hyp, weights,folds=10):
    '''
        Computes Cross Validation for the data given the regressors as 
        defined in hyp and weights
    '''
    trainDs, testDs = split_data(psydata,F=folds)
    test_results = []
    for k in range(folds):
        print("\rrunning fold " +str(k),end="") 
        _,_,wMode_K,_ = psy.hyperOpt(trainDs[k], hyp, weights, ['sigma'],hess_calc=None)
        logli, gw = xval_loglike(testDs[k], wMode_K, trainDs[k]['missing_trials'], 
            weights)
        res = {'logli' : np.sum(logli), 'gw' : gw, 'test_inds' : testDs[k]['test_inds']}
        test_results += [res]
   
    print("") 
    return test_results

def compute_cross_validation_ypred(psydata,test_results,ypred):
    '''
        Computes the predicted outputs from cross validation results by stitching 
        together the predictions from each folds test set

        full_pred is a vector of probabilities (0,1) for each time bin in psydata
    '''
    # combine each folds predictions
    myrange = np.arange(0, len(psydata['y']))
    xval_mask = np.ones(len(myrange)).astype(bool)
    X = np.array([i['gw'] for i in test_results]).flatten()
    test_inds = np.array([i['test_inds'] for i in test_results]).flatten()
    inrange = np.where((test_inds >= 0) & (test_inds < len(psydata['y'])))[0]
    inds = [i for i in np.argsort(test_inds) if i in inrange]
    X = X[inds]
    cv_pred = 1/(1+np.exp(-X))

    # Fill in untested indicies with ypred, these come from end
    full_pred = copy.copy(ypred)
    full_pred[np.where(xval_mask==True)[0]] = cv_pred
    return full_pred