#!/usr/bin/env python

"""
Project-wide application configuration.

DO NOT STORE SECRETS, PASSWORDS, ETC. IN THIS FILE.
They will be exposed to users. Use environment variables instead.
See get_secrets() below for a fast way to access them.
"""

import os

"""
NAMES
"""
# Project name used for display
PROJECT_NAME = '$NEW_PROJECT_NAME'

# Project name used for paths on the filesystem and in urls
# Use dashes, not underscores
PROJECT_SLUG = '$NEW_PROJECT_SLUG'

# The name of the repository containing the source
REPOSITORY_NAME = '$NEW_REPOSITORY_NAME'

PROJECT_CREDITS = 'Jeremy Bowers, Brian Boyer, Alyson Hurt and Matt Stiles / NPR'
PROJECT_SHORTLINK = 'npr.org/foo'

"""
DEPLOYMENT
"""
PRODUCTION_S3_BUCKETS = ['apps.npr.org', 'apps2.npr.org']
PRODUCTION_SERVERS = ['54.214.20.225']

STAGING_S3_BUCKETS = ['stage-apps.npr.org']
STAGING_SERVERS = ['54.214.20.232']

# Should code be deployed to the web/cron servers?
DEPLOY_TO_SERVERS = 'True'

# Should the crontab file be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_CRONTAB = False

# Should the service configurations be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_SERVICES = True

# These variables will be set at runtime. See configure_targets() below
S3_BUCKETS = []
SERVERS = []
DEBUG = True

LOG_PATH = '/var/log/%s.log' % PROJECT_SLUG

"""
COPY EDITING
"""
COPY_GOOGLE_DOC_KEY = '0AlXMOHKxzQVRdHZuX1UycXplRlBfLVB0UVNldHJYZmc'

"""
SHARING
"""
PROJECT_DESCRIPTION = 'An opinionated project template for (mostly) server-less apps.'
SHARE_URL = 'http://%s/%s/' % (PRODUCTION_S3_BUCKETS[0], PROJECT_SLUG)


TWITTER = {
    'TEXT': PROJECT_NAME,
    'URL': SHARE_URL
}

FACEBOOK = {
    'TITLE': PROJECT_NAME,
    'URL': SHARE_URL,
    'DESCRIPTION': PROJECT_DESCRIPTION,
    'IMAGE_URL': '',
    'APP_ID': '138837436154588'
}

NPR_DFP = {
    'STORY_ID': '203618536',
    'TARGET': 'News_NPR_News_Investigations',
    'ENVIRONMENT': 'NPRTEST',
    'TESTSERVER': 'true'
}

"""
SERVICES
"""
GOOGLE_ANALYTICS_ID = 'UA-5828686-4'

TUMBLR_TAGS = 'TODO,TKTK,CHANGEME'
TUMBLR_FILENAME = 'www/live-data/%s-data.json' % PROJECT_SLUG


"""
Utilities
"""
def get_secrets():
    """
    A method for accessing our secrets.
    """
    env_var_prefix = PROJECT_SLUG.replace('-', '').upper()

    secrets = [
        '%s_TUMBLR_APP_KEY' % env_var_prefix,
        '%s_TUMBLR_OAUTH_TOKEN' % env_var_prefix,
        '%s_TUMBLR_OAUTH_TOKEN_SECRET' % env_var_prefix,
        '%s_TUMBLR_APP_SECRET' % env_var_prefix
    ]

    secrets_dict = {}

    for secret in secrets:
        # Saves the secret with the old name.
        secrets_dict[secret.replace('%s_' % env_var_prefix, '')] = os.environ.get(secret, None)

    return secrets_dict

def configure_targets(deployment_target):
    """
    Configure deployment targets. Abstracted so this can be
    overriden for rendering before deployment.
    """
    global S3_BUCKETS
    global SERVERS
    global DEBUG
    global TUMBLR_URL
    global TUMBLR_BLOG_ID
    global STATIC_URL
    global STATIC_CSS

    if deployment_target == 'production':
        S3_BUCKETS = PRODUCTION_S3_BUCKETS
        SERVERS = PRODUCTION_SERVERS
        DEBUG = False
        TUMBLR_URL = '%s.tumblr.com' % PROJECT_SLUG
        TUMBLR_BLOG_ID = PROJECT_SLUG
        STATIC_URL = 'http://%s/%s/' % (S3_BUCKETS[0], PROJECT_SLUG)
        STATIC_CSS = '%scss/tumblr.less.css' % STATIC_URL

    elif deployment_target == 'staging':
        S3_BUCKETS = STAGING_S3_BUCKETS
        SERVERS = STAGING_SERVERS
        DEBUG = True
        TUMBLR_URL = 'staging-%s.tumblr.com' % PROJECT_SLUG
        TUMBLR_BLOG_ID = 'staging-%s' % PROJECT_SLUG
        STATIC_URL = 'http://%s/%s/' % (S3_BUCKETS[0], PROJECT_SLUG)
        STATIC_CSS = '%scss/tumblr.less.css' % STATIC_URL

    else:
        S3_BUCKETS = None
        SERVERS = ['127.0.0.1:8000']
        DEBUG = True
        TUMBLR_URL = None
        TUMBLR_BLOG_ID = None
        STATIC_URL = 'http://127.0.0.1:8000/'
        STATIC_CSS = '%sless/tumblr.less' % STATIC_URL

"""
Run automated configuration
"""
DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

configure_targets(DEPLOYMENT_TARGET)
