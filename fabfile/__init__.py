#!/usr/bin/env python

from fabric.api import local, require, settings, task
from fabric.state import env
from termcolor import colored

import app_config

# Other fabfiles
import assets
import data
import flat
import issues
import render
import text
import utils

if app_config.DEPLOY_TO_SERVERS:
    import servers

if app_config.DEPLOY_CRONTAB:
    import cron_jobs

# Bootstrap can only be run once, then it's disabled
if app_config.PROJECT_SLUG == '$NEW_PROJECT_SLUG':
    import bootstrap

"""
Base configuration
"""
env.user = app_config.SERVER_USER
env.forward_agent = True

env.hosts = []
env.settings = None

"""
Environments

Changing environment requires a full-stack test.
An environment points to both a server and an S3
bucket.
"""
@task
def production():
    """
    Run as though on production.
    """
    env.settings = 'production'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def staging():
    """
    Run as though on staging.
    """
    env.settings = 'staging'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

"""
Branches

Changing branches requires deploying that branch to a host.
"""
@task
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

@task
def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

@task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

"""
Running the app
"""
@task
def app(port='8000'):
    """
    Serve app.py.
    """
    local('gunicorn -b 0.0.0.0:%s --debug --reload app:wsgi_app' % port)

@task
def public_app(port='8001'):
    """
    Serve public_app.py.
    """
    local('gunicorn -b 0.0.0.0:%s --debug --reload public_app:wsgi_app' % port)

@task
def tests():
    """
    Run Python unit tests.
    """
    local('nosetests')

"""
Deployment

Changes to deployment requires a full-stack test. Deployment
has two primary functions: Pushing flat files to S3 and deploying
code to a remote server if required.
"""
@task
def update():
    """
    Update all application data not in repository (copy, assets, etc).
    """
    text.update()
    assets.sync()
    data.update()

@task
def deploy(remote='origin'):
    """
    Deploy the latest app to S3 and, if configured, to our servers.
    """
    require('settings', provided_by=[production, staging])

    if app_config.DEPLOY_TO_SERVERS:
        require('branch', provided_by=[stable, master, branch])

        if (app_config.DEPLOYMENT_TARGET == 'production' and env.branch != 'stable'):
            utils.confirm(
                colored("You are trying to deploy the '%s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env.branch, "red")
            )

        servers.checkout_latest(remote)

        servers.fabcast('text.update')
        servers.fabcast('assets.sync')
        servers.fabcast('data.update')

        if app_config.DEPLOY_CRONTAB:
            servers.install_crontab()

        if app_config.DEPLOY_SERVICES:
            servers.deploy_confs()

    update()
    render.render_all()

    # Clear files that should never be deployed
    local('rm -rf www/live-data')

    flat.deploy_folder(
        'www',
        app_config.PROJECT_SLUG,
        max_age=app_config.DEFAULT_MAX_AGE,
        ignore=['www/assets/*']
    )

    flat.deploy_folder(
        'www/assets',
        '%s/assets' % app_config.PROJECT_SLUG,
        max_age=app_config.ASSETS_MAX_AGE
    )


"""
Destruction

Changes to destruction require setup/deploy to a test host in order to test.
Destruction should remove all files related to the project from both a remote
host and S3.
"""

@task
def shiva_the_destroyer():
    """
    Deletes the app from s3
    """
    require('settings', provided_by=[production, staging])

    utils.confirm(
        colored("You are about to destroy everything deployed to %s for this project.\nDo you know what you're doing?')" % app_config.DEPLOYMENT_TARGET, "red")
    )

    with settings(warn_only=True):
        flat.delete_folder(app_config.PROJECT_SLUG) 

        if app_config.DEPLOY_TO_SERVERS:
            servers.delete_project()

            if app_config.DEPLOY_CRONTAB:
                servers.uninstall_crontab()

            if app_config.DEPLOY_SERVICES:
                servers.nuke_confs()

