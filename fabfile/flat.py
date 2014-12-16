#!/usr/bin/env python

from cStringIO import StringIO
from fnmatch import fnmatch
import gzip
import hashlib
import mimetypes
import os

import boto
from boto.s3.key import Key

import app_config

GZIP_FILE_TYPES = ['.html', '.js', '.json', '.css', '.xml']

class FakeTime:
    def time(self):
        return 1261130520.0

# Hack to override gzip's time implementation
# See: http://stackoverflow.com/questions/264224/setting-the-gzip-timestamp-from-python
gzip.time = FakeTime()

def deploy_file(connection, src, dst, max_age):
    """
    Deploy a single file to S3, if the local version is different.
    """
    bucket = connection.get_bucket(app_config.S3_BUCKET['bucket_name'])
    
    k = bucket.get_key(dst)
    s3_md5 = None

    if k:
        s3_md5 = k.etag.strip('"')
    else:
        k = Key(bucket) 
        k.key = dst

    headers = {
        'Content-Type': mimetypes.guess_type(src)[0],
        'Cache-Control': 'max-age=%i' % max_age 
    }

    # Gzip file
    if os.path.splitext(src)[1].lower() in GZIP_FILE_TYPES:
        headers['Content-Encoding'] = 'gzip'
    
        with open(src, 'rb') as f_in:
            contents = f_in.read()

        output = StringIO()
        f_out = gzip.GzipFile(filename=dst, mode='wb', fileobj=output)
        f_out.write(contents)
        f_out.close()
    
        local_md5 = hashlib.md5()
        local_md5.update(output.getvalue())
        local_md5 = local_md5.hexdigest()
        
        if local_md5 == s3_md5:
            print 'Skipping %s (has not changed)' % src
        else:
            print 'Uploading %s --> %s (gzipped)' % (src, dst)
            k.set_contents_from_string(output.getvalue(), headers, policy='public-read')
    # Non-gzip file
    else:
        with open(src, 'rb') as f:
            local_md5 = hashlib.md5()
            local_md5.update(f.read())
            local_md5 = local_md5.hexdigest()
        
        if local_md5 == s3_md5:
            print 'Skipping %s (has not changed)' % src
        else:
            print 'Uploading %s --> %s' % (src, dst)
            k.set_contents_from_filename(src, headers, policy='public-read')

def deploy_folder(src, dst, max_age=app_config.DEFAULT_MAX_AGE, ignore=[]):
    """
    Deploy a folder to S3, checking each file to see if it has changed.
    """
    to_deploy = []

    for local_path, subdirs, filenames in os.walk(src, topdown=True):
        rel_path = os.path.relpath(local_path, src)

        for name in filenames:
            if name.startswith('.'):
                continue
                
            src_path = os.path.join(local_path, name)

            skip = False

            for pattern in ignore:
                if fnmatch(src_path, pattern):
                    skip = True
                    break

            if skip:
                continue

            if rel_path == '.':
                dst_path = os.path.join(dst, name)
            else:
                dst_path = os.path.join(dst, rel_path, name)

            to_deploy.append((src_path, dst_path))

    s3 = boto.connect_s3() 

    for src, dst in to_deploy:
        deploy_file(s3, src, dst, max_age)

def delete_folder(dst):
    """
    Delete a folder from S3.
    """
    s3 = boto.connect_s3() 
    
    bucket = s3.get_bucket(app_config.S3_BUCKET['bucket_name'])

    for key in bucket.list(prefix='%s/' % dst):
        print 'Deleting %s' % (key.key)

        key.delete()

