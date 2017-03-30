#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import copy
from cStringIO import StringIO
from fnmatch import fnmatch
import gzip
import hashlib
import logging
import mimetypes
import os

from boto.s3.key import Key

import app_config
import utils

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

GZIP_FILE_TYPES = ['.html', '.js', '.json', '.css', '.xml']


def deploy_file(bucket, src, dst, headers={}, public=True):
    """
    Deploy a single file to S3, if the local version is different.
    """
    k = bucket.get_key(dst)
    s3_md5 = None

    if k:
        s3_md5 = k.etag.strip('"')
    else:
        k = Key(bucket)
        k.key = dst

    file_headers = copy.copy(headers)

    if 'Content-Type' not in headers:
        file_headers['Content-Type'] = mimetypes.guess_type(src)[0]
        if file_headers['Content-Type'] == 'text/html':
            # Force character encoding header
            file_headers['Content-Type'] = '; '.join([
                file_headers['Content-Type'],
                'charset=utf-8'])

    # Define policy
    if public:
        policy = 'public-read'
    else:
        policy = 'private'

    # Gzip file
    if os.path.splitext(src)[1].lower() in GZIP_FILE_TYPES:
        file_headers['Content-Encoding'] = 'gzip'

        with open(src, 'rb') as f_in:
            contents = f_in.read()

        output = StringIO()
        f_out = gzip.GzipFile(filename=dst, mode='wb', fileobj=output, mtime=0)
        f_out.write(contents)
        f_out.close()

        local_md5 = hashlib.md5()
        local_md5.update(output.getvalue())
        local_md5 = local_md5.hexdigest()

        if local_md5 == s3_md5:
            logger.info('Skipping %s (has not changed)' % src)
        else:
            logger.info('Uploading %s --> %s (gzipped)' % (src, dst))
            k.set_contents_from_string(output.getvalue(), file_headers, policy=policy)
    # Non-gzip file
    else:
        with open(src, 'rb') as f:
            local_md5 = hashlib.md5()
            local_md5.update(f.read())
            local_md5 = local_md5.hexdigest()

        if local_md5 == s3_md5:
            logger.info('Skipping %s (has not changed)' % src)
        else:
            logger.info('Uploading %s --> %s' % (src, dst))
            k.set_contents_from_filename(src, file_headers, policy=policy)

def deploy_folder(bucket_name, src, dst, headers={}, ignore=[]):
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

    if bucket_name == app_config.STAGING_S3_BUCKET:
        public = False
    else:
        public = True
    bucket = utils.get_bucket(bucket_name)
    logger.info(dst)
    for src, dst in to_deploy:
        deploy_file(bucket, src, dst, headers, public=public)


def delete_folder(bucket_name, dst):
    """
    Delete a folder from S3.
    """
    bucket = utils.get_bucket(bucket_name)

    for key in bucket.list(prefix='%s/' % dst):
        logger.info('Deleting %s' % (key.key))

        key.delete()
