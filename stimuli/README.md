
# Preparing your stimuli for your experiment
The process to prepare your stimuli for the experiment follows 3 steps.

1. Prepare your stimuli. These code examples assume you have a directory structure with stimulus files (this can be a single directory with all stimuli or a nested directory structure) and a metadata.json file containing the relevant metadata you'll need for each stimuli.

2. Upload your data to AWS S3 so you have a semi-permanent link to access the stimuli while your experiment is running.

3. Configure your experiment. This step will 1.) create a dataframe of all the filenames, S3 links, and metadata for all the stimuli in your set, 2.) batch the full dataset into smaller chunks that will be presented to individual participants, 3.) save local JSON files with the filenames, s3 links, and metadata for each batch, and 4.) upload the same filenames/s3 links/metadata for each batch to MongoDB.

Each step is broken down in more detail below. An ipynb notebook example for running the code is included. The example uses the Dominoes subset of the Physion dataset (which can be downloaded here (https://physics-benchmarking-neurips2021-dataset.s3.amazonaws.com/Physion_Dominoes.zip).

## Step 1 - Create your stimulus set
Step 1 above is assumed to be completed on your end before use of the code in this repo.

## Step 2 - Upload stimulus to AWS S3
The purpose of this step is to host your stimuli on AWS S3 so you have a semi-permanent link to refer to each stimulus. These links will be used when running the online experiment to retrieve the necessary stimulus for each trial and present the stimulus to the participants. 

Step 2 is handled by the function `upload_stim_to_s3` in `upload_to_s3.py`. This function takes 5 inputs:
- `bucket`: string, name of AWS s3 bucket to write to

- `pth_to_s3_credentials`: string, path to AWS credentials file. Alternatively, you can pass `None` to use a shared credentials file (usually in `~/.aws/credentials`) or environment variables.

- `data_root`: string, root path for data to upload

- `data_path`: string, path in data_root to be included in upload.

- `multilevel`: True for multilevel directory structures, False if all data is stored in one directory

- `overwrite`: Set to true if files have changed and the files in S3 need to be overwritten.

For a simple data directory with all to-be-uploaded files stored in data_root without any sub-directories, data_path should simply be *
    
For a multi-level directory structure, you will need to use glob * and ** notation in data_path to index all the relevant files and set multilevel=True. Any multi-level directory structure is preserved in the uploaded AWS S3 bucket.  Here are some basic examples of the glob notation:

    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)

Example code to call `upload_to_s3.py` can be found in `stimulus_setup_example.ipynb` 

## Step 3 - Experiment Configuration
The purpose of this step is to compile all relevant metadata for all stimuli into a single omnibus dataframe, chunk the full stimulus set into smaller batches that are the appropriate size to be shown to a single participant within the allotted time for your experiment, save local copies of the batched dataframes, and upload the dataframes to MongoDB for use in the actual experiment interface.

Chunking the full stimulus set into smaller batches is usually necessary so individual participants can complete the experiment in a reasonable amount of time. For example, you have have a large set of stimuli (e.g. 500) that you would like to record behavioral responses for. However, depending on your trial length, it may take an unreasonably long time for one participant to view and respond to all stimuli. In this case, you break the stimulus set down into smaller batches that can be completed in a reasonable amount of time (we usually aim for a maximum experiment time of 30 minutes for an individual participant). For our example dataset with 500 stimuli, if each trial takes ~20 seconds, then showing one participant 50 stimuli would take about 16.6 minutes (not including time for instructions and familiarization trials). If we decide this sounds good for our experiment, then we would need 10 batches of 50 stimuli each to cover the whole set. Each participant would see one batch, and results across all subjects then provide responses for all stimuli in the full set. Note that your batch size should be a multiple of your overall stimulus set size (after removing familiariazation trials, more below).

Many experiments will have stimuli from different conditions. If this is the case, you will want to counter-balance across batches so an equal number of stimuli from each condition appear in each batch. Since this is idiosyncratic to each experiment, this code does not support counterbalancing and randomly assigns images to batches. However, the relevant section in `experiment_config.py` where such counterbalancing can be added is indicated starting on line 83.

Another relevant feature of Experiment Configuration is the inclusion of familiarization stimuli to let participants practice the task before beginning the real experiment. These appear at the beginning of the experiment either after or interleaved with the instructions for the task. This code assumes all subjects will see the same set of familiarization stimuli. These will be specified as an input to the experiment configuration function in the form of a list of filenames. Note that when selecting your batch size, make sure to subtract the number of familiarization stimuli from the total stimulus set size before determining a multiple of the stimulus set size as your batch size.

Step 3 is handled by `experiment_config.py`. To load the relevant metadata into a dataframe, batch it into individual session dataframes, save local JSONs for each batch, and upload the dataframes to MongoDB, call the function `experiment_file_setup`. This function takes 7 inputs:

- `meta_file`: string, path to a JSON file that contains all the relevant metadata for each stimulus.

- `bucket`: string, name of AWS s3 bucket to write to (same as Step 2)

- `s3_stim_paths`: list of strings, paths to stimuli on S3 bucket
    
- `fam_trial_ids`: fam_trial_ids: list of strings, stim_id for familiarization stimuli shown to participants before the experiment to familiarize them with the task

- `batch_set_size`: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size (not including familiarization files in the count for the overall stimulus set size). Set to the number of stimuli in the experiment if you want to use the full set of stimuli for every participant.

- `overwrite`: Should the collection (usually corresponing to the name of the experiment) be overwritten if it already exists? Set to True if you want to clear the collection of all entries. Note that this will delete **all** entries in the collection, including those with of an earlier iteration.

- `n_entries`: How many different shuffled/sampled version of the stimuli should we include? It is recommended to include more shuffled entries than the expected number of participants.
    
Example code to call `experiment_config.py` can be found in `stimulus_setup_example.ipynb` 
