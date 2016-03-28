#!/usr/bin/env python

"""
Commands related to syncing copytext from Google Docs.
"""

import app_config
import logging

from fabric.api import task
from oauth import get_document, get_credentials

logging.basicConfig(format=app_config.LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(app_config.LOG_LEVEL)

@task(default=True)
def update():
    """
    Downloads a Google Doc as an Excel file.
    """
    if app_config.COPY_GOOGLE_DOC_KEY == None:
        logger.warn('You have set COPY_GOOGLE_DOC_KEY to None. If you want to use a Google Sheet, set COPY_GOOGLE_DOC_KEY  to the key of your sheet in app_config.py')
        return

    credentials = get_credentials()
    if not credentials:
        print logger.warn('No Google OAuth credentials file found.')
        print logger.warn('Run `fab app` and visit `http://localhost:8000` to generate credentials.')
        return

    get_document(app_config.COPY_GOOGLE_DOC_KEY, app_config.COPY_PATH)
