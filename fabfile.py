#!/usr/bin/env python

from glob import glob
import os

from fabric.api import *
from jinja2 import Template

import app
import app_config
from etc import github

"""
Base configuration
"""
env.deployed_name = app_config.PROJECT_SLUG
env.repo_name = app_config.REPOSITORY_NAME

env.deploy_to_servers = True
env.install_crontab = False
env.deploy_web_services = True

env.repo_url = 'git@github.com:nprapps/%(repo_name)s.git' % env
env.alt_repo_url = None  # 'git@bitbucket.org:nprapps/%(repo_name)s.git' % env
env.user = 'ubuntu'
env.python = 'python2.7'
env.path = '/home/%(user)s/apps/%(deployed_name)s' % env
env.repo_path = '%(path)s/repository' % env
env.virtualenv_path = '%(path)s/virtualenv' % env
env.forward_agent = True

SERVICES = [
    ('nginx', '/etc/nginx/sites-available/'),
    ('uwsgi', '/etc/init/')
]

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
    env.hosts = app_config.STAGING_SERVERS

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

"""
Template-specific functions
"""
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('less/*.less'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = 'www/css/%s.less.css' % name

        local('node_modules/.bin/lessc %s %s' % (path, out_path))

def jst():
    """
    Render Underscore templates to a JST package.
    """
    local('node_modules/.bin/jst --template underscore jst www/js/templates.js')

def download_copy():
    """
    Downloads a Google Doc as an .xls file.
    """
    base_url = 'https://docs.google.com/spreadsheet/pub?key=%s&output=xls'
    doc_url = base_url % app_config.COPY_GOOGLE_DOC_KEY
    local('curl -o data/copy.xls "%s"' % doc_url)

def update_copy():
    """
    Fetches the latest Google Doc and updates local JSON.
    """
    download_copy()

def app_config_js():
    """
    Render app_config.js to file.
    """
    from app import _app_config_js

    response = _app_config_js()
    js = response[0]

    with open('www/js/app_config.js', 'w') as f:
        f.write(js)

def render():
    """
    Render HTML templates and compile assets.
    """
    from flask import g

    update_copy()
    less()
    jst()

    # Fake out deployment target
    app_config.configure_targets(env.get('settings', None))

    app_config_js()

    compiled_includes = []

    for rule in app.app.url_map.iter_rules():
        rule_string = rule.rule
        name = rule.endpoint

        if name == 'static' or name.startswith('_'):
            print 'Skipping %s' % name
            continue

        if rule_string.endswith('/'):
            filename = 'www' + rule_string + 'index.html'
        elif rule_string.endswith('.html'):
            filename = 'www' + rule_string
        else:
            print 'Skipping %s' % name
            continue

        dirname = os.path.dirname(filename)

        if not (os.path.exists(dirname)):
            os.makedirs(dirname)

        print 'Rendering %s' % (filename)

        with app.app.test_request_context(path=rule_string):
            g.compile_includes = True
            g.compiled_includes = compiled_includes

            view = app.__dict__[name]
            content = view()

            compiled_includes = g.compiled_includes

        with open(filename, 'w') as f:
            f.write(content.encode('utf-8'))

    # Un-fake-out deployment target
    app_config.configure_targets(app_config.DEPLOYMENT_TARGET)

def tests():
    """
    Run Python unit tests.
    """
    local('nosetests')

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
    if env.get('deploy_web_services', False):
        deploy_confs()

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
    require('branch', provided_by=[stable, master, branch])

    env.remote = remote

    run('cd %(repo_path)s; git fetch %(remote)s' % env)
    run('cd %(repo_path)s; git checkout %(branch)s; git pull %(remote)s %(branch)s' % env)

def install_requirements():
    """
    Install the latest requirements.
    """
    require('settings', provided_by=[production, staging])

    run('%(virtualenv_path)s/bin/pip install -U -r %(repo_path)s/requirements.txt' % env)

def install_crontab():
    """
    Install cron jobs script into cron.d.
    """
    require('settings', provided_by=[production, staging])

    sudo('cp %(repo_path)s/crontab /etc/cron.d/%(deployed_name)s' % env)

def uninstall_crontab():
    """
    Remove a previously install cron jobs script from cron.d
    """
    require('settings', provided_by=[production, staging])

    sudo('rm /etc/cron.d/%(deployed_name)s' % env)

def bootstrap_issues():
    """
    Bootstraps Github issues with default configuration.
    """
    auth = github.get_auth()
    github.delete_existing_labels(auth)
    github.create_default_labels(auth)
    github.create_default_tickets(auth)

"""
Deployment
"""
def _deploy_to_s3():
    """
    Deploy the gzipped stuff to S3.
    """
    s3cmd = 's3cmd -P --add-header=Cache-Control:max-age=5 --guess-mime-type --recursive --exclude-from gzip_types.txt sync gzip/ %s'
    s3cmd_gzip = 's3cmd -P --add-header=Cache-Control:max-age=5 --add-header=Content-encoding:gzip --guess-mime-type --recursive --exclude "*" --include-from gzip_types.txt sync gzip/ %s'

    for bucket in env.s3_buckets:
        env.s3_bucket = bucket
        local(s3cmd % ('s3://%(s3_bucket)s/%(deployed_name)s/' % env))
        local(s3cmd_gzip % ('s3://%(s3_bucket)s/%(deployed_name)s/' % env))

def _gzip_www():
    """
    Gzips everything in www and puts it all in gzip
    """
    local('python gzip_www.py')
    local('rm -rf gzip/live-data')


def render_confs():
    """
    Renders server configurations.
    """
    require('settings', provided_by=[production, staging])

    with settings(warn_only=True):
        local('mkdir confs/rendered')

    context = app_config.get_secrets()
    context['PROJECT_SLUG'] = app_config.PROJECT_SLUG
    context['PROJECT_NAME'] = app_config.PROJECT_NAME
    context['DEPLOYMENT_TARGET'] = env.settings

    for service, remote_path in SERVICES:
        file_path = 'confs/rendered/%s.%s.conf' % (app_config.PROJECT_SLUG, service)

        with open('confs/%s.conf' % service, 'r') as read_template:

            with open(file_path, 'wb') as write_template:
                payload = Template(read_template.read())
                write_template.write(payload.render(**context))


def deploy_confs():
    """
    Deploys rendered server configurations to the specified server.
    This will reload nginx and the appropriate uwsgi config.
    """
    require('settings', provided_by=[production, staging])

    render_confs()

    with settings(warn_only=True):
        run('touch /tmp/%s.sock' % app_config.PROJECT_SLUG)

        for service, remote_path in SERVICES:
            service_name = '%s.%s' % (app_config.PROJECT_SLUG, service)
            file_name = '%s.conf' % service_name
            local_path = 'confs/rendered/%s' % file_name
            put(local_path, remote_path, use_sudo=True)

            if service == 'nginx':
                sudo('ln -s %s%s /etc/nginx/sites-enabled/%s' % (remote_path, file_name, file_name))
                sudo('service nginx reload')

            else:
                sudo('initctl reload-configuration')
                sudo('service %s restart' % service_name)


def deploy(remote='origin'):
    """
    Deploy the latest app to S3 and, if configured, to our servers.
    """
    require('settings', provided_by=[production, staging])

    if env.get('deploy_to_servers', False):
        require('branch', provided_by=[stable, master, branch])

    if (env.settings == 'production' and env.branch != 'stable'):
        _confirm("You are trying to deploy the '%(branch)s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env)

    render()
    _gzip_www()
    _deploy_to_s3()

    if env.get('deploy_to_servers', False):
        checkout_latest(remote)

        if env.get('install_crontab', False):
            install_crontab()

"""
Cron jobs
"""
def cron_test():
    """
    Example cron task. Note we use "local" instead of "run"
    because this will run on the server.
    """
    require('settings', provided_by=[production, staging])

    local('echo $DEPLOYMENT_TARGET > /tmp/cron_test.txt')

"""
Destruction
"""
def _confirm(message):
    answer = prompt(message, default="Not at all")

    if answer.lower() not in ('y', 'yes', 'buzz off', 'screw you'):
        exit()


def nuke_confs():
    """
    DESTROYS rendered server configurations from the specified server.
    This will reload nginx and stop the uwsgi config.
    """
    require('settings', provided_by=[production, staging])

    for service, remote_path in SERVICES:
        with settings(warn_only=True):
            service_name = '%s.%s' % (app_config.PROJECT_SLUG, service)
            file_name = '%s.conf' % service_name

            if service == 'nginx':
                sudo('rm -f %s%s' % (remote_path, file_name))
                sudo('service nginx reload')

            else:
                sudo('service %s stop' % service_name)
                sudo('rm -f %s%s' % (remote_path, file_name))
                sudo('initctl reload-configuration')


def shiva_the_destroyer():
    """
    Deletes the app from s3
    """
    require('settings', provided_by=[production, staging])

    _confirm("You are about to destroy everything deployed to %(settings)s for this project.\nDo you know what you're doing?" % env)

    with settings(warn_only=True):
        s3cmd = 's3cmd del --recursive %s'

        for bucket in env.s3_buckets:
            env.s3_bucket = bucket
            local(s3cmd % ('s3://%(s3_bucket)s/%(deployed_name)s' % env))

        if env.get('deploy_to_servers', False):
            run('rm -rf %(path)s' % env)

            if env.get('deploy_web_services', False):
                nuke_confs()

            if env.get('install_crontab', False):
                uninstall_crontab()

"""
App-template meta-commands
"""

def super_merge():
    """
    Merge master branch into all init- branches.
    """
    _confirm("You are about to merge 'master' into all 'init-' branches.\nDo you know what you're doing?")

    local('git fetch')
    local('git checkout master')

    for branch in ['table', 'map', 'chat']:
        local('git checkout init-%s' % branch)
        local('git merge origin/init-%s --no-edit' % branch)
        local('git merge master --no-edit')

    local('git checkout master')

    local('git push --all')

