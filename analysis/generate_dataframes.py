"""This file gets dataframes from mongoDB and saves them in the corresponding locations. The data that is pulled from mongoDB is—at least in the hardcoded iterations—the data that was used in the NeurIPS 2021 submission. Make sure to run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` to set up the mongoDB connection as well as provide auth.txt in the same folder as this file."""

import os
import sys
import argparse

os.getcwd()
sys.path.append("..")
sys.path.append("../utils")
sys.path.append("../analysis/utils")

import numpy as np
import scipy.stats as stats
import pandas as pd

import pymongo as pm

from tqdm import tqdm

from analysis_helpers import apply_exclusion_criteria, basic_preprocessing

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

REPO = 'cognitive-ai-benchmarking'

#helper function for pd.agg
def item(x):
    """Returns representative single item"""
    return x.tail(1).item()

# set up directories
## directory & file hierarchy
# get path of this file
current_dir = os.path.dirname(os.path.abspath(__file__))
while current_dir != '/':
    try:
        if REPO in os.listdir(current_dir):
            proj_dir = os.path.join(current_dir, REPO)
            break
        else:
            current_dir = os.path.dirname(current_dir)
    except:
        print("Could not find cognitive-AI-benchmarking repo. Please make sure it is in the a parent directory as this repo under the name `cognitive-AI-benchmarking`. Edit this file if you want to change the name of the repo.")
        sys.exit()
if current_dir == '/': 
    print("Could not find cognitive-AI-benchmarking repo. Please make sure it is in the a parent directory as this repo under the name `cognitive-AI-benchmarking`. Edit this file if you want to change the name of the repo.")
    sys.exit()

## add helpers to python path

results_dir = os.path.join(proj_dir, 'results')
csv_dir = os.path.join(proj_dir, 'csv')

if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)       
    
## add helpers to python path
sys.path.append(proj_dir)

if os.path.join(proj_dir,'utils') not in sys.path:
    sys.path.append(os.path.join(proj_dir,'utils'))   

if os.path.join(proj_dir,'stimuli') not in sys.path:
    sys.path.append(os.path.join(proj_dir,'stimuli'))   

# CAB imports
import cabutils
from stimuli.experiment_config import *

def make_dir_if_not_exists(dir_name):   
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def anonymize(subjID):
    '''
    import mapper dict from anonymize_mapper.py (ignored in github repo)
    apply to anonymize prolific IDs
    '''
    try:
        from anonymize_mapper import mapper
    except:
        print('ERROR: You need the anonymize_mapper file in order to generate anonymized results.')
        sys.exit()
    return ''.join([mapper[char] for char in list(subjID)])

## create directories that don't already exist        
result = [make_dir_if_not_exists(x) for x in [results_dir,csv_dir]]

# have to fix this to be able to analyze from local
import pymongo as pm
try:
    conn = get_db_connection()
    print('Connected to database.')
except:
    print('Could not connect to database. Try to set up ssh bridge to write to mongodb. Insert your username. If you dont have an SSH secret set yet, run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` in your shell.')
    sys.exit()

def get_dfs_from_mongo(project, dataset, task, iteration, anonymizeIDs=True):
    """Get's and saves the given iteration from the mongoDB. Writes out two dataframes."""
    df_trial_entries, df_familiarization_entries = pull_dataframes_from_mongo(project, dataset, task, iteration, anonymizeIDs)

    # save out df_trials_entries
    df_trial_entries.to_csv(os.path.join(csv_dir,"human_responses_{}_{}_{}.csv".format(project, dataset++task, iteration)))
    # save out df_famili arizations_entries
    df_familiarization_entries.to_csv(os.path.join(csv_dir,"familiarization_human_responses_{}_{}_{}.csv".format(project, dataset++task, iteration)))

    #generate per stim aggregated df
    df_trial_entries['c'] = 1 #add dummy variable for count in agg
    per_stim_agg = df_trial_entries.groupby('stim_ID').agg({
        'correct' : lambda cs: np.mean([1 if c == True else 0 for c in cs]),
        'c' : 'count',
    })
    #save
    per_stim_agg.to_csv(os.path.join(csv_dir,"human_accuracy_{}_{}_{}.csv".format(project, dataset++task, iteration)))
    return

