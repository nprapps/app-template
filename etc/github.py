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

    auth = HTTPBasicAuth(username, password)

    # Test auth by requesting repo events
    response = requests.get('https://api.github.com/notifications', auth=auth)

    if response.status_code == 401:
        raise Exception('Invalid username or password')

    return auth

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

def create_labels(auth, filename='etc/default_labels.csv'):
    """
    Creates labels in Github issues.
    """
    url = 'https://api.github.com/repos/%s/labels' % get_repo_path()

    with open(filename) as f:
        labels = list(csv.DictReader(f))

    print 'Creating %i labels' % len(labels)

    for label in labels:
        print 'Creating label "%s"' % label['name']
        data = json.dumps(label)

        requests.post(url, data=data, auth=auth)

def create_tickets(auth, filename='etc/default_tickets.csv'):
    """
    Creates tickets in Github issues.
    """
    url = 'https://api.github.com/repos/%s/issues' % get_repo_path()

    with open(filename) as f:
        tickets = list(csv.DictReader(f))

    print 'Creating %i tickets' % len(tickets)

    for ticket in tickets:
        print 'Creating ticket "%s"' % ticket['title']

        if ticket['labels']:
            ticket['labels'] = ticket['labels'].split(',')
        else:
            ticket['labels'] = []

        ticket['labels'].append('Default Ticket')

        data = json.dumps(ticket)

        requests.post(url, data=data, auth=auth) 

def create_milestones(auth, filename='etc/default_milestones.csv'):
    """
    Creates milestones in Github issues.
    """
    url = 'https://api.github.com/repos/%s/milestones' % get_repo_path()

    with open(filename) as f:
        milestones = list(csv.DictReader(f))

    print 'Creating %i milestones' % len(milestones)

    for milestone in milestones:
        print 'Creating milestone "%s"' % milestone['title']

        data = json.dumps(milestone)

        requests.post(url, data=data, auth=auth) 

def create_hipchat_hook(auth):
    """
    Sets up hipchat to notify our room when changes are made.
    """
    url = 'https://api.github.com/repos/%s/hooks' % get_repo_path()

    print 'Creating Hipchat hook'

    auth_token = os.environ.get('HIPCHAT_AUTH_TOKEN', None)
    room = os.environ.get('HIPCHAT_ROOM_ID', None)

    if (not auth_token or not room):
        print 'Skipping! (Not configured.)'
        return

    data = json.dumps({
        'name': 'hipchat',
        'active': True,
        'config': {
            'auth_token': auth_token,
            'restrict_to_branch': '',
            'room': room,
            'notify': 1,
            'quiet_fork': 0,
            'quiet_watch': 0,
            'quiet_comments': 0
        }
    })

    requests.post(url, data=data, auth=auth)
