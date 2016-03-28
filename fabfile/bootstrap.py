#!/usr/bin/env python


"""
Bootstrap the app-template. This module disables itself
after execution.
"""

import app_config
import json
import logging
import os
import subprocess
import utils
import uuid
import webbrowser

from distutils.spawn import find_executable
from fabric.api import execute, local, prompt, task
from oauth import get_credentials
from time import sleep

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

SPREADSHEET_COPY_URL_TEMPLATE = 'https://www.googleapis.com/drive/v2/files/%s/copy'
SPREADSHEET_VIEW_TEMPLATE = 'https://docs.google.com/spreadsheet/ccc?key=%s#gid=1'

@task(default=True)
def go(github_username=app_config.GITHUB_USERNAME, repository_name=None):
    """
    Execute the bootstrap tasks for a new project.
    """
    check_credentials()
    config_files = ' '.join(['PROJECT_README.md', 'app_config.py', 'crontab'])

    config = {}
    config['$NEW_PROJECT_SLUG'] = os.getcwd().split('/')[-1]
    config['$NEW_REPOSITORY_NAME'] = repository_name or config['$NEW_PROJECT_SLUG']
    config['$NEW_PROJECT_FILENAME'] = config['$NEW_PROJECT_SLUG'].replace('-', '_')
    config['$NEW_DISQUS_UUID'] = str(uuid.uuid1())

    utils.confirm("Have you created a Github repository named \"%s\"?" % config['$NEW_REPOSITORY_NAME'])

    # Create the spreadsheet
    title = '%s COPY' % config['$NEW_PROJECT_SLUG']
    new_spreadsheet_key = create_spreadsheet(title)
    if new_spreadsheet_key:
        config[app_config.COPY_GOOGLE_DOC_KEY] = new_spreadsheet_key
    else:
        logger.warn('No spreadsheet created, you will need to update COPY_GOOGLE_DOC_KEY manually.')

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

    if new_spreadsheet_key:
        logger.info('You can view your COPY spreadsheet at:')
        logger.info(SPREADSHEET_VIEW_TEMPLATE % new_spreadsheet_key)


def check_credentials():
    """
    Check credentials and spawn server and browser if not
    """
    credentials = get_credentials()
    if not credentials or 'https://www.googleapis.com/auth/drive' not in credentials.config['google']['scope']:
        try:
            with open(os.devnull, 'w') as fnull:
                logger.info('Credentials were not found or permissions were not correct. Automatically opening a browser to authenticate with Google.')
                gunicorn = find_executable('gunicorn')
                process = subprocess.Popen([gunicorn, '-b', '127.0.0.1:8888', 'app:wsgi_app'], stdout=fnull, stderr=fnull)
                webbrowser.open_new('http://127.0.0.1:8888/oauth')
                logger.info('Waiting...')
                while not credentials:
                    try:
                        credentials = get_credentials()
                        sleep(1)
                    except ValueError:
                        continue
                logger.info('Successfully authenticated!')
                process.terminate()
        except KeyboardInterrupt:
            logger.info('\nCtrl-c pressed. Later, skater!')
            exit()

def create_spreadsheet(title):
    """
    Copy the COPY spreadsheet
    """
    kwargs = {
        'credentials': get_credentials(),
        'url': SPREADSHEET_COPY_URL_TEMPLATE % app_config.COPY_GOOGLE_DOC_KEY,
        'method': 'POST',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'title': title,
        }),
    }

    resp = app_config.authomatic.access(**kwargs)
    if resp.status == 200:
        spreadsheet_key = resp.data['id']
        logger.info('New spreadsheet created with key %s' % spreadsheet_key)
        return spreadsheet_key
    else:
        logger.info('Error creating spreadsheet (status code %s) with message %s' % (resp.status, resp.reason))
        return None