def pull_dataframes_from_mongo(project, dataset, task, iteration, anonymizeIDs=True, raw_data=False):
    """Gets dataframes from mongo and returns both the experimental and the familiarization trials"""
    # connect to database
    experiment = dataset+'_'+task
    db = conn[project+'_output']
    coll = db[experiment]
    stim_db = conn[project+'_input']
    stim_coll = stim_db[experiment]

    print('Reading from {}_output.{} and {}_input.{}'.format(project, experiment, project, experiment))
    print('Reading iteration {}'.format(iteration))
    print("This might take a while...")
    # get dataframe of served stims
    stim_df = pd.DataFrame(stim_coll.find({}))
    stim_df.set_index('_id')
    df = coll.find({
            'iterationName': iteration,
            # 'prolificID': {'$exists' : True},
            'studyID': {'$exists' : True},
            'sessionID': {'$exists' : True},
    })
    df = pd.DataFrame(df)
    
    assert len(df)>0, "df from mongo empty"

    print("Got {} rows from the database".format(len(df)))
    if raw_data: print("Returning raw data")

    pID_count = df['prolificID'].nunique()
    if not raw_data:
        df = fill_ProlificIDs(df)
        if df['prolificID'].nunique() > pID_count: print("Filled {} Prolific IDs from manually recorded ones".format(df['prolificID'].nunique() - pID_count))
        # Which gameids have completed all trials that were served to them? 
        # Note that this will also exclude complete trials whose games aren't in the stim database anymore (ie if it has been dropped)

    complete_gameids = []
    for gameid in tqdm(df['gameID'].unique()):
        # if participants have given a sex, they have completed the experiment
        # TODO generalize this to other tasks
        try:
            responses = df[df['gameID'] == gameid]['responses']
            for response in list(responses):
                try:
                    if 'participantSex' in response:
                        complete_gameids.append(gameid)
                        break
                except TypeError as e:
                    pass
        except KeyError as e:
            if len(df[df['gameID'] == gameid]) > 10:
                print("No response field for gameID",gameid)
            continue
        #get the corresponding games
        # served_stim_ID = None
        # for stims_ID in stim_df.index:
        #     try:
        #         if gameid in stim_df.iloc[stims_ID]['games']:
        #             #great, we found our corresponding stim_ID
        #             served_stim_ID = stims_ID
        #     except TypeError as e:
        #         print("No games listed for",stims_ID)
        #         continue
        # if served_stim_ID == None:
        #     #we haven't found the stim_ID
        #     print("No recorded entry for game_ID in stimulus database:",gameid)
        #     continue
        # served_stims = stim_df.at[served_stim_ID,'stims']
        # #let's check if we can find an entry for each stim
        # found_empty = False
        # for stim_ID in [s['stimulus_name'] for s in served_stims.values()]:
        #     #check if we have an entry for that stimulus
        #     if len(df.query("gameID == '"+gameid+"' & stimulus_name == '"+stim_ID+"'")) == 0:
        #         found_empty = True
        #         break
        # if not found_empty: complete_gameids.append(gameid)
    
    # add scenario name
    df['scenarioName'] = dataset

    if not raw_data:
    # apply basic preprocessing
        df = basic_preprocessing(df)
        # apply exclusion criteria
        df = apply_exclusion_criteria(df,verbose=True) # should automatically pull familiarization trials from full dataframe

    #mark unfinished entries
    if not raw_data:
        df['complete_experiment'] = df['gameID'].isin(complete_gameids) 
        # # we only consider the first 100 gameIDs
        # complete_gameids = complete_gameids[:100]       
        #exclude unfinished games ⚠️
        old_n_IDs = df['gameID'].nunique()
        df = df[df['gameID'].isin(complete_gameids)]
        print("Excluded {} unfinished games".format(old_n_IDs - df['gameID'].nunique()))
    #Generate some useful views
    df_trial_entries = df[(df['condition'] == 'prediction') & (df['trial_type'] == 'video-overlay-button-response')] #only experimental trials
    df_trial_entries = df_trial_entries.assign(study=[experiment]*len(df_trial_entries), axis=0)
    df_familiarization_entries = df[(df['condition'] == 'familiarization_prediction') & (df['trial_type'] == 'video-overlay-button-response')] #only experimental fam trials
    df_familiarization_entries = df_familiarization_entries.assign(study=[experiment]*len(df_familiarization_entries), axis=0)
    if not set(df_trial_entries.gameID.unique()) == set(df_familiarization_entries.gameID.unique()):
        print("GameIDs in trial and familiarization entries don't match")
        print("IDs in familiarization, not in trials:",set(df_familiarization_entries.gameID.unique()) - set(df_trial_entries.gameID.unique()))
        print("IDs in trials, not in familiarization:",set(df_trial_entries.gameID.unique()) - set(df_familiarization_entries.gameID.unique()))
    
    # apply anonymization
    if anonymizeIDs==True:    
        print('Anonymizing prolificIDs')
        df_trial_entries = df_trial_entries.assign(prolificIDAnon = df_trial_entries['prolificID'].apply(lambda x: anonymize(x)), axis=0)
        df_trial_entries.drop(labels=['prolificID'],axis=1, inplace=True)
        df_familiarization_entries = df_familiarization_entries.assign(prolificIDAnon = df_familiarization_entries['prolificID'].apply(lambda x: anonymize(x)), axis=0)
        df_familiarization_entries.drop(labels=['prolificID'],axis=1, inplace=True)
    return df_trial_entries,df_familiarization_entries

