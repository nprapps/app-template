#!/usr/bin/env python

import csv

from fabric.api import *
from jinja2 import Environment, FileSystemLoader

import app_config

"""
Base configuration
"""
env.project_name = app_config.PROJECT_NAME 
env.deployed_name = app_config.DEPLOYED_NAME
env.deploy_to_servers = False
env.repo_url = 'git@github.com:nprapps/%(project_name)s.git' % env
env.alt_repo_url = 'git@bitbucket.org:nprapps/%(project_name)s.git' % env
env.user = 'ubuntu'
env.python = 'python2.7'
env.path = '/home/%(user)s/apps/%(project_name)s' % env
env.repo_path = '%(path)s/repository' % env
env.virtualenv_path = '%(path)s/virtualenv' % env
env.forward_agent = True

"""
Environments
"""
def production():
    env.settings = 'production'
    env.s3_buckets = app_config.PRODUCTION_S3_BUCKETS
    env.hosts = app_config.PRODUCTION_SERVERS

def staging():
    env.settings = 'staging'
    env.s3_buckets = app_config.STAGING_S3_BUCKETS
    env.hosts = app_config.PRODUCTION_SERVERS

"""
Branches
"""
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

def _confirm_branch():
    """
    Confirm a production deployment.
    """
    if (env.settings == 'production' and env.branch != 'stable'):
        answer = prompt("You are trying to deploy the '%(branch)s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env, default="Not at all")
        if answer not in ('y','Y','yes','Yes','buzz off','screw you'):
            exit()

"""
Template-specific functions
"""
def _render_template(template, data={}):
    """
    Helper function for rendering a jinja template.
    """
    jinja = Environment(loader=FileSystemLoader('templates'))
    template = jinja.get_template(template)

    data['project_name'] = env.project_name

    return template.render(data)

def make_index():
    """
    Generate a basic index.html.
    """
    with open('www/index.html', 'w') as f:
        f.write(_render_template('base.html'))

def make_table(filename='data/example.csv'):
    """
    Rewrite index.html with a table from a CSV.
    """
    with open(filename) as f:
        reader = csv.reader(f)
        header = reader.next()

        table = _render_template('table.html', {
            'columns': header,
            'data': reader
        })

    with open('www/index.html', 'w') as f:
        f.write(table)

"""
Setup
"""
def setup():
    """
    Setup servers for deployment.
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])

    setup_directories()
    setup_virtualenv()
    clone_repo()
    checkout_latest()
    install_requirements()

def setup_directories():
    """
    Create server directories.
    """
    require('settings', provided_by=[production, staging])

    run('mkdir -p %(path)s' % env)

def setup_virtualenv():
    """
    Setup a server virtualenv.
    """
    require('settings', provided_by=[production, staging])

    run('virtualenv -p %(python)s --no-site-packages %(virtualenv_path)s' % env)
    run('source %(virtualenv_path)s/bin/activate' % env)

def clone_repo():
    """
    Clone the source repository.
    """
    require('settings', provided_by=[production, staging])

    run('git clone %(repo_url)s %(repo_path)s' % env)

    if env.get('alt_repo_url', None):
        run('git remote add bitbucket %(alt_repo_url)s' % env)

def checkout_latest(remote='origin'):
    """
    Checkout the latest source.
    """
    require('settings', provided_by=[production, staging])

    env.remote = remote

    run('cd %(repo_path)s; git fetch %(remote)s' % env)
    run('cd %(repo_path)s; git checkout %(branch)s; git pull %(remote)s %(branch)s' % env)


def install_requirements():
    """
    Install the latest requirements.
    """
    require('settings', provided_by=[production, staging])

    run('%(virtualenv_path)s/bin/pip install -U -r %(repo_path)s/requirements.txt' % env)

"""
Deployment
"""
def _deploy_to_s3():
    """
    Deploy the gzipped stuff to
    """
    build_assets()

    s3cmd = 's3cmd -P --add-header=Cache-Control:max-age=5 --add-header=Content-encoding:gzip --guess-mime-type --recursive --exclude .webassets-cache/* sync gzip/ %s'

    for bucket in env.s3_buckets:
        env.s3_bucket = bucket
        local(s3cmd % ('s3://%(s3_bucket)s/%(deployed_name)s/' % env))

def _gzip_www():
    """
    Gzips everything in www and puts it all in gzip
    """
    local('python gzip_www.py')

def deploy(remote='origin'):
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])

    _confirm_branch()
    _gzip_www()
    _deploy_to_s3()

    if env.get('deploy_to_servers', False):
        checkout_latest(remote)
    
"""
Local workflow
"""
def compile_less():
    """
    Compile less stylesheets to CSS. 
    """
    local('node_modules/.bin/lessc less/app.less > www/css/app.css')

def watch_less():
    """
    Watch LESS stylesheets for changes and recompile as needed.
    """
    local('node_modules/.bin/lesswatcher --compiler node_modules/.bin/lessc --less_dir less --css_dir www/css/')

def compile_jst():
    """
    Compile JST.
    """
    local('node_modules/.bin/jst --template underscore www/jst/ www/js/templates.js')

def watch_jst():
    """
    Watch JST for changes and recompile as needed.
    """
    local('node_modules/.bin/jst --template underscore www/jst/ www/js/templates.js --watch true')

def build_assets():
    """
    Build consolidated versions of CSS and JS assets.
    """
    compile_jst()
    compile_less()
    local('webassets -m assets_env build')

def watch_assets():
    """
    Watch CSS and JS for changes and rebuild assets as necessary.
    """
    compile_jst()
    compile_less()
    local('webassets -m assets_env watch')

"""
Destruction
"""
def shiva_the_destroyer():
    """
    Deletes the app from s3
    """
    with settings(warn_only=True):
        s3cmd = 's3cmd del --recursive %s' % env
        
        for bucket in env.s3_buckets:
            env.s3_bucket = bucket
            local(s3cmd % ('s3://%(s3_bucket)s/%(deployed_name)s' % env))

        if env.get('alt_s3_bucket', None):
            local(s3cmd % ('s3://%(alt_s3_bucket)s/%(deployed_name)s' % env))

        if env.get('deploy_to_servers', False):
            run('rm -rf %(path)s' % env)
