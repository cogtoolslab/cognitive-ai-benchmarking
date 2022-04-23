"""This files contains a script that ensures that we keep an up-to-date tally of underserved stims to ensure an equal distribution of observations across stimuli.
It periodically fetches responses from the database, performs exclusions, computes underserved stims and stores them in the database."""

DB = 'curiophysion'
BALANCING_COLL = 'curiophysion_stim_balance'

COLLS = [
    'clothiness',
    'collision',
    'containment',
    'dominoes',
    'drop',
    'linking',
    'rollingsliding',
    'towers',
    ]

NUM_STIMS = 150 # number of stims per session that we require to start balancing. Otherwise we might exclude other stims.
STIMS_PER_SESSION = 25 # how many stimuli are shown per participant?
TARGET = 32 # how many observations per stimulus?

DURATION = 10 # how often to check in seconds

# imports
import pymongo as pm
import sys
import numpy as np
import pandas as pd
import json
from experiments.watchdog.exclusion import *
import time

def main():
    try:
        auth = pd.read_csv('auth.txt', header = None) # this auth.txt file contains the password for the sketchloop user
    except FileNotFoundError:
        print('auth.txt not found. Please create a file named auth.txt with the password for the sketchloop user.')
        sys.exit()
    pswd = auth.values[0][0]
    user = 'sketchloop'
    host = 'cogtoolslab.org' ## experiment server ip address

    try:
        conn = pm.MongoClient('mongodb://sketchloop:' + pswd + '@127.0.0.1')
    except:
        print('Could not connect to database. Try to set up ssh bridge to write to mongodb. Insert your username. If you dont have an SSH secret set yet, run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` in your shell.')
        sys.exit()
    db = conn[DB]
    # get stim collection
    stim_db = conn['stimuli']
    stim_coll = stim_db[BALANCING_COLL]
    # we keep a dictionary of the latest entry for each study so we don't need to pull the entire dataframe when nothing has changed
    latest_entries = {}
    # we keep a dictionary with number of good games
    good_games_per_study = {}

    print("All set. Remember to stop this script when you're done collecting data. Starting to check for underserved stims...")
    while True:
        for coll_name in COLLS:
            print('\n \nChecking ' + coll_name)
            coll = db[coll_name]
            # get iteration names
            try:
                iteration_names = coll.distinct('iterationName')
            except pm.errors.ServerSelectionTimeoutError:
                print('Could not connect to database. Try to set up ssh bridge to write to mongodb. Insert your username. If you dont have an SSH secret set yet, run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` in your shell.')
                sys.exit()
            print("We have {} iterations: {}".format(len(iteration_names), str(iteration_names)))
            if len(iteration_names) == 0:
                continue

            for iteration_name in iteration_names:
                # get document name
                doc_name = coll_name + '_' + iteration_name
                print("\nChecking iteration {}".format(iteration_name))
                # get latest entry
                try:
                    # latest_entry = str(coll.find({'iterationName': iteration_name}).limit(1).sort("{$natural: -1}")[0]['_id'])
                    latest_entry = str(coll.find_one({'iterationName': iteration_name},sort=[('$natural', -1)])['_id'])
                except IndexError:
                    # no entries yet—this should not be reachable
                    print("No entries in database yet. Skipping...")
                    continue
                try:
                    if latest_entry == latest_entries[doc_name]:
                        print("No new data, latest was ID: {}. Skipping...".format(latest_entry))
                        continue
                except KeyError:
                    # We don't have an entry yet, add it
                    print("Adding latest entry with ID: {}".format(latest_entry))
                    latest_entries[doc_name] = latest_entry
                
                # get all entries for iteration
                it_df = pd.DataFrame(coll.find({'iterationName': iteration_name}))
                # perform exclusions
                it_df = pre_exclusion(it_df)
                it_df = perform_exclusion(it_df)

                # get number of good games
                good_games = it_df['gameID'].unique()
                # add to dictionary
                good_games_per_study[coll_name+"_"+iteration_name] = len(good_games)

                # do we have enough data?
                if len(it_df) == 0:
                    print("No data. Skipping...")
                    continue
                
                # do we have at least one observation per stimulus?
                # TODO pull stimulus from stim database so we don't need to start worrying about covering each first 
                if it_df['stimulus_name'].nunique() < NUM_STIMS:
                    print("Only {} stimuli out of {} covered yet. Skipping....".format(it_df['stimulus_name'].nunique(), NUM_STIMS))
                    continue

                # how many observations per stimulus do we have?
                undercovered = find_undercovered_stims(it_df)
                
                # insert list of undercovered stims into stim database
                # get document
                doc = stim_coll.find_one({'name': doc_name})
                if doc is None:
                    # create new document
                    doc = {'name': doc_name, 'stims': undercovered}
                    stim_coll.insert_one(doc)
                else:
                    # update document
                    doc['stims'] = undercovered
                    stim_coll.replace_one({'name': doc_name}, doc)
                print("Inserted into {} under {}".format(BALANCING_COLL, doc_name))

        # save dictionary with number of good games to csv
        good_games_df = pd.DataFrame.from_dict(good_games_per_study, orient='index')
        good_games_df.columns = ['num_good_games']  # rename column
        good_games_df.index.name = 'study_iteration'  # rename index
        good_games_df.to_csv('num_good_games.csv')
        
        print("Done with all. Sleeping...")
        time.sleep(DURATION)

def perform_exclusion(it_df):
    print("We have {} entries".format(len(it_df)))
    # perform the exclusions
    # add flag column
    it_df['flags'] = ""

    games = it_df['gameID'].unique()
    print("We have {} total unique games".format(len(games)))

    good_games = []
    completed_games = [] #complete games that might otherwise be flagged

    for game in games:
        reasons = exclude_games(it_df[it_df['gameID'] == game],it_df) # reasons returns a list of reasons why a gameID is flagged. Empty list is good.
        if reasons == []:
            good_games.append(game)
        else:
            if 'unfinished' not in reasons:
                it_df.loc[it_df['gameID'] == game,'flags'] = str(reasons)
                completed_games.append(game)
                # print("Excluded {} for the following reasons: ".format(game),reasons)
                
    completed_games+=good_games
    print("We have {} good unique games and {} completed unique games".format(len(good_games),len(completed_games)))

    # ⚠️ exclude flagged games
    it_df = it_df[it_df['gameID'].isin(good_games)]

    return it_df


def find_undercovered_stims(it_df):                
    counts = pd.DataFrame(it_df['stimulus_name'].value_counts()).reset_index()
    # extract smallest viable set of undercovered stims
    c = TARGET
    while c >= 0:
        # keep iterating until we find the smallest set of stims with the
        undercovered = list(
            counts[counts['stimulus_name'] < c]['index'])
        if len(undercovered) < STIMS_PER_SESSION:
            # not enough stims
            c = c+1
            undercovered = list(
                counts[counts['stimulus_name'] < c]['index']) # need to update the list with the larger c
            break
        c = c - 1
    undercovered = list(
        counts[counts['stimulus_name'] < c]['index'])
    print("We got {} stims with a maximum of {} observations".format(
        len(undercovered),
        c-1))
    return undercovered

# run main
if __name__ == '__main__':
    main()
