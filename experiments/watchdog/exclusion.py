import numpy as np
import pandas as pd

"""Exclusion/flagging criteria"""

def get_main_trials(df):
    """return a dataframe of rows only corresponding to the main trials"""
    return df[(df['trial_type'] == "video-overlay-button-response") & (df['condition'] == 'rating')]

def pre_exclusion(df):
    """Performs exclusion to get rid of non-prolific rows, rows that are missing gameIDs, etc."""
    old_len = len(df)
    df = df[~df['gameID'].isna()]
    new_len = len(df)
    if new_len < old_len:
        print("Dropped %d rows due to missing gameID" % (old_len-new_len))
    df = df[~df['prolificID'].isna()]
    if len(df) < new_len:
        print("Dropped %d rows due to missing prolificID" % (new_len-len(df)))
    return pd.DataFrame(df)

def exclude_games(game,full_df):
    """Returns a list of reasons why a game might be excluded. If empty list, game is not excluded.
    Pass game df and full df."""
    reasons = []
    assert game['gameID'].nunique() == 1,"more than one game passed in"
    assert len(game)>0, "empty game df passed. Don't run exclusion more than once!"
    
    # unfinished
    ## if we have data on participant's sex, they've finished
    if not np.any(['participantSex' in str(r) for r in list(game['responses'])]):
        reasons.append("unfinished")
    
    # not_prolific
    ## exclude responses that didn't come from prolific
    if np.all([s in [None,np.nan] for s in list(game['prolificID'])]): 
        reasons.append("not_prolific")

    # no_responses
    responses = get_main_trials(game)['response']
    if len(responses) == 0:
        reasons.append("no_responses")
        return reasons # no need to do the later criteria        
        
    # singular_responses
    ## more than 80% of responses of one kind
    if max(responses.value_counts())/responses.count() > 0.8:
        reasons.append("singular_responses")
        
    # no_extreme_responses
    ## no 1 or 5 in responses?
    if not ('1' in list(responses) and '5' in list(responses)):
        reasons.append("no_extreme_response")
        
    # mean_rt
    ## the mean log-transformed response time for that participant is 3 standard deviations above the median log-transformed response time across all participants for that scenario
    all_rt_mean = np.mean(np.log(get_main_trials(full_df)['rt']))
    all_rt_std = np.std(np.log(get_main_trials(full_df)['rt']))
    rt_mean = np.mean(np.log(get_main_trials(game)['rt']))
    if rt_mean > all_rt_mean + 3*all_rt_std:
        reasons.append("mean_rt")
        
    # comprehension_check
    if np.any(list(game['comprehension_check_failed'].dropna())):
        reasons.append("comprehension_check")
    
    return reasons