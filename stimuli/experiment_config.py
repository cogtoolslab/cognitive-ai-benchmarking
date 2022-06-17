import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('..')
import h5py
import random
import itertools
import ast
from IPython.display import clear_output
from glob import glob
import pymongo as pm
import json
import pandas as pd
from PIL import Image
import numpy as np
from cabutils import get_db_connection  # needs to be after sys.append
from upload_to_s3 import get_filepaths
import os


def load_metadata(meta_file, iteration):
    """
    load trial metadata

    params:
    meta_file: string, path to metadata file for dataset
    """
    with open(meta_file, 'rb') as f:
        trial_metas = json.load(f)
    M = pd.DataFrame(trial_metas).transpose()
    M['iteration'] = iteration
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

    base_pth = 'https://{}.s3.amazonaws.com/{}/{}{}'
    for path in s3_stim_paths:
        stim_type = path.split('/')[0]
        suffix = path.split('*')[1]
        M['{}_url'.format(stim_type)] = [base_pth.format(bucket, stim_type, x, suffix)
                                             for x in M['stimulus_name']]
    return M


def get_familiarization_stimuli(M, fam_trial_ids, iteration):
    """
    identify familiarization stimuli and make familiarization trial dataframe

    params:
    M: main pandas dataframe
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    """
    M_fam = M[M['stimulus_name'].isin(fam_trial_ids)]
    trials_fam = M_fam.transpose().to_dict()
    trials_fam = {str(key): value for key, value in trials_fam.items()}
    assert len(M_fam) == len(M_fam['stimulus_name'].unique())
    # drop familiarization trials from main dataframe
    for f in M_fam['stimulus_name']:
        ind = M.index[M['stimulus_name'] == f]
        M = M.drop(ind)
    return M, M_fam, trials_fam


def split_stim_set_to_batches(batch_set_size, M, project, experiment, iteration, n_entries):
    """
    split full stimulus dataset into batches that will be shown to individual participants

    params:
    bucket: string, AWS S3 bucket name
    batch_set_size: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size
    """
    # n_entries = int(len(M) / batch_set_size)
    # M_sets = np.array_split(M.sample(frac=1), n_entries)
    ##################################################################
    # most experiments require experiment-specific counterbalancing
    # for this example we assign stimuli randomly to batches
    # experiment specific-counterbalancing should go in the loop below
    ##################################################################
    trial_data_sets = []
    for batch in range(n_entries):
        # randomly sample the stimulus set
        assert batch_set_size <= len(
            M), "batch_set_size is larger than the number of stimuli in the dataset"
        M_set = M.sample(n=batch_set_size, replace=False,
                         random_state=np.random.get_state()[1] + batch)
        assert len(M_set) == M_set['stimulus_name'].nunique()
        # save json for each batch to disk in stimulus folder
        # M_set.transpose().to_json('{}_{}_{}_trial_data_{}.json'.format(project, experiment, iteration, batch))
        cur_dict = M_set.transpose().to_dict()
        trial_data_sets.append(
            {str(key): value for key, value in cur_dict.items()})
        # save trial_data_sets to disk
        with open('{}_{}_trial_data_{}.json'.format(project, experiment, iteration), 'w') as f:
            json.dump(trial_data_sets[batch], f)
    return trial_data_sets


def make_familiarization_json(M, project, experiment, iteration):
    M.transpose().to_json('{}_{}_trial_data_{}.json'.format(project, experiment, iteration))


def upload_to_mongo(project, experiment, iteration, trial_data_sets, trials_fam, drop_old=True):
    """
    upload batched experiment files to mongoDB
    """
    # we require that the database ends in input per convention
    if not "_input" in project:
        project = project + "_input"
    conn = get_db_connection()
    db = conn[project]
    coll = db[experiment]
    # get list of current collections
    sorted(db.list_collection_names())
    # drop collection if necessary.
    if drop_old:
        # db.drop_collection(experiment)
        # print("Dropped old collection {}".format(experiment))
        # delete only entries that match current iteration
        coll.delete_many({'iteration': iteration})
        print("Deleted old entries of iteration {} from collection {}".format(iteration, experiment))
    # upload to mongo
    for batch in range(len(trial_data_sets)):
        coll.insert_one({'stims': trial_data_sets[batch],
                        'familiarization_stims': trials_fam,
                         'iteration': iteration, })
    print('Done inserting records into database {}, collection {}. `.json` files have been saved to `stimuli/` folder.'.format(project, experiment))
    coll.estimated_document_count()
    # check to see if it worked
    # print(coll.find_one())
    # print(list(coll.find()))


def experiment_setup(project, experiment, iteration, meta_file_path, bucket, s3_stim_paths, fam_trial_ids, batch_set_size, n_entries, overwrite=True):
    """
    load all stimulus dataset data, batch for individual participants, save exp_data jsons locally, upload dataset to mongoDB

    params:
    meta_file: string, name of metadata file for dataset
    bucket: string, AWS S3 bucket name
    s3_stim_paths: list of strings, paths to stimuli on S3 bucket
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    batch_set_size: int, # of stimuli to be included in each batch. should be a divisor of overall stimulus set size
    """

    M = load_metadata(meta_file_path, iteration)
    M = build_s3_url(M, s3_stim_paths, bucket)
    M, M_fam, fam_trials = get_familiarization_stimuli(
        M, fam_trial_ids, iteration)
    trial_data_sets = split_stim_set_to_batches(
        batch_set_size, M, project, experiment, iteration, n_entries)
    make_familiarization_json(M_fam, project, experiment, iteration)
    upload_to_mongo(project, experiment, iteration,
                    trial_data_sets, fam_trials, overwrite)

# Debugging code
# if __name__ == '__main__':
#     PROJECT = "Cognitive_AI_Benchmarking"
#     DATASET = "Physion"
#     TASK = "OCP"
#     ITERATION = "1"
#     EXPERIMENT = DATASET + "_" + TASK

#     bucket = (PROJECT + "_" + DATASET).replace("_","-").lower() # bucket name on AWS S3 where stimuli where be stored. `_` is not allowed in bucket names
#     pth_to_s3_credentials = None # local path to your aws credentials in JSON format. Pass None to use shared credentials file
#     data_root = 'stimuli/Physion_Dominoes' 
#     data_path = '**/*' # this finds all subdirectories in data_root and loads all files in each subdirectory to s3
#     multilevel=True # Dominoes/ contains 2 subdirectories, so the structure is multi-level
#     stim_paths = ['maps/*_map.png', 'mp4s/*_img.mp4'] # list of paths to stimuli to upload to s3—include a pattern to match only for relevant files
#     meta_file = data_root + '/metadata.json' # path to metadata for stimulus set
#     fam_trial_ids = ['pilot_dominoes_0mid_d3chairs_o1plants_tdwroom_0013', 
#                     'pilot_dominoes_1mid_J025R45_boxroom_0020'] # image ids for familiarization trials
#     batch_set_size = 20
#     n_entries = 10 # how many different random orders do we want?

#     experiment_setup(PROJECT,
#                  EXPERIMENT,
#                  ITERATION,
#                  meta_file,
#                  bucket,
#                  stim_paths,
#                  fam_trial_ids,
#                  batch_set_size,
#                  overwrite=True,
#                  n_entries = n_entries)