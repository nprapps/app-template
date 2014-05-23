#!/usr/bin/env python

"""
Analytics reporting tasks
"""

from fabric.api import task

import app_config
from etc.ga import GoogleAnalytics

@task
def report():
    """
    Query some things.
    """
    ga = GoogleAnalytics(slug=app_config.PROJECT_SLUG)

    print 'Totals:'

    totals = ga.totals()

    for k, v in totals.items():
        print '\t%i\t\t %s' % (v, k)
    
    print ''
    print 'Top devices:'

    for column, devices in ga.totals_by_device_category(totals).items():
        print '\t%s' % column

        for d, v in devices.items():
            print '\t\t%.1f%%\t\t%s' % (v, d)

    print ''
    print 'Top browsers (pageviews):'

    browsers = ga.totals_by_browser(totals)['ga:pageviews']

    for d, v in browsers.items():
        print '\t%.1f%%\t\t%s' % (v, d)

    print ''
    print 'Top pageviews:'

    for page, pageviews in ga.top_pageviews().items():
        print '\t%i\t\t%s' % (pageviews, page)


