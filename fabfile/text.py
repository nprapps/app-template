#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

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
    else:
        g = GoogleDoc(key=app_config.COPY_GOOGLE_DOC_KEY)
        g.get_auth()
        g.get_document()
