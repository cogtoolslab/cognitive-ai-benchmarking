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
from utils import get_db_connection
from upload_to_s3 import get_filepaths


def build_s3_url(filenames, bucket):
    """
    convert filenames to AWS S3 URLs
    
    params:
    bucket: string, AWS S3 bucket name
    filenames: list of strings, AWS S3 filenames
    """
    s3_urls = []
    for f in filenames:
        s3_urls.append('https://{}.s3.amazonaws.com/{}'.format(bucket, f))
    return s3_urls


def make_stimulus_dataframe(bucket, data_root, data_path, multilevel):
    """
    make pandas dataframe of filenames and s3 urls
    
    params:
    bucket: string, AWS S3 bucket name
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload
    multilevel: True for multilevel directory structures, False if all data is stored in one directore
    
    for a simple data directory with all to-be-uploaded files in one directory,  data_path is in the form /path/to/your/data
    
    for a multi-level directory structure, you will need to use glob ** notation in data_path to index all the relevant files. something like:
    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)
    """
    stim_IDs = get_filepaths(data_root, data_path, 
                      multilevel=multilevel, aws_path_out=True)
    stim_urls = build_s3_url(stim_IDs, bucket)
    M = pd.DataFrame([stim_IDs, stim_urls]).transpose()
    M.columns = ['stim_id', 'stim_URLs']
    return M


def merge_metadata_with_dataframe(M, meta_file):
    """
    load trial metadata and merge with main dataframe
    
    params:
    M: main pandas dataframe
    meta_file: string, path of metadata file for dataset
    """
    with open(meta_file, 'rb') as f:
        trial_metas = json.load(f)
    M_meta = pd.DataFrame(trial_metas).transpose()
    assert list(M_meta['stim_id']) == list(M['stim_id'])
    for key in M_meta.keys():
        if key == 'stim_id':
            continue
        M[key] = list(M_meta[key])
    return M


def get_familiarization_files(M, fam_trial_ids):
    """
    identify familiarization stimuli and make familiarization trial dataframe
    
    params:
    M: main pandas dataframe
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    """
    M_fam = M[M['stim_id'].isin(fam_trial_ids)]
    trials_fam = M_fam.transpose().to_dict()
    trials_fam = {str(key):value for key, value in trials_fam.items()}
    assert len(M_fam) == len(M_fam['stim_id'].unique())
    # drop familiarization trials from main dataframe
    M = pd.merge(M, M_fam, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
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
    for batch in range(n_batches):
        M_set = M_sets[batch].sample(frac=1)
        assert len(M_set) == len(M_set['stim_id'].unique())
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
    


def experiment_file_setup(bucket, data_root, data_path, meta_file, fam_trial_ids, batch_set_size, multilevel):
    """
    load all stimulus dataset data, batch for individual participants, save exp_data jsons locally, upload dataset to mongoDB
    
    params:
    bucket: string, AWS S3 bucket name
    meta_file: string, name of metadata file for dataset
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload
    meta_file: string, path of metadata file for dataset
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    batch_set_size: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size
    multilevel: True for multilevel directory structures, False if all data is stored in one directore
    
    for a simple data directory with all to-be-uploaded files in one directory,  data_path is in the form /path/to/your/data
    
    for a multi-level directory structure, you will need to use glob ** notation in data_path to index all the relevant files. something like:
    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)
    """
    filepaths = get_filepaths(data_root,data_path,
                               multilevel=multilevel, aws_path_out=True)
    s3_urls = build_s3_url(filepaths, bucket)
    M = make_stimulus_dataframe(bucket, data_root, data_path, multilevel=multilevel)
    M = merge_metadata_with_dataframe(M, meta_file)
    M, M_fam, trial_data, trials_fam = get_familiarization_files(M, fam_trial_ids)
    trial_data_sets = split_stim_set_to_batches(bucket, batch_set_size, M, trial_data)
    make_familiarization_json(bucket, M_fam)
    upload_to_mongo(trial_data_sets, trials_fam)


def main():
    bucket = 'dummy-stim'
    data_root = '/mindhive/nklab4/users/tom/bach_hackathon/dummy_dataset/'
    data_path = '*'
    meta_file = '/mindhive/nklab4/users/tom/bach_hackathon/dummy_metadata.json'
    fam_trial_ids = ['Image0001.png', 'Image0002.png']
    batch_set_size = 6
    multilevel = False

    experiment_file_setup(bucket, data_root, data_path, meta_file, fam_trial_ids, batch_set_size, multilevel)
    

if __name__ == "__main__":
    main()
