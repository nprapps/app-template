#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

from fabric.api import task

import app_config
from etc.gdocs import GoogleDoc

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    doc = {}
    url = app_config.COPY_GOOGLE_DOC_URL
    bits = url.split('key=')
    bits = bits[1].split('&')
    doc['key'] = bits[0]

    g = GoogleDoc(**doc)
    g.get_auth()
    g.get_document()

