import pymongo as pm
import os
import sys
import numpy as np
import pandas as pd
from experiments.watchdog.exclusion import *
import parse

DB = 'curiophysion'

def main():
    try:
        # this auth.txt file contains the password for the sketchloop user
        auth = pd.read_csv('auth.txt', header=None)
    except FileNotFoundError:
        print('auth.txt not found. Please create a file named auth.txt with the password for the sketchloop user.')
        sys.exit()
    pswd = auth.values[0][0]
    user = 'sketchloop'
    host = 'cogtoolslab.org'  # experiment server ip address

    try:
        conn = pm.MongoClient('mongodb://sketchloop:' + pswd + '@127.0.0.1')
        db = conn[DB]

        #get list of current collections
        collections = sorted(db.list_collection_names())
    except:
        print('Could not connect to database. Try to set up ssh bridge to write to mongodb. Insert your username. If you dont have an SSH secret set yet, run `ssh -fNL 27017:127.0.0.1:27017 USERNAME@cogtoolslab.org` in your shell.')
        sys.exit()
    print("We got the following collections:")
    print(collections)

    for coll_name in collections:
        print("Checking",coll_name)

        coll = db[coll_name]
        # might take a long time
        coll_df = pd.DataFrame(coll.find())
        print("We have {} entries".format(len(coll_df)))

        iterations = coll_df['iterationName'].unique()
        print("We have the following iterations:\n",
              list(coll_df['iterationName'].unique()))

        for iteration in iterations:
            print("Getting",iteration,"on",coll_name)
            df = pd.DataFrame(coll_df[coll_df['iterationName'] == iteration])

            # perform pre-exclusions
            df = pre_exclusion(df)


            ### add flag column
            df['flags'] = ""

            games = df['gameID'].unique()
            print("We have {} total unique games".format(len(games)))

            good_games = []
            completed_games = []  # complete games that might otherwise be flagged

            for game in games:
                reasons = exclude_games(df[df['gameID'] == game], df)
                if reasons == []:
                    good_games.append(game)
                else:
                    if 'unfinished' not in reasons:
                        df.loc[df['gameID'] == game, 'flags'] = str(reasons)
                        completed_games.append(game)
                        # print("Excluded {} for the following reasons: ".format(game), reasons)

            completed_games += good_games
            print("We have {} good unique games and {} completed unique games".format(
                len(good_games), len(completed_games)))

            # ⚠️ exclude flagged games
            df = df[df['gameID'].isin(good_games)]

            print("{} unique games left".format(df['gameID'].nunique()))

            # apply fixes
            df = fix_df(df)

            # out to disk with it!
            filename = "curiophysion_"+coll_name+"_"+iteration+".csv"
            path = os.path.join(os.path.join(os.getcwd(), "results"), filename)
            print("Saving {} out to:\n{}".format(filename, path))
            df.to_csv(path)
            print("Saved.")
    
    print("Done. Download all scenarios and iterations ")


def fix_df(df):
    """Applies various fixes to df"""
    try:
        df['push_force'] = df['push_force'].apply(parse_pushforce)
    except KeyError:
        print("No push_force column")

    df['stimulus_name'] = df['stimulus_name'].apply(fix_stim_name)
    return df

# save pushforce as vector magnitude
def parse_pushforce(text):
    if text is np.nan:
       return np.nan
    if type(text) is float:
        return text
    try:
        vec = parse.parse("[{x}{:s}{y}{:s}{z}{:s}]", text).named
        # parse the number
        vec = {key: eval(val) for key, val in vec.items()}
        #get magnitude
        mag = np.sqrt(np.sum([val**2 for val in vec.values()]))
        return mag
    except AttributeError:
        return np.nan

#fix trailing char in stim_name
def fix_stim_name(name):
    if type(name) is str:
        return name.split("'")[1]
    else:
        return np.NaN

# run main
if __name__ == '__main__':
    main()