def fill_ProlificIDs(df):
    """A bug in Prolific can prevent the URL fields from being served out. This tries to recreate them from the field."""
    for game_id in tqdm(df['gameID'].unique()):
        m = df['gameID'] == game_id
        if set(df[m]['prolificID'].unique()) == set([None]):
            # no prolific ID recorded. Can we recover it?
            responses = df[m]['responses'].dropna()
            pID = df[m]['prolificID'].unique()[0] # default value is None
            for r in responses:
                if "manual_prolificID" in r:
                    try:
                        r = eval(r) # really bad idea to run eval on data from participants TODO make safe
                    except:
                        continue
                    pID = r['manual_prolificID']
            df.loc[m,'prolificID'] = pID
    return df

if __name__ == "__main__":
    # DEBUG
    PROJECT = "Physion_V1_5" 
    DATASET = "Dominoes"
    TASK = "OCP"
    ITERATION = "pilot_1"
    EXPERIMENT = DATASET + "_" + TASK
    pull_dataframes_from_mongo(PROJECT, DATASET, TASK, ITERATION, anonymizeIDs=False)
    # /DEBUG
    # parse for pull_dataframes_from_mongo
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project name (eg. Physion_V1_5)")
    parser.add_argument("dataset", help="Dataset name (eg. Dominoes)")
    parser.add_argument("task", help="Task name (eg. OCP)")
    parser.add_argument("iteration", help="Iteration name (eg. pilot_1)")
    parser.add_argument("--outputPath", default=csv_dir, help="Path to save output to", required=False)
    parser.add_argument("--anonymizeIDs", default=False, help="Whether to anonymize prolificIDs", required=False)
    args = parser.parse_args()

    # get data
    df_trial_entries,df_familiarization_entries = pull_dataframes_from_mongo(args.project, args.dataset, args.task, args.iteration, anonymizeIDs=args.anonymizeIDs)
    
    # save data
    filename = "{}_{}_{}_{}".format(args.project, args.dataset, args.task, args.iteration)
    df_trial_entries.to_csv(args.outputPath + '/' + filename + '.csv')
    df_familiarization_entries.to_csv(args.outputPath + '/' + filename + '_familiarization.csv')
    print("Saved to",args.outputPath + '/' + filename + '.csv and ' + args.outputPath + '/' + filename + '_familiarization.csv')
    
