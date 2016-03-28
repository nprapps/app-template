#!/usr/bin/env python

import boto

from boto.s3.connection import OrdinaryCallingFormat
from fabric.api import local, task

"""
Utilities used by multiple commands.
"""

from fabric.api import prompt

def confirm(message):
    """
    Verify a users intentions.
    """
    answer = prompt(message, default="Not at all")

    if answer.lower() not in ('y', 'yes', 'buzz off', 'screw you'):
        exit()


def get_bucket(bucket_name):
    """
    Established a connection and gets s3 bucket
    """

    if '.' in bucket_name:
        s3 = boto.connect_s3(calling_format=OrdinaryCallingFormat())
    else:
        s3 = boto.connect_s3()

    return s3.get_bucket(bucket_name)

@task
def install_font(force='true'):
    """
    Install font
    """
    print 'Installing font'
    if force != 'true':
        try:
            with open('www/css/icon/elections16.css') and open('www/css/font/elections16.svg'):
                print 'Font installed, skipping.'
                return
        except IOError:
            pass

    local('node_modules/fontello-cli/bin/fontello-cli install --config fontello/config.json --css www/css/icon --font www/css/font/')


@task
def open_font():
    """
    Open font in Fontello GUI in your browser
    """
    local('node_modules/fontello-cli/bin/fontello-cli open --config fontello/config.json')
