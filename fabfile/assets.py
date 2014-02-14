#!/usr/bin/env python

from glob import glob
import os

import boto
from fabric.api import prompt, task
import app_config
import utils

@task
def sync():
    """
    Intelligently synchronize assets between S3 and local folder.
    """
    local_paths = []

    for local_path, subdirs, filenames in os.walk('www/assets'):
        for name in filenames:
            local_paths.append(os.path.join(local_path, name))

    bucket = _assets_get_bucket()
    keys = bucket.list(app_config.PROJECT_SLUG)

    which = None
    always = False

    for key in keys:
        download = False
        upload = False

        local_path = key.name.replace(app_config.PROJECT_SLUG, 'www/assets', 1)

        print local_path

        if local_path in local_paths:
            # A file can only exist once, this speeds up future checks
            # and provides a list of non-existing files when complete
            local_paths.remove(local_path)

            # We need an actual key, not a "list key"
            # http://stackoverflow.com/a/18981298/24608
            key = bucket.get_key(key.name)

            with open(local_path, 'rb') as f:
                local_md5 = key.compute_md5(f)[0]

            # Hashes are different
            if key.get_metadata('md5') != local_md5:
                if not always:
                    # Ask user which file to take
                    which, always = _assets_confirm(local_path)

                if not which:
                    print 'Cancelling!'

                    return

                if which == 'remote':
                    download = True
                elif which == 'local':
                    upload = True
        else:
            download = True
            
        if download:
            _assets_download(key, local_path)

        if upload:
            _assets_upload(local_path, key)

    action = None
    always = False

    # Iterate over files that didn't exist on S3
    for local_path in local_paths:
        key_name = local_path.replace('www/assets', app_config.PROJECT_SLUG, 1)
        key = bucket.get_key(key_name, validate=False)

        print local_path

        if not always:
            action, always = _assets_upload_confirm()

        if not action:
            print 'Cancelling!'

            return

        if action == 'upload':
            _assets_upload(local_path, key)
        elif action == 'delete':
            _assets_delete(local_path, key)

@task
def assets_rm(path):
    """
    Remove an asset from s3 and locally
    """
    bucket = _assets_get_bucket()

    file_list = glob(path)

    if len(file_list) > 0:
        utils.confirm("You are about to destroy %i files. Are you sure?" % len(file_list))

        for local_path in file_list:
            key_name = local_path.replace('www/assets', app_config.PROJECT_SLUG, 1)
            key = bucket.get_key(key_name)
            
            _assets_delete(local_path, key)

def _assets_get_bucket():
    """
    Get a reference to the assets bucket.
    """
    s3 = boto.connect_s3()
    
    return s3.get_bucket(app_config.ASSETS_S3_BUCKET)

def _assets_confirm(local_path):
    """
    Check with user about whether to keep local or remote file.
    """
    print '--> This file has been changed locally and on S3.'
    answer = prompt('Take remote [r] Take local [l] Take all remote [ra] Take all local [la] cancel', default='c')

    if answer == 'r':
        return ('remote', False)
    elif answer == 'l':
        return ('local', False)
    elif answer == 'ra':
        return ('remote', True)
    elif answer == 'la':
        return ('local', True)
        
    return (None, False)

def _assets_upload_confirm():
    print '--> This file does not exist on S3.'
    answer = prompt('Upload local copy [u] Delete local copy [d] Upload all [ua] Delete all [da] cancel', default='c')

    if answer == 'u':
        return ('upload', False)
    elif answer == 'd':
        return ('delete', False)
    elif answer == 'ua':
        return ('upload', True)
    elif answer == 'da':
        return ('delete', True)

    return (None, False) 

def _assets_download(s3_key, local_path):
    """
    Utility method to download a single asset from S3.
    """
    print '--> Downloading!' 

    dirname = os.path.dirname(local_path)

    if not (os.path.exists(dirname)):
        os.makedirs(dirname)
    
    s3_key.get_contents_to_filename(local_path)

def _assets_upload(local_path, s3_key):
    """
    Utility method to upload a single asset to S3.
    """
    print '--> Uploading!'
    
    with open(local_path, 'rb') as f:
        local_md5 = s3_key.compute_md5(f)[0]

    s3_key.set_metadata('md5', local_md5)
    s3_key.set_contents_from_filename(local_path)

def _assets_delete(local_path, s3_key):
    """
    Utility method to delete assets both locally and remotely.
    """
    print '--> Deleting!'

    s3_key.delete()
    os.remove(local_path)
