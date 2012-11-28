#!/usr/bin/env python

from flask import Markup

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

