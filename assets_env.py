#!/usr/bin/env python

from webassets import Environment
from webassets import Bundle

environment = Environment('./www', '/')

header_js = Bundle(
    'js/lib/jquery-1.8.2.min.js',
    'js/lib/modernizr.js',
    'js/responsive-ad.js',
    output='js/app-header.min.js')

footer_js = Bundle(
    'js/lib/underscore-min.js',
    'js/lib/moment.min.js',
    'bootstrap/js/bootstrap.min.js',
    'js/templates.js',
    'js/app.js',
    output='js/app-footer.min.js')

css = Bundle(
    'bootstrap/css/bootstrap.min.css',
    'bootstrap/css/bootstrap-responsive.min.css',
    'css/app.css',
    output='css/app.min.css')

environment.register('js_header', header_js)
environment.register('js_footer', footer_js)
environment.register('css', css)
