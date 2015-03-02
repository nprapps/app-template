#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

import os

from fabric.api import task
from termcolor import colored

import app_config
from etc.gdocs import GoogleDoc
from oauth import get_credentials

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    if app_config.COPY_GOOGLE_DOC_KEY == None:
        print colored('You have set COPY_GOOGLE_DOC_KEY to None. If you want to use a Google Sheet, set COPY_GOOGLE_DOC_KEY  to the key of your sheet in app_config.py', 'blue')
        return

    cred_file = os.path.expanduser(app_config.GOOGLE_OAUTH_CREDENTIALS_PATH)
    if not os.path.isfile(cred_file):
        print 'No Google OAuth credentials file found.'
        print 'Run `fab app` and visit `http://localhost:8000` to generate credentials.'
        return

    doc = {
        'key': app_config.COPY_GOOGLE_DOC_KEY,
        'file_path': app_config.COPY_PATH,
        'credentials': get_credentials(),
        'authomatic': app_config.authomatic,
    }
    g = GoogleDoc(**doc)
    g.get_document()
