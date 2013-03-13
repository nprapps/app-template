#!/usr/bin/env python

from flask import Flask, render_template

import app_config

app = Flask(app_config.PROJECT_NAME)


# Example application views
@app.route('/%s/' % app_config.PROJECT_SLUG)
def _dynamic_page():
    """
    Example dynamic view demonstrating rendering a simple HTML page.
    """
    return "SAMPLE DYNAMIC PAGE."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=app_config.DEBUG)
