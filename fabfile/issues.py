#!/usr/bin/env python

"""
Commands that integrate with Github issues.
"""

from fabric.api import task

import app_config
from etc import github

@task
def bootstrap():
    """
    Bootstraps Github issues with default configuration.
    """
    if app_config.PROJECT_SLUG == '$NEW_PROJECT_SLUG':
        print 'You can\'t run the issues bootstrap until you\'ve set PROJECT_SLUG in app_config.py!'
        return

    auth = github.get_auth()
    github.delete_existing_labels(auth)
    github.create_labels(auth)
    github.create_tickets(auth)
    github.create_milestones(auth)
    github.create_hipchat_hook(auth)

@task
def from_file(path):
    """
    Import a list of a issues from any CSV formatted like default_tickets.csv.
    """
    auth = github.get_auth()
    github.create_tickets(auth, path)

