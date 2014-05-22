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

def js():
    """
    Render COPY to copy.js.
    """
    from static import _copy_js

    response = _copy_js()
    js = response[0]

    with open('www/js/copy.js', 'w') as f:
        f.write(js)

