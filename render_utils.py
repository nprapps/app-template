#!/usr/bin/env python

import json

from cssmin import cssmin
from flask import Markup, g
from slimit import minify

import app_config

class Includer(object):
    """
    Base class for Javascript and CSS psuedo-template-tags.
    """
    def __init__(self):
        self.includes = []
        self.tag_string = None

    def push(self, path):
            self.includes.append(path)

            return ""

    def _compress(self):
        raise NotImplementedError()

    def render(self, path):
        if getattr(g, 'compile_includes', False):
            out_filename = 'www/%s' % path

            if out_filename not in g.compiled_includes:
                print 'Rendering %s' % out_filename

                with open(out_filename, 'w') as f:
                    f.write(self._compress())

            # See "fab render"
            g.compiled_includes.append(out_filename)

            markup = Markup(self.tag_string % path)
        else:
            response = ','.join(self.includes)

            response = '\n'.join([
                self.tag_string % src for src in self.includes
                ])

            markup = Markup(response)

        del self.includes[:]

        return markup

class JavascriptIncluder(Includer):
    """
    Psuedo-template tag that handles collecting Javascript and serving appropriate clean or compressed versions.
    """
    def __init__(self):
        Includer.__init__(self)

        self.tag_string = '<script type="text/javascript" src="%s"></script>'

    def _compress(self):
        output = []

        for src in self.includes:
            with open('www/%s' % src) as f:
                print '- compressing %s' % src
                output.append(minify(f.read()))

        return '\n'.join(output)

class CSSIncluder(Includer):
    """
    Psuedo-template tag that handles collecting CSS and serving appropriate clean or compressed versions.
    """
    def __init__(self):
        Includer.__init__(self)

        self.tag_string = '<link rel="stylesheet" type="text/css" href="%s" />'

    def _compress(self):
        output = []

        for src in self.includes:
            if src.endswith('less'):
                src = src.replace('less', 'css') # less/example.less -> css/example.css
                src = '%s.less.css' % src[:-4]   # css/example.css -> css/example.less.css

            with open('www/%s' % src) as f:
                print '- compressing %s' % src
                output.append(cssmin(f.read()))

        return '\n'.join(output)

class Sheet(object):
    """
    Wrap copy text, for a single worksheet, for error handling.
    """
    _sheet = {}
    _name = None

    def __init__(self, data, name=None):
        self._sheet = data
        self._name = name

    def __getattr__(self, name):
        if not self._sheet:
            return 'COPY ERROR: sheet `%s`' % self._name
        try:
            return Markup(self._sheet[name])
        except KeyError:
            return 'COPY ERROR: `%s`' % name

class Copy(object):
    """
    Wraps copy text, for multiple worksheets, for error handling.
    """
    _copy = {}

    def __init__(self):
        with open('data/copy.json', 'r') as f:
            data = json.load(f)

        for sheet, data in data.items():
            self._copy[sheet] = Sheet(data, name=sheet)

    def __getattr__(self, name):
        try:
            return self._copy[name]
        except KeyError:
            return Sheet({}, name=name)

def flatten_app_config():
    """
    Returns a copy of app_config containing only
    configuration variables.
    """
    config = {}

    # Only all-caps [constant] vars get included
    for k, v in app_config.__dict__.items():
        if k.upper() == k:
            config[k] = v

    return config

def make_context():
    """
    Create a base-context for rendering views.
    Includes app_config and JS/CSS includers.
    """
    context = flatten_app_config()

    context['COPY'] = Copy()
    context['JS'] = JavascriptIncluder()
    context['CSS'] = CSSIncluder()

    return context

