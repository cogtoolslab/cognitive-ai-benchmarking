import json
import boto3
from tqdm import tqdm
from glob import glob
from botocore.exceptions import ClientError


def get_s3_client(credential_path):
    """
    Open AWS S3 client

    Params:
    pth_to_credentials: string, path to AWS credentials file. If None, shared credential file will be used.
    """
    if credential_path is None:
        s3 = boto3.resource('s3')
    else:
        credentials = json.load(open(credential_path, "r"))
        s3 = boto3.resource(service_name="s3",
                            aws_access_key_id=credentials.get(
                                "aws_access_key_id"),
                            aws_secret_access_key=credentials.get("aws_secret_access_key"))
    return s3


def create_bucket(client, bucket, location='us-east-2'):
    """
    Create new bucket on AWS S3

    Params:
    client: s3 client object
    bucket: string, name of bucket to create

    see below for valid bucket naming conventions:
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
    """
    assert all([x.islower() for x in bucket if x.isalpha()]
               ), 'Invalid bucket name. (no uppercase letters in bucket name)'
    assert '_' not in bucket, 'Invalid bucket name. (consider replacing _ with -)'
    try:
        b = client.create_bucket(Bucket=bucket,
                                 CreateBucketConfiguration={
                                     "LocationConstraint": location})
        print('Created new bucket.')
    except Exception as e:
        b = client.Bucket(bucket)
        print('Bucket exists. Skipping creation.')
        # logging.error(e)
    b.Acl().put(ACL="public-read")
    return b


def check_exists(client, bucket, stim):
    """
    Check if file exists on AWS S3

    Params:
    client: s3 client object
    bucket: string, name of s3 bucket to check
    stim: string, name of stimulus to check
    """
    try:
        client.Object(bucket, stim).load()
        return True
    except ClientError as e:
        if (e.response['Error']['Code'] == "404"):
            return False
        else:
            print('Something else has gone wrong with {}'.format(stim))


def upload(client, bucket, s3_path, local_path, overwrite=False):
    """
    Upload file to AWS S3 bucket

    Params:
    client: s3 client object
    bucket: string, name of bucket to write to
    s3_path: string, new path for upload in bucket
    local_path: string, local path of file being uploaded
    """
    if check_exists(client, bucket, s3_path) and not overwrite:
        # print(s3_path + " exists on s3. Skipping")
        return

    # print("Uploading " + local_path + " to path: " + s3_path)
    client.Object(bucket, s3_path).put(
        Body=open(local_path, 'rb'))  # upload stimuli
    client.Object(bucket, s3_path).Acl().put(
        ACL='public-read')  # set access controls
    return


def get_filepaths(data_root, data_path, multilevel=True, aws_path_out=False):
    """
    Get filepaths for all files to upload to AWS S3

    Params:
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload
    multilevel: True for multilevel directory structures, False if all data is stored in one directore

    for a simple data directory with all to-be-uploaded files in one directory,  data_path is in the form /path/to/your/data

    for a multi-level directory structure, you will need to use glob ** notation in data_path to index all the relevant files. something like:
    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)
    """
    if type(data_path) is str:
        data_path = [data_path]
    filepaths = []
    if multilevel:
        for dp in data_path:
            for pth in glob(data_root+'/'+dp, recursive=True):
                filepaths.append(pth)
    else:
        for pth in glob(data_root+data_path):
            filepaths.append(pth)
    if aws_path_out:
        filepaths = [x.split(data_root)[1] for x in filepaths]
    return sorted(filepaths)


def upload_stim_to_s3(bucket,
                      pth_to_s3_credentials,
                      data_root,
                      data_path,
                      multilevel=True,
                      overwrite=False):
    """
    Upload stimuli dataset to AWS S3

    Params:
    bucket: string, name of bucket to write to
    pth_to_s3_credentials: string, path to AWS credentials file
    data_root: string, root path for data to upload
    data_path: string, path in data_root to be included in upload
    multilevel: True for multilevel directory structures, False if all data is stored in one directore
    overwrite: True to overwrite existing files, False to skip

    for a simple data directory with all to-be-uploaded files in one directory,  data_path is in the form /path/to/your/data

    for a multi-level directory structure, you will need to use glob ** notation in data_path to index all the relevant files. something like:
    /path/to/your/files/**/* (this finds all the files in your directory structure)
    /path/to/your/files/**/another_dir/* (this finds all the files contained in all sub-directories named another_dir)
    /path/to/your/files/**/another_dir/*png (this finds all the pngs contained in all sub-directories named another_dir)
    """
    client = get_s3_client(pth_to_s3_credentials)
    b = create_bucket(client, bucket)
    filepaths = get_filepaths(data_root, data_path, multilevel=multilevel)
    # print("Got {} filepaths".format(len(filepaths)))
    for fp in tqdm(filepaths):
        if "." in fp:
            s3_path = fp.split(data_root)[1]
            if s3_path[0] == '/': s3_path = s3_path[1::]
            upload(client, bucket, s3_path, fp, overwrite=overwrite)
            # print("Uploaded " + fp + " to s3 path: " + s3_path)
    print("Done")
#

# debugging
# if __name__ == "__main__":
#     # bucket name on AWS S3 where stimuli where be stored
#     bucket = 'cognitive-ai-benchmarking-physion'
#     # local path to your aws credentials
#     pth_to_s3_credentials = None
#     # make sure to have trailing / for data_root
#     data_root = '/Users/felixbinder/Desktop/Physion/Dominoes'
#     # this finds all subdirectories in data_root and loads all files in each subdirectory to s3
#     data_path = '**/*'
#     multilevel = True  # Dominoes/ contains 2 subdirectories, so the structure is multi-level
#     # list of paths to stimuli to upload to s3—include a pattern to match only for relevant files
#     stim_paths = ['maps/*_map.png', 'mp4s/*_img.mp4']
#     meta_file = './metadata.json'  # path to metadata for stimulus set
#     fam_trial_ids = ['pilot_dominoes_0mid_d3chairs_o1plants_tdwroom_0013',
#                      'pilot_dominoes_1mid_J025R45_boxroom_0020']  # image ids for familiarization trials
#     batch_set_size = 37  # 150 total stimuli, 2 familiarization trials, 4 batches
#     # upload dataset to aws s3
#     upload_stim_to_s3(bucket,
#                       pth_to_s3_credentials,
#                       data_root,
#                       stim_paths,
#                       multilevel)
