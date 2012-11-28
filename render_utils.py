#!/usr/bin/env python

from cssmin import cssmin
from flask import Markup
from slimit import minify

import app_config

class Includer():
    def __init__(self, debug):
        self.debug = debug
        self.includes = []

    def push(self, path):
            self.includes.append(path)

            return ""

    def render():
        raise NotImplementedError()

class JavascriptIncluder(Includer):
    """
    Psuedo-template tag that handles collecting Javascript and serving appropriate clean or compressed versions.
    """
    def _compress(self):
        output = []

        for src in self.includes:
            with open('www/%s' % src) as f:
                output.append(minify(f.read()))

        return '\n'.join(output)

    def render(self, path):
        if self.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<script type="text/javascript" src="%s"></script>' % src for src in self.includes
                ])
            del self.includes[:]

            return Markup(response)

        with open('www/%s' % path, 'w') as f:
            f.write(self._compress())
        
        del self.includes[:]

        return Markup('<script type="text/javascript" src="%s"></script>' % path)

class CSSIncluder(Includer):
    """
    Psuedo-template tag that handles collecting CSS and serving appropriate clean or compressed versions.
    """
    def _compress(self):
        output = []

        for src in self.includes:
            if src.endswith('less'):
                src = src.replace('less', 'css')

            with open('www/%s' % src) as f:
                output.append(cssmin(f.read()))

        return '\n'.join(output)

    def render(self, path):
        if self.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<link rel="stylesheet" type="text/css" href="%s" />' % src for src in self.includes
                ])
            del self.includes[:]

            return Markup(response)
 
        with open('www/%s' % path, 'w') as f:
            f.write(self._compress())
       
        del self.includes[:]

        return Markup('<link rel="stylesheet" type="text/css" href="%s" />' % path)

def make_context(app):
    context = app_config.__dict__
    context['JS'] = JavascriptIncluder(debug=app.debug)
    context['CSS'] = CSSIncluder(debug=app.debug)

    return context

