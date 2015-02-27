import app_config
import os

from functools import wraps
from flask import request, redirect, url_for
from app_config import authomatic

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

def oauth_required(f):
    """
    Decorator to ensure oauth workflow has happened.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        credentials = get_credentials()
        if app_config.COPY_GOOGLE_DOC_KEY and (not credentials or not credentials.valid):
            return redirect('/oauth')
        else:
            return f(*args, **kwargs)
    return decorated_function

