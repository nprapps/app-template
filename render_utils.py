#!/usr/bin/env python

from cssmin import cssmin
from flask import Markup, g
from slimit import minify

import app_config

class Includer():
    def __init__(self, app):
        self.app = app
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
        if self.app.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<script type="text/javascript" src="%s"></script>' % src for src in self.includes
                ])
            del self.includes[:]

            return Markup(response)

        out_filename = 'www/%s' % path

        if out_filename not in g.rendered_includes:
            print 'Rendering %s' % out_filename

            with open(out_filename, 'w') as f:
                f.write(self._compress())

            # See "fab render"
            g.rendered_includes.append(out_filename)

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
        if self.app.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<link rel="stylesheet" type="text/css" href="%s" />' % src for src in self.includes
                ])
            del self.includes[:]

            return Markup(response)

        out_filename = 'www/%s' % path
 
        if out_filename not in g.rendered_includes:
            print 'Rendering %s' % out_filename

            with open(out_filename, 'w') as f:
                f.write(self._compress())

            # See "fab render"
            g.rendered_includes.append(out_filename)
     
        del self.includes[:]

        return Markup('<link rel="stylesheet" type="text/css" href="%s" />' % path)

def make_context(app):
    context = app_config.__dict__
    context['JS'] = JavascriptIncluder(app=app)
    context['CSS'] = CSSIncluder(app=app)

    return context

