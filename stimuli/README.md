Directory to contain stimulus preprocessing code for this project.

upload_to_s3.py contains a series of functions to upload datasets to AWS S3. 

To upload data, call the function upload_stim_to_s3. 

It takes 5 inputs:
    bucket: string, name of bucket to write to
    pth_to_s3_credentials: string, path to AWS credentials file
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload
    multilevel: True for multilevel directory structures, False if all data is stored in one directore
    
for a simple data directory with all to-be-uploaded files in one directory,  data_path is in the form /path/to/your/data
    
for a multi-level directory structure, you will need to use glob ** notation in data_path to index all the relevant files. something like:

    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)

upload_stim_to_s3(bucket=‘bucket-name’,
                  pth_to_s3_credentials=‘/path/to/aws/s3/credentials.json’,
                  data_root=‘/local/path/to/top/level/of/data/directory/’,
                  data_path=‘directory/structure/within/data/directory/’,
                  multilevel=True)