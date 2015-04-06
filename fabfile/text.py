#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

import app_config
import os

from fabric.api import task
from oauth import get_document, get_credentials
from termcolor import colored

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    if app_config.COPY_GOOGLE_DOC_KEY == None:
        print colored('You have set COPY_GOOGLE_DOC_KEY to None. If you want to use a Google Sheet, set COPY_GOOGLE_DOC_KEY  to the key of your sheet in app_config.py', 'blue')
        return

    credentials = get_credentials()
    if not credentials:
        print colored('No Google OAuth credentials file found.', 'yellow')
        print colored('Run `fab app` and visit `http://localhost:8000` to generate credentials.', 'yellow')
        return

    get_document(app_config.COPY_GOOGLE_DOC_KEY, app_config.COPY_PATH)
