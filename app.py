#!/usr/bin/env python

import csv
from mimetypes import guess_type

from flask import Flask, render_template

import app_config

app = Flask(app_config.PROJECT_NAME)

# App-specific views 
@app.route('/')
@app.route('/simple')
def simple():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    context = app_config.__dict__

    return render_template('simple.html', **context)

@app.route('/table')
def table():
    """
    Example view demonstrating rendering a table page.
    """
    context = app_config.__dict__ 

    with open('data/example.csv') as f:
        reader = csv.reader(f)
        context['columns'] = reader.next()
        context['rows'] = list(reader)

    return render_template('table.html', **context)

@app.route('/map')
def map():
    """
    TODO: Example view demonstrating rendering a map page.
    """
    context = app_config.__dict__

    return render_template('map.html', **context)

# Generic routing mechanism for static files
@app.route('/<path:path>')
def _www(path):
    with open('www/%s' % path) as f:
        return f.read(), 200, { 'Content-Type': guess_type(path)[0] }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
