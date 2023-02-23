"""This file will download all stimuli from S3 and save them to a local directory."""

import os
import sys
import boto3
import botocore
import argparse
from tqdm import tqdm
from glob import glob

def download_bucket(bucket_name, local_dir):
    """Download all files from an S3 bucket."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = list(bucket.objects.all())
    if bucket_name not in local_dir:
        local_dir = os.path.join(local_dir, bucket_name)
    print('Downloading {} files from bucket {} to {}'.format(len(objects), bucket_name, local_dir))
    for obj in tqdm(objects):
        target = os.path.join(local_dir, obj.key)
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        # does the file exist already?
        if os.path.exists(target):
            # if so, is it the same size?
            if os.path.getsize(target) == obj.size:
                # if so, skip it
                continue
        bucket.download_file(obj.key, target)
    print('Downloaded all files from bucket {} to {}'.format(bucket_name, local_dir))

def get_bucket_urls(bucket_name):
    """Get all urls for files in an S3 bucket."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = list(bucket.objects.all())
    urls = []
    for obj in objects:
        url = 'https://{}.s3.amazonaws.com/{}'.format(bucket_name, obj.key)
        urls.append(url)
    return urls

def save_url_lists(bucket_names, local_dir=None):
    """Save lists of urls for all files in a list of S3 buckets."""
    if local_dir is None:
        local_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'urls')
    # does the directory exist?
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    for bucket_name in bucket_names:
        urls = get_bucket_urls(bucket_name)
        with open(os.path.join(local_dir, '{}_urls.txt'.format(bucket_name)), 'w') as f:
            for url in urls:
                f.write('{}\n'.format(url))
        print('Saved {} urls to {}'.format(len(urls), os.path.join(local_dir, '{}_urls.txt'.format(bucket_name))))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download all stimuli from S3.')
    parser.add_argument('--bucket_name', type=str, default='physion-stimuli', help='name of S3 bucket')
    parser.add_argument('--local_dir', type=str, default='.', help='directory to save stimuli to')
    args = parser.parse_args()
    download_bucket(args.bucket_name, args.local_dir)