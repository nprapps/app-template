#!/usr/bin/env python

"""
Commands for rendering various parts of the app stack.
"""

from glob import glob
import os

from fabric.api import local, task

import app

def _fake_context(path):
    return app.app.test_request_context(path=path)

@task
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('less/*.less'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = 'www/css/%s.less.css' % name

        try:
            local('node_modules/less/bin/lessc %s %s' % (path, out_path))
        except:
            print 'It looks like "lessc" isn\'t installed. Try running: "npm install"'
            raise

@task
def jst():
    """
    Render Underscore templates to a JST package.
    """
    try:
        local('node_modules/universal-jst/bin/jst.js --template underscore jst www/js/templates.js')
    except:
        print 'It looks like "jst" isn\'t installed. Try running: "npm install"'

@task
def app_config_js():
    """
    Render app_config.js to file.
    """
    from static import _app_config_js

    with _fake_context('/js/app_config.js'):
        response = _app_config_js()

    with open('www/js/app_config.js', 'w') as f:
        f.write(response.data)

@task
def copytext_js():
    """
    Render COPY to copy.js.
    """
    from static import _copy_js

    with _fake_context('/js/copytext.js'):
        response = _copy_js()

    with open('www/js/copy.js', 'w') as f:
        f.write(response.data)

@task(default=True)
def render_all():
    """
    Render HTML templates and compile assets.
    """
    from flask import g

    less()
    jst()
    app_config_js()
    copytext_js()

    compiled_includes = {} 

    for rule in app.app.url_map.iter_rules():
        rule_string = rule.rule
        name = rule.endpoint

        if name == 'static' or name.startswith('_'):
            print 'Skipping %s' % name
            continue

        if rule_string.endswith('/'):
            filename = 'www' + rule_string + 'index.html'
        elif rule_string.endswith('.html'):
            filename = 'www' + rule_string
        else:
            print 'Skipping %s' % name
            continue

        dirname = os.path.dirname(filename)

        if not (os.path.exists(dirname)):
            os.makedirs(dirname)

        print 'Rendering %s' % (filename)

        with _fake_context(rule_string):
            g.compile_includes = True
            g.compiled_includes = compiled_includes

            bits = name.split('.')

            # Determine which module the view resides in
            if len(bits) > 1:
                module, name = bits
            else:
                module = 'app'

            view = globals()[module].__dict__[name]
            # NB: Flask response object utf-8 encodes the data
            content = view().data

            compiled_includes = g.compiled_includes

        with open(filename, 'w') as f:
            f.write(content)

