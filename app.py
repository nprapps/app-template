#!/usr/bin/env python

import csv
from mimetypes import guess_type

from flask import Flask, render_template

import app_config

app = Flask(app_config.PROJECT_NAME)

# App-specific routes
@app.route('/')
def index():
    data = app_config.__dict__ 

    with open('data/example.csv') as f:
        reader = csv.reader(f)
        data['columns'] = reader.next()
        data['rows'] = list(reader)

    return render_template('index.html', **data)

# Generic routing mechanism for static files
@app.route('/<path:path>')
def _www(path):
    with open('www/%s' % path) as f:
        return f.read(), 200, { 'Content-Type': guess_type(path)[0] }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
