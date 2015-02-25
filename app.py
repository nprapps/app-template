#!/usr/bin/env python

import json
import os

from app_config import authomatic
from authomatic.adapters import WerkzeugAdapter
from etc.decorators import oauth_required
from flask import Flask, make_response, render_template
from werkzeug.debug import DebuggedApplication

import app_config
from render_utils import make_context, smarty_filter, urlencode_filter
import static

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')

# Example application views
@app.route('/')
@oauth_required
def index():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    context = make_context()

    with open('data/featured.json') as f:
        context['featured'] = json.load(f)

    return render_template('index.html', **context)

@app.route('/oauth-alert/')
def oauth_alert():
    context = make_context()

    serialized_credentials = os.environ.get('APPS_GOOGLE_OAUTH', None)
    if serialized_credentials:
        credentials = authomatic.credentials(serialized_credentials)

        if credentials.valid:
            resp = authomatic.access(credentials, 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json')
            if resp.status == 200:
                context['email'] = resp.data['email']
                context['credentials'] = credentials

    return render_template('oauth_alert.html', **context)

@app.route('/authenticate/', methods=['GET', 'POST'])
def authenticate():
    from flask import request
    response = make_response()
    context = make_context()
    result = authomatic.login(WerkzeugAdapter(request, response), 'google')

    if result:
        context['result'] = result

        if not result.error:
            os.environ['APPS_GOOGLE_OAUTH'] = result.user.credentials.serialize()

        return render_template('authenticate.html', **context)
    return response

@app.route('/comments/')
def comments():
    """
    Full-page comments view.
    """
    return render_template('comments.html', **make_context())

@app.route('/widget.html')
def widget():
    """
    Embeddable widget example page.
    """
    return render_template('widget.html', **make_context())

@app.route('/test_widget.html')
def test_widget():
    """
    Example page displaying widget at different embed sizes.
    """
    return render_template('test_widget.html', **make_context())

app.register_blueprint(static.static)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab app" instead!'
