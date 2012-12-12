#!/usr/bin/env python

import csv
import getpass
import json
import os
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

    repo_url = re.search('(https.+)\w', gitconfig).group(0)
    base, repo = os.path.split(repo_url)
    repo_username = os.path.split(base)[-1]
    repo_name = os.path.splitext(repo)[0]

    return '%s/%s' % (repo_username, repo_name)

def delete_existing_labels(auth):
    """
    Delete labels currently on the repository
    """
    url = 'https://api.github.com/repos/%s/labels' % get_repo_path()

    response = requests.get(url)
    labels = json.loads(response.content)

    print 'Deleting %i labels' % len(labels)

    for label in labels:
        print 'Deleting label %s' % label['name']

        requests.delete(url + '/' + label['name'])

def create_default_labels(auth):
    """
    Creates default labels in a Github repo
    """
    url = 'https://api.github.com/repos/%s/repo/labels' % get_repo_path()

    with open('etc/default_labels.csv') as f:
        labels = list(csv.DictReader(f))

    print 'Creating %i labels' % len(labels)

    for label in labels:
        print 'Creating label "%s"' % label['name']
        data = json.dumps(label)

        requests.post(url, data=data, auth=auth)

