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
        print '{:>15,d}    {:s}'.format(v, k)
    
    print ''
    print 'Top devices:'

    for column, devices in ga.totals_by_device_category(totals).items():
        print '    %s' % column

        for d, v in devices.items():
            print '{:>15.1f}    {:s}'.format(v, d)

    print ''
    print 'Top browsers (pageviews):'

    browsers = ga.totals_by_browser(totals)['ga:pageviews']

    for d, v in browsers.items():
        print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print 'Top pageviews:'

    for page, pageviews in ga.top_pageviews().items():
        print '{:>15,d}    {:s}'.format(pageviews, page)

    print ''
    print 'Performance (seconds):'

    metrics = ga.performance()

    for k, v in metrics.items():
        print '{:>15.1f}    {:s}'.format(v, k)

