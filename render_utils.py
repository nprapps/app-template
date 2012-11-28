#!/usr/bin/env python

from flask import Markup

import app_config

class JavascriptIncluder():
    """
    Psuedo-template tag that handles collecting Javascript and serving appropriate clean or compressed versions.
    """
    def __init__(self, debug):
        self.debug = debug
        self.includes = []

    def push(self, path):
        self.includes.append(path)

        return ""

    def render(self, path):
        if self.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<script type="text/javascript" src="%s"></script>' % js for js in self.includes
                ])
            del self.includes[:]

            return Markup(response)
        
        del self.includes[:]

        return Markup('<script type="text/javascript" src="%s"></script>' % path)

class CSSIncluder():
    """
    Psuedo-template tag that handles collecting CSS and serving appropriate clean or compressed versions.
    """
    def __init__(self, debug):
        self.debug = debug
        self.includes = []

    def push(self, path):
        self.includes.append(path)

        return ""

    def render(self, path):
        if self.debug:
            response = ','.join(self.includes)
            
            response = '\n'.join([
                '<link rel="stylesheet" type="text/css" href="%s" />' % css for css in self.includes
                ])
            del self.includes[:]

            return Markup(response)
        
        del self.includes[:]

        return Markup('<link rel="stylesheet" type="text/css" href="%s" />' % path)

def make_context(app):
    context = app_config.__dict__
    context['JS'] = JavascriptIncluder(debug=app.debug)
    context['CSS'] = CSSIncluder(debug=app.debug)

    return context

