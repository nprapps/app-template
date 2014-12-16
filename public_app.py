#!/usr/bin/env python

import datetime
import logging
import json

from flask import Flask, make_response, render_template
from werkzeug.debug import DebuggedApplication

import app_config
from render_utils import make_context, smarty_filter, urlencode_filter
import static

app = Flask(__name__)
app.debug = app_config.DEBUG

file_handler = logging.FileHandler('%s/public_app.log' % app_config.SERVER_LOG_PATH)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.register_blueprint(static.static, url_prefix='/%s' % app_config.PROJECT_SLUG)

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')

# Example application views
@app.route('/%s/test/' % app_config.PROJECT_SLUG, methods=['GET'])
def _test_app():
    """
    Test route for verifying the application is running.
    """
    app.logger.info('Test URL requested.')

    return make_response(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Example of rendering index.html with public_app 
@app.route ('/%s/' % app_config.PROJECT_SLUG, methods=['GET'])
def index():
    """
    Example view rendering a simple page.
    """
    context = make_context(asset_depth=1)

    with open('data/featured.json') as f:
        context['featured'] = json.load(f)

    return make_response(render_template('index.html', **context))

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab public_app" instead!'
