#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

import os

from fabric.api import task
from termcolor import colored

import app_config
from etc.gdocs import GoogleDoc

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    if app_config.COPY_GOOGLE_DOC_KEY == None:
        print colored('You have set COPY_GOOGLE_DOC_KEY to None. If you want to use a Google Sheet, set COPY_GOOGLE_DOC_KEY  to the key of your sheet in app_config.py', 'blue')
        return
    elif not os.environ.get('APPS_GOOGLE_OAUTH'):
        print 'You have not set the `APPS_GOOGLE_OAUTH` environment variable.'
        print 'Run `fab app` and visit `http://localhost:8000` to generate credentials.'
    else:
        doc = {
            'key': app_config.COPY_GOOGLE_DOC_KEY,
            'file_path': app_config.COPY_PATH,
            'credentials': os.environ.get('APPS_GOOGLE_OAUTH'),
            'authomatic': app_config.authomatic,
        }
        g = GoogleDoc(**doc)
        g.get_document()
