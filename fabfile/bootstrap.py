#!/usr/bin/env python


"""
Bootstrap the app-template. This module disables itself
after execution.
"""

import os
import uuid

from fabric.api import execute, local, task
from oauth import get_credentials

import app_config
import utils

SPREADSHEET_COPY_TEMPLATE = 'https://www.googleapis.com/drive/v2/files/%s/copy'

@task(default=True)
def go(github_username=app_config.GITHUB_USERNAME, repository_name=None):
    """
    Execute the bootstrap tasks for a new project.
    """
    config_files = ' '.join(['PROJECT_README.md', 'app_config.py', 'crontab'])

    config = {}
    config['$NEW_PROJECT_SLUG'] = os.getcwd().split('/')[-1]
    config['$NEW_REPOSITORY_NAME'] = repository_name or config['$NEW_PROJECT_SLUG']
    config['$NEW_PROJECT_FILENAME'] = config['$NEW_PROJECT_SLUG'].replace('-', '_')
    config['$NEW_DISQUS_UUID'] = str(uuid.uuid1())

    utils.confirm("Have you created a Github repository named \"%s\"?" % config['$NEW_REPOSITORY_NAME'])

    for k, v in config.items():
        local('sed -i "" \'s|%s|%s|g\' %s' % (k, v, config_files))

    local('rm -rf .git')
    local('git init')
    local('mv PROJECT_README.md README.md')
    local('rm *.pyc')
    local('rm LICENSE')
    local('git add .')
    local('git add -f www/assets/assetsignore')
    local('git commit -am "Initial import from app-template."')
    local('git remote add origin git@github.com:%s/%s.git' % (github_username, config['$NEW_REPOSITORY_NAME']))
    local('git push -u origin master')

    # Update app data
    execute('update')

@task
def create_spreadsheet():
    credentials = get_credentials()
    kwargs = {
        'credentials': credentials,
        'url': SPREADSHEET_COPY_TEMPLATE % app_config.COPY_GOOGLE_DOC_KEY,
        'method': 'POST',
    }

    resp = app_config.authomatic.access(**kwargs)
