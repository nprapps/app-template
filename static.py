#!/usr/bin/env python

import json
from mimetypes import guess_type
import os
import subprocess

from flask import abort, make_response

import app_config
import copytext
from flask import Blueprint
from render_utils import BetterJSONEncoder, flatten_app_config

static = Blueprint('static', __name__)

# Render JST templates on-demand
@static.route('/js/templates.js')
def _templates_js():
    r = subprocess.check_output(["node_modules/universal-jst/bin/jst.js", "--template", "underscore", "jst"])

    return make_response(r, 200, { 'Content-Type': 'application/javascript' })

# Render LESS files on-demand
@static.route('/less/<string:filename>')
def _less(filename):
    if not os.path.exists('less/%s' % filename):
        abort(404)

    r = subprocess.check_output(["node_modules/less/bin/lessc", "less/%s" % filename])

    return make_response(r, 200, { 'Content-Type': 'text/css' })

# Render application configuration
@static.route('/js/app_config.js')
def _app_config_js():
    config = flatten_app_config()
    js = 'window.APP_CONFIG = ' + json.dumps(config, cls=BetterJSONEncoder)

    return make_response(js, 200, { 'Content-Type': 'application/javascript' })

# Render copytext
@static.route('/js/copy.js')
def _copy_js():
    copy = 'window.COPY = ' + copytext.Copy(app_config.COPY_PATH).json()

    return make_response(copy, 200, { 'Content-Type': 'application/javascript' })

# Server arbitrary static files on-demand
@static.route('/<path:path>')
def _static(path):
    try:
        with open('www/%s' % path) as f:
            return make_response(f.read(), 200, { 'Content-Type': guess_type(path)[0] })
    except IOError:
        abort(404)
