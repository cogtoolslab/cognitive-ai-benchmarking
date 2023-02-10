"""This file gets dataframes from mongoDB and saves them in the corresponding locations. The data that is pulled from mongoDB is—at least in the hardcoded iterations—the data that was used in the NeurIPS 2021 submission. Make sure to run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` to set up the mongoDB connection as well as provide auth.txt in the same folder as this file."""

import os
import sys

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

#helper function for pd.agg
def item(x):
    """Returns representative single item"""
    return x.tail(1).item()

# set up directories
## directory & file hierarchy
try:
    proj_dir = str(os.path.abspath(__file__)).split('physics-benchmarking-neurips2021')[0]+'physics-benchmarking-neurips2021'
except:
    print("ERROR: this script needs to be located in the human-physics-benchmarking folder")
analysis_dir =  os.path.join(proj_dir,'analysis')
results_dir = os.path.join(proj_dir,'results')
csv_dir = os.path.join(results_dir,'csv/humans')

## add helpers to python path
if os.path.join(proj_dir,'stimuli') not in sys.path:
    sys.path.append(os.path.join(proj_dir,'stimuli'))
    
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)       
    
## add helpers to python path
if os.path.join(proj_dir,'utils') not in sys.path:
    sys.path.append(os.path.join(proj_dir,'utils'))   

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

# set vars 
try:
    auth = pd.read_csv(os.path.join(analysis_dir,'auth.txt'), header = None) # this auth.txt file contains the password for the sketchloop user. Place in repo folder
except: 
    print('ERROR: Before you can generate dataframes, please make sure you have the auth.txt file with mongodb credentials.')
    sys.exit()

pswd = auth.values[0][0]
user = 'sketchloop'
host = 'cogtoolslab.org'

# do we want to anonymize prolific IDs?
anonymizeIDs=True

# have to fix this to be able to analyze from local
import pymongo as pm
try:
    conn = pm.MongoClient('mongodb://sketchloop:' + pswd + '@127.0.0.1')
except:
    print('Could not connect to database. Try to set up ssh bridge to write to mongodb. Insert your username. If you dont have an SSH secret set yet, run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` in your shell.')
    sys.exit()

neurips2021_iterations = [
    {'study' : "dominoes_pilot",
    'bucket_name' : 'human-physics-benchmarking-dominoes-pilot',
    'stim_version' : 'production_1',
    'iterationName' : 'production_1_testing'},
    {'study' : "collision_pilot",
    'bucket_name' : 'human-physics-benchmarking-collision-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "towers_pilot",
    'bucket_name' : 'human-physics-benchmarking-towers-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "linking_pilot",
    'bucket_name' : 'human-physics-benchmarking-linking-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "containment_pilot",
    'bucket_name' : 'human-physics-benchmarking-containment-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "rollingsliding_pilot",
    'bucket_name' : 'human-physics-benchmarking-rollingsliding-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "drop_pilot",
    'bucket_name' : 'human-physics-benchmarking-drop-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
    {'study' : "clothiness_pilot",
    'bucket_name' : 'human-physics-benchmarking-clothiness-pilot',
    'stim_version' : 'production_2',
    'iterationName' : 'production_2_testing'},
]

def get_dfs_from_mongo(study,bucket_name,stim_version,iterationName):
    """Get's and saves the given iteration from the mongoDB. Writes out two dataframes."""
    df_trial_entries, df_familiarization_entries = pull_dataframes_from_mongo(study, bucket_name, stim_version, iterationName)

    # save out df_trials_entries
    df_trial_entries.to_csv(os.path.join(csv_dir,"human_responses-{}-{}.csv".format(study,iterationName)))
    # save out df_famili arizations_entries
    df_familiarization_entries.to_csv(os.path.join(csv_dir,"familiarization_human_responses-{}-{}.csv".format(study,iterationName)))

    #generate per stim aggregated df
    df_trial_entries['c'] = 1 #add dummy variable for count in agg
    per_stim_agg = df_trial_entries.groupby('stim_ID').agg({
        'correct' : lambda cs: np.mean([1 if c == True else 0 for c in cs]),
        'c' : 'count',
    })
    #save
    per_stim_agg.to_csv(os.path.join(csv_dir,"human_accuracy-{}-{}.csv".format(study,iterationName)))
    return


def pull_dataframes_from_mongo(study, bucket_name, stim_version, iterationName, database_name='human_physics_benchmarking'):
    """Gets dataframes from mongo and returns both the experimental and the familiarization trials"""
    # connect to database
    db = conn[database_name]
    coll = db[study]
    stim_db = conn['stimuli']
    stim_coll = stim_db[bucket_name+'_'+stim_version]

    # get dataframe of served stims
    stim_df = pd.DataFrame(stim_coll.find({}))
    stim_df.set_index('_id')
    df = coll.find({
            'iterationName':iterationName,
            'prolificID': {'$exists' : True},
            'studyID': {'$exists' : True},
            'sessionID': {'$exists' : True},
    })
    df = pd.DataFrame(df)
    
    assert len(df)>0, "df from mongo empty"

    #Which gameids have completed all trials that were served to them? 
    #Note that this will also exclude complete trials whose games aren't in the stim database anymore (ie if it has been dropped)
    complete_gameids = []
    for gameid in tqdm(df['gameID'].unique()):
        #get the corresponding games
        served_stim_ID = None
        for stims_ID in stim_df.index:
            try:
                if gameid in stim_df.iloc[stims_ID]['games']:
                    #great, we found our corresponding stim_ID
                    served_stim_ID = stims_ID
            except TypeError as e:
    #             print("No games listed for",stims_ID)
                    pass
        if served_stim_ID == None:
            #we haven't found the stim_ID
            print("No recorded entry for game_ID in stimulus database:",gameid)
            continue
        served_stims = stim_df.at[served_stim_ID,'stims']
        #let's check if we can find an entry for each stim
        found_empty = False
        for stim_ID in [s['stim_ID'] for s in served_stims.values()]:
            #check if we have an entry for that stimulus
            if len(df.query("gameID == '"+gameid+"' & stim_ID == '"+stim_ID+"'")) == 0:
                found_empty = True
                break
        if not found_empty: complete_gameids.append(gameid)
    
    # add scenario name
    df['scenarioName'] = study.split('_')[0]

    # apply basic preprocessing
    df = basic_preprocessing(df)

    # apply exclusion criteria
    df = apply_exclusion_criteria(df,verbose=True) # should automatically pull familiarization trials from full dataframe

    #mark unfinished entries
    df['complete_experiment'] = df['gameID'].isin(complete_gameids) 
    # # we only consider the first 100 gameIDs
    # complete_gameids = complete_gameids[:100]       
    #exclude unfinished games ⚠️
    df = df[df['gameID'].isin(complete_gameids)]
    #Generate some useful views
    df_trial_entries = df[(df['condition'] == 'prediction') & (df['trial_type'] == 'video-overlay-button-response')] #only experimental trials
    df_trial_entries = df_trial_entries.assign(study=[study]*len(df_trial_entries), axis=0)
    df_familiarization_entries = df[(df['condition'] == 'familiarization_prediction') & (df['trial_type'] == 'video-overlay-button-response')] #only experimental fam trials
    df_familiarization_entries = df_familiarization_entries.assign(study=[study]*len(df_familiarization_entries), axis=0)
    
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
    
