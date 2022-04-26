import os, sys
import numpy as np
from PIL import Image
import pandas as pd
import json
import pymongo as pm
from glob import glob
from IPython.display import clear_output
import ast
import pandas as pd
import itertools
import random
import h5py
sys.path.append('..')
from cabutils import get_db_connection
from upload_to_s3 import get_filepaths


def load_metadata(meta_file):
    """
    load trial metadata
    
    params:
    meta_file: string, path to metadata file for dataset
    """
    with open(meta_file, 'rb') as f:
        trial_metas = json.load(f)
    M = pd.DataFrame(trial_metas).transpose()
    return M


def build_s3_url(M, s3_stim_paths, bucket):
    """
    add AWS S3 filepaths to metadata dataframe
    
    params:
    M_meta: pandas dataframe, metadata for experiment
    s3_stim_paths: list of strings, paths to stimuli on S3 bucket
    bucket: string, AWS S3 bucket name
    filenames: list of strings, AWS S3 filenames
    """
    
    base_pth = 'https://{}.s3.amazonaws.com/{}{}'
    for path in s3_stim_paths:
        stim_type = path.split('/')[0]
        suffix = path.split('/')[1][3:]
        M['{}_s3_path'.format(stim_type)] = [base_pth.format(bucket, x, suffix) 
                                             for x in M['stimulus_name']]
    return M


def get_familiarization_stimuli(M, fam_trial_ids):
    """
    identify familiarization stimuli and make familiarization trial dataframe
    
    params:
    M: main pandas dataframe
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    """
    M_fam = M[M['stimulus_name'].isin(fam_trial_ids)]
    trials_fam = M_fam.transpose().to_dict()
    trials_fam = {str(key):value for key, value in trials_fam.items()}
    assert len(M_fam) == len(M_fam['stimulus_name'].unique())
    # drop familiarization trials from main dataframe
    for f in M_fam['stimulus_name']:
        ind = M.index[M['stimulus_name']==f]
        M = M.drop(ind)
    trial_data = M.transpose().to_dict()
    trial_data = {str(key):value for key, value in trial_data.items()}
    return M, M_fam, trial_data, trials_fam


def split_stim_set_to_batches(bucket, batch_set_size, M, trial_data):
    """
    split full stimulus dataset into batches that will be shown to individual participants
    
    params:
    bucket: string, AWS S3 bucket name
    batch_set_size: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size
    """
    n_batches = int(len(M) / batch_set_size)
    M_sets = np.array_split(M.sample(frac=1), n_batches)
    ##################################################################
    # most experiments require experiment-specific counterbalancing
    # for this example we assign stimuli randomly to batches
    # experiment specific-counterbalancing should go in the loop below
    ##################################################################
    trial_data_sets = []
    for batch, M_set in enumerate(M_sets):
        assert len(M_set) == len(M_set['stimulus_name'].unique())
        # save json for each batch
        M_set.transpose().to_json('%s_trial_data_%d.json' % (bucket, batch))
        cur_dict = M_set.transpose().to_dict()
        trial_data_sets.append({str(key):value for key, value in trial_data.items()})
    return trial_data_sets
    
    
def make_familiarization_json(bucket, M):
    M.transpose().to_json('%s_familiarization_data.json' % bucket)
    

def upload_to_mongo(trial_data_sets, trials_fam):
    """
    upload batched experiment files to mongoDB
    """
    dataset_name = 'thomas_test'
    conn = get_db_connection()
    db = conn['experiment_files']
    coll = db[dataset_name]
    # get list of current collections
    sorted(db.list_collection_names())
    # drop collection if necessary. 
    db.drop_collection(dataset_name)
    # upload to mongo
    for batch in range(len(trial_data_sets)):
        coll.insert_one({'stim': trial_data_sets[batch],
                        'familiarization_trials': trials_fam})
    print('Done inserting records into mongo! The collection name is',dataset_name)
    coll.estimated_document_count()
    # check to see if it worked
    print(coll.find_one())
    print(list(coll.find()))
    


def experiment_setup(meta_file, bucket, s3_stim_paths, fam_trial_ids, batch_set_size):
    """
    load all stimulus dataset data, batch for individual participants, save exp_data jsons locally, upload dataset to mongoDB
    
    params:
    meta_file: string, name of metadata file for dataset
    bucket: string, AWS S3 bucket name
    s3_stim_paths: list of strings, paths to stimuli on S3 bucket
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    batch_set_size: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size
    """
    
    M = load_metadata(meta_file)
    M = build_s3_url(M, s3_stim_paths, bucket)
    M, M_fam, trial_data, fam_trials = get_familiarization_stimuli(M, fam_trial_ids)
    trial_data_sets = split_stim_set_to_batches(bucket, batch_set_size, M, trial_data)
    make_familiarization_json(bucket, M_fam)
    upload_to_mongo(trial_data_sets, fam_trials)    


def main():
    bucket = 'cognitive-ai-benchmarking-physion-stim'
    meta_file = './metadata.json'
    s3_stim_paths = ['maps/*_map.png', 'mp4s/*_img.mp4']
    fam_trial_ids = ['pilot_dominoes_0mid_d3chairs_o1plants_tdwroom_0013',
                     'pilot_dominoes_1mid_J025R45_boxroom_0020']
    batch_set_size = 37
    experiment_setup(meta_file, bucket, s3_stim_paths, fam_trial_ids, batch_set_size)

if __name__ == "__main__":
    main()
