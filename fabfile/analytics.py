#!/usr/bin/env python

"""
Analytics reporting tasks
"""

from fabric.api import task

from etc.ga import GoogleAnalytics

@task
def report():
    """
    Query some things.
    """
    ga = GoogleAnalytics(slug='commencement')

    print 'Totals:'

    totals = ga.totals()

    for k, v in totals.items():
        print '\t%i\t\t %s' % (v, k)
    
    print ''
    print 'Top pageviews:'

    for page, pageviews in ga.top_pageviews().items():
        print '\t%i\t\t%s' % (pageviews, page)

    print ''
    print 'Top devices:'

    for column, devices in ga.totals_by_device_category(totals).items():
        print '\t%s' % column

        for d, v in devices.items():
            print '\t\t%.1f%%\t\t%s' % (v, d)
