#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
Commands that ease the interaction with the app google spreadsheet
"""
from fabric.api import task
import app_config
import webbrowser

SPREADSHEET_VIEW_TEMPLATE = 'https://docs.google.com/spreadsheet/ccc?key=%s#gid=1'

@task(default=True)
def open_spreadsheet(key=None):
    """
    Open the spreadsheet associated with the app
    """
    if key:
        pass
    elif not app_config.COPY_GOOGLE_DOC_KEY:
        print 'There seems to be no spreadsheet linked to this app. (COPY_GOOGLE_DOC_KEY is not defined in app_config.py.)'
        return
    else:
        key = app_config.COPY_GOOGLE_DOC_KEY

    spreadsheet_url = SPREADSHEET_VIEW_TEMPLATE % key
    webbrowser.open_new(spreadsheet_url)
