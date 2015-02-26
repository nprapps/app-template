import app_config
import os

from functools import wraps
from flask import g, request, redirect, url_for
from app_config import authomatic

def get_credentials():
    file_path = os.path.expanduser(app_config.GOOGLE_OAUTH_CREDENTIALS_PATH)

    with open(file_path) as f:
        serialized_credentials = f.read()

    credentials = authomatic.credentials(serialized_credentials)

    if not credentials.valid:
        credentials.refresh()
        save_credentials(credentials)

    return credentials

def save_credentials(credentials):
    file_path = os.path.expanduser(app_config.GOOGLE_OAUTH_CREDENTIALS_PATH)
    with open(file_path, 'w') as f:
        f.write(credentials.serialize())

def oauth_required(f):
    """
    Decorator to ensure oauth workflow has happened.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        credentials = get_credentials()
        if app_config.COPY_GOOGLE_DOC_KEY and not credentials.valid:
            return redirect('/oauth-alert')
        else:
            return f(*args, **kwargs)
    return decorated_function

