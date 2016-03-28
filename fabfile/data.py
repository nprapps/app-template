#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from fabric.api import task

@task(default=True)
def update():
    """
    Stub function for updating app-specific data.
    """
    pass
