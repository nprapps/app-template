#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
Cron jobs
"""

from fabric.api import local, require, task

@task
def test():
    """
    Example cron task. Note we use "local" instead of "run"
    because this will run on the server.
    """
    require('settings', provided_by=['production', 'staging'])

    local('echo $DEPLOYMENT_TARGET > /tmp/cron_test.txt')

