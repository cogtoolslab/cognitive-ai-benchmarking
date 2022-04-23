If you want to test your experiment on the server but don't want to worry about MongoDB, you can do the following:

First, create a directory in the `stimuli` folder specified by your database name and collection name (e.g. `stimuli/BACH/dominoes/`). 

Then run the `generate_metadata.ipynb` jupyter notebook to generate your stimuli and save the is as a `.json` file in the directory you just created.

Next, run `node app.js --gameport PORT --local_store`. This needs to be ran from the experiments folder (ie. do `cd experiments` before running this).

This should be it! When you try out the experiment, your data will be saved on the server (as opposed to MongoDB) in the direcotry: `results/databaseName_resp/collectionName.csv` (e.g. `results/BACH_resp/dominoes.csv`) that you can check and help you debug.