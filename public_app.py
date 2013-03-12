#!/usr/bin/env python

from flask import Flask, render_template

import app_config

app = Flask(app_config.PROJECT_NAME)


# Example application views
@app.route('/dynamic/view/')
def index():
    """
    Example dynamic view demonstrating rendering a simple HTML page.
    """
    context = {'app_config': app_config}
    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=app_config.DEBUG)
