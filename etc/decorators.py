import os

from functools import wraps
from flask import g, request, redirect, url_for
from app_config import authomatic

def oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        serialized_credentials = os.environ.get('APPS_GOOGLE_OAUTH', None)
        if serialized_credentials:
            credentials = authomatic.credentials(serialized_credentials)
        if not serialized_credentials or not credentials.valid:
            return redirect('/oauth-alert')
        else:
            return f(*args, **kwargs)
    return decorated_function
