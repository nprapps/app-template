#!/usr/bin/env python

import csv
from mimetypes import guess_type

from flask import Flask, render_template

import app_config
from render_utils import JavascriptIncluder

app = Flask(app_config.PROJECT_NAME)

# Utils
def make_context():
    context = app_config.__dict__
    context['JS'] = JavascriptIncluder(debug=app.debug)

    return context

# App-specific views 
@app.route('/')
@app.route('/simple')
def simple():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    return render_template('simple.html', **make_context())

@app.route('/table')
def table():
    """
    Example view demonstrating rendering a table page.
    """
    context = make_context() 

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
    return render_template('map.html', **make_context())

foo="""# Generic routing for static files
@app.route('/js/<path:path>')
def _js(path):
    with open('www/%s' % path) as f:
        return f.read(), 200, { 'Content-Type': guess_type(path)[0] }"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
