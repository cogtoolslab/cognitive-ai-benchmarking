Directory containing stimulus preprocessing code for this project.

The process to prepare your stimuli for the experiment broadly follows 3 steps

1. Prepare your stimuli. These code examples assume you have a directory structure with stimlus files (this can be a single directory with all stimuli or a nested directory structure) and a metadata.json file containing the relevant metadata you'll need for each stimuli.

2. Upload your data to AWS S3 so you have a semi-permanent link to access the stimuli while your experiment is running.

3. Configure your experiment. This step will 1.) create a dataframe of all the filenames, S3 links, and metadata for all the stimuli in your set, 2.) batch the full dataset into smaller chunks that will be presented to individual participants, 3.) save local JSON files with the filenames, s3 links, and metadata for each batch, and 4.) upload the same filenames/s3 links/metadata for each batch to MongoDB.

Each step is broken down in more detail below. The ipynb code examples make use of the Dominoes subset of the Physion dataset (also included in the stimuli directory).


Step 1 above is assumed to be completed on your end before use of the code in this repo.


Step 2 is handled by upload_to_s3.py. To upload data, call the function upload_stim_to_s3. This function takes 5 inputs:
    bucket: string, name of AWS s3 bucket to write to
    pth_to_s3_credentials: string, path to AWS credentials file
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload.
    multilevel: True for multilevel directory structures, False if all data is stored in one directory

For a simple data directory with all to-be-uploaded files stored in data_root without any sub-directories, data_path should simply be *
    
For a multi-level directory structure, you will need to use glob * and ** notation in data_path to index all the relevant files and set multilevel=True. Any multi-level directory structure is preserved in the uploaded AWS S3 bucket.  Here are some basic examples of the glob notation:

    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)

Example code to call upload_to_s3.py can be found in upload_to_s3_example.ipynb


Step 3 is handled by experiment_config.py. To load the relevant metadata into a dataframe, batch it into individual session dataframes, save local JSONs for each batch, and upload the dataframes to MongoDB, call the function experiment_file_setup. This function takes 7 inputs:
    bucket: string, name of AWS s3 bucket to write to (same as Step 2)
    data_root: string, root path for data to upload (same as Step 2)
    data_path: string, path in data_root to be included in upload. (same as Step 2)
    multilevel: True for multilevel directory structures, False if all data is stored in one directore (same as Step 2)
    meta_file: string, path to a JSON file that contains all the relevant metadata for each stimulus.
    fam_trial_ids: fam_trial_ids: list of strings, stim_id for familiarization stimuli shown to participants before the experiment to familiarize them with the task
    batch_set_size: int, # of stimuli to be included in each batch. should be a multiple of overall stimulus set size (not including familiarization files in the count for the overall stimulus set size)
    
Example code to call experiment_config.py can be found in experiment_config_example.ipynb 
