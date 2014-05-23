#!/usr/bin/env python

from fabric.api import task

import app_config
from etc.gdocs import GoogleDoc

@task
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    doc = {}
    doc['key'] = app_config.COPY_GOOGLE_DOC_KEY

    g = GoogleDoc(**doc)
    g.get_auth()
    g.get_document()

