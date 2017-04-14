#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import app_config
import os

from app_config import authomatic
from authomatic.adapters import WerkzeugAdapter
from exceptions import KeyError
from flask import Blueprint, make_response, redirect, render_template, url_for
from functools import wraps
from render_utils import make_context

# Via: https://developers.google.com/drive/v3/reference/files/export
# and: https://developers.google.com/drive/v3/web/manage-downloads
DRIVE_API_EXPORT_TEMPLATE = 'https://www.googleapis.com/drive/v3/files/%s/export?mimeType=%s'

oauth = Blueprint('_oauth', __name__)

@oauth.route('/oauth/')
def oauth_alert():
    """
    Show an OAuth alert to start authentication process.
    """
    context = make_context()

    if not _has_api_credentials():
        return render_template('oauth/warning.html', **context)

    credentials = get_credentials()
    if credentials:
        resp = authomatic.access(credentials, 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json')
        if resp.status == 200:
            context['email'] = resp.data['email']

    return render_template('oauth/oauth.html', **context)

@oauth.route('/authenticate/', methods=['GET', 'POST'])
def authenticate():
    """
    Run OAuth workflow.
    """
    from flask import request
    response = make_response()
    context = make_context()

    if not _has_api_credentials():
        return render_template('oauth/warning.html', **context)

    result = authomatic.login(WerkzeugAdapter(request, response), 'google')

    if result:
        context['result'] = result

        if not result.error:
            save_credentials(result.user.credentials)
            get_document(app_config.COPY_GOOGLE_DOC_KEY, app_config.COPY_PATH)

        return render_template('oauth/authenticate.html', **context)

    return response

def oauth_required(f):
    """
    Decorator to ensure oauth workflow has happened.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        credentials = get_credentials()
        if app_config.COPY_GOOGLE_DOC_KEY and (not credentials or not credentials.valid):
            return redirect(url_for('_oauth.oauth_alert'))
        else:
            if request.args.get('refresh'):
                get_document(app_config.COPY_GOOGLE_DOC_KEY, app_config.COPY_PATH)
            return f(*args, **kwargs)
    return decorated_function

def get_credentials():
    """
    Read Authomatic credentials object from disk and refresh if necessary.
    """
    file_path = os.path.expanduser(app_config.GOOGLE_OAUTH_CREDENTIALS_PATH)

    try:
        with open(file_path) as f:
            serialized_credentials = f.read()
    except IOError:
        return None

    credentials = authomatic.credentials(serialized_credentials)

    if not credentials.valid:
        credentials.refresh()
        save_credentials(credentials)

    return credentials

def save_credentials(credentials):
    """
    Take Authomatic credentials object and save to disk.
    """
    file_path = os.path.expanduser(app_config.GOOGLE_OAUTH_CREDENTIALS_PATH)
    with open(file_path, 'w') as f:
        f.write(credentials.serialize())

def get_document(key, file_path, mimeType=None):
    """
    Uses Authomatic to get the google doc
    """
    # Default to spreadsheet if no mimeType is passed
    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    if not mimeType:
        mimeType = mime
    credentials = get_credentials()
    url = DRIVE_API_EXPORT_TEMPLATE % (
        key,
        mimeType)
    response = app_config.authomatic.access(credentials, url)

    if response.status != 200:
        if response.status == 404:
            raise KeyError("Error! Your Google Doc does not exist or you do not have permission to access it.")
        else:
            raise KeyError("Error! Google returned a %s error" % response.status)

    with open(file_path, 'wb') as writefile:
        writefile.write(response.content)

def _has_api_credentials():
    """
    Test for API credentials
    """
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_OAUTH_CONSUMER_SECRET')
    salt = os.environ.get('AUTHOMATIC_SALT')
    return bool(client_id and client_secret and salt)
