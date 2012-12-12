#!/usr/bin/env python

import csv
import getpass
import json
import re

import requests
from requests.auth import HTTPBasicAuth

def get_auth():
    """
    Construct a basic auth object from a username and password
    """
    username = raw_input('Username:')
    password = getpass.getpass('Password:')

    return HTTPBasicAuth(username, password)

def get_repo_path():
    """
    Extract the repository url from the gitconfig file.
    """
    with open('.git/config') as f:
        gitconfig = f.read()

    match = re.search('(git@github.com:|https://github.com/)(.+)/(.+).git', gitconfig)    
    repo_username = match.group(2)
    repo_name = match.group(3)

    return '%s/%s' % (repo_username, repo_name)

def delete_existing_labels(auth):
    """
    Delete labels currently on the repository
    """
    url = 'https://api.github.com/repos/%s/labels' % get_repo_path()

    response = requests.get(url, auth=auth)
    labels = json.loads(response.content)

    print 'Deleting %i labels' % len(labels)

    for label in labels:
        print 'Deleting label %s' % label['name']

        requests.delete(url + '/' + label['name'], auth=auth)

def create_default_labels(auth):
    """
    Creates default labels in a Github repo
    """
    url = 'https://api.github.com/repos/%s/labels' % get_repo_path()

    with open('etc/default_labels.csv') as f:
        labels = list(csv.DictReader(f))

    print 'Creating %i labels' % len(labels)

    for label in labels:
        print 'Creating label "%s"' % label['name']
        data = json.dumps(label)

        requests.post(url, data=data, auth=auth)

