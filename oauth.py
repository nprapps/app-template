import app_config
import os

from app_config import authomatic
from authomatic.adapters import WerkzeugAdapter
from etc.gdocs import GoogleDoc
from flask import Blueprint, make_response, redirect, render_template, url_for
from functools import wraps
from render_utils import make_context

oauth = Blueprint('oauth', __name__)

@oauth.route('/oauth/')
def oauth_alert():
    """
    Show an OAuth alert to start authentication process.
    """
    context = make_context()
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

    result = authomatic.login(WerkzeugAdapter(request, response), 'google')

    if result:
        context['result'] = result

        if not result.error:
            save_credentials(result.user.credentials)
            doc = {
                'key': app_config.COPY_GOOGLE_DOC_KEY,
                'file_path': app_config.COPY_PATH,
                'credentials': result.user.credentials,
                'authomatic': app_config.authomatic,
            }
            g = GoogleDoc(**doc)
            g.get_document()

        return render_template('oauth/authenticate.html', **context)

    return response

def oauth_required(f):
    """
    Decorator to ensure oauth workflow has happened.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        credentials = get_credentials()
        if app_config.COPY_GOOGLE_DOC_KEY and (not credentials or not credentials.valid):
            return redirect(url_for('/oauth/'))
        else:
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

