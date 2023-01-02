from parse_hdf5 import get_label, get_metadata_from_h5
from tqdm import tqdm
from upload_to_s3 import get_filepaths
import numpy as np
import pandas as pd
import json
import pymongo as pm
from glob import glob
from IPython.display import clear_output
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('..')

from cabutils import get_db_connection  # needs to be after sys.append


def load_metadata(paths, iteration, json_path=None):
    """
    load trial metadata

    params:
    path: string
    use_json: bool, if True, load metadata from json file
    """
    print('Loading metadata...')
    if json_path:
        return load_metadata_json(json_path, iteration)
    else:
        print('Parsing labels...')
        labels = [get_label(path) for path in tqdm(paths)]
        print('Reading `static`...')
        metadatas = [get_metadata_from_h5(path) for path in tqdm(paths)]
        # create dataframe
        M = pd.DataFrame(metadatas)
        M['target_contacting_zone'] = labels
        print("Got data for {} stimuli".format(len(M)))
        return M


def load_metadata_json(meta_file, iteration):
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

    STIM_TYPES = {'*_img.mp4': 'mp4s_url',
                  '*_map.png': 'maps_url'
                  }

    base_pth = 'https://{}.s3.amazonaws.com/{}/{}{}'
    for path in s3_stim_paths:
        try: # what sort of path is this? 
            stim_type = STIM_TYPES[path]
        except: # not one obsviously corresponding to the two hard coded types
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
    ##################################################################
    # most experiments require experiment-specific counterbalancing
    # for this example we assign stimuli randomly to batches
    # experiment specific-counterbalancing should go in the loop below
    ##################################################################
    trial_data_sets = []
    print("Splitting stimulus set into batches...")
    for batch in tqdm(range(n_entries)):
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
        # fails if a ndarray is somewhere in the structure
        with open('{}_{}_trial_data_{}.json'.format(project, experiment, iteration), 'w') as f:
            json.dump(trial_data_sets[batch], f)
    print("Saving—might take a second...")
    # save to disk as dataframe
    csv_name = '{}_{}_trial_data_{}.csv'.format(project, experiment, iteration)
    pd.DataFrame(trial_data_sets).to_csv(
        csv_name)
    print("Saved {} batches of {} stimuli to disk at {}".format(
        n_entries, batch_set_size, csv_name))
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
    print("Uploading to mongoDB with project {}, experiment {}, iteration {}...".format(
        project, experiment, iteration))
    conn = get_db_connection()
    db = conn[project]
    coll = db[experiment]
    # get list of current collections
    print("We have the following collections:",
          sorted(db.list_collection_names()))
    # drop collection if necessary.
    if drop_old:
        # delete only entries that match current iteration
        coll.delete_many({'iteration': iteration})
        print("Deleted old entries of iteration {} from collection {}".format(
            iteration, experiment))
    # upload to mongo
    print("Uploading {} batches of {} stimuli to mongoDB...".format(
        len(trial_data_sets), len(trial_data_sets[0])))
    for batch in tqdm(range(len(trial_data_sets))):
        coll.insert_one({'stims': trial_data_sets[batch],
                        'familiarization_stims': trials_fam,
                         'iteration': iteration, })
    print('Done inserting records into database {}, collection {}. `.json` files have been saved to `stimuli/` folder.'.format(project, experiment))
    coll.estimated_document_count()
    # check to see if it worked
    # print(coll.find_one())
    # print(list(coll.find()))


def experiment_setup(project, experiment, iteration, bucket, s3_stim_paths, hdf5_paths, fam_trial_ids, batch_set_size, n_entries, overwrite=True):
    """
    load all stimulus dataset data, batch for individual participants, save exp_data jsons locally, upload dataset to mongoDB

    params:
    meta_file: string, name of metadata file for dataset
    bucket: string, AWS S3 bucket name
    s3_stim_paths: list of strings, paths to stimuli on S3 bucket
    fam_trial_ids: list of strings, stim_id for familiarization stimuli
    batch_set_size: int, # of stimuli to be included in each batch. should be a divisor of overall stimulus set size
    """

    M = load_metadata(hdf5_paths, iteration)
    print("Loaded metadata for {} stimuli".format(len(M)))
    M = build_s3_url(M, s3_stim_paths, bucket)
    print("Loaded S3 URLs for {} stimuli".format(len(M)))
    M, M_fam, fam_trials = get_familiarization_stimuli(
        M, fam_trial_ids, iteration)
    print("Loaded familiarization stimuli for {} stimuli".format(len(M_fam)))
    trial_data_sets = split_stim_set_to_batches(
        batch_set_size, M, project, experiment, iteration, n_entries)
    print("Split stimuli into {} batches of {} stimuli".format(
        n_entries, batch_set_size))
    make_familiarization_json(M_fam, project, experiment, iteration)
    upload_to_mongo(project, experiment, iteration,
                    trial_data_sets, fam_trials, overwrite)
    print("Uploaded stimuli to mongoDB")

