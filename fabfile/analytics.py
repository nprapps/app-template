#!/usr/bin/env python

"""
Analytics reporting tasks
"""

from collections import OrderedDict
from datetime import timedelta
import json
import os

from fabric.api import task

import app_config
from etc.ga import GoogleAnalytics

@task
def machine(path, ndays=None):
    """
    Write current analytics to a JSON file.
    """
    start_date = None
    end_date = None

    if ndays and not app_config.LAUNCH_DATE:
        print 'You must specify a LAUNCH_DATE in app_config.py before you can report a number of days.'

        return

    if app_config.LAUNCH_DATE:
        start_date = app_config.LAUNCH_DATE

        if ndays:
            end_date = start_date + timedelta(days=int(ndays))

    slug = app_config.PROJECT_SLUG

    ga = GoogleAnalytics(slug=slug, start_date=start_date, end_date=end_date)

    output = {}
    output['slug'] = slug
    output['start_date'] = start_date.strftime('%Y-%m-%d') if start_date else None
    output['ndays'] = int(ndays) if ndays else None

    print 'Getting totals'
    output['totals'] = ga.totals()
    print 'Getting top devices'
    output['top_devices'] = ga.totals_by_device_category(output['totals'])
    print 'Getting top sources'
    output['top_sources'] = ga.totals_by_source(output['totals'])
    print 'Getting top browsers'
    output['top_browsers'] = ga.totals_by_browser(output['totals'])
    print 'Getting top pages'
    output['top_pageviews'] = ga.top_pageviews()
    print 'Getting performance data'
    output['performance'] = ga.performance()
    print 'Getting time on site'
    output['time_on_site'] = ga.time_on_site()
    print 'Getting time on site by devices'
    output['time_on_site_devices'] = ga.time_on_site_by_device_category()

    with open(path, 'w') as f:
        json.dump(output, f)

def _format_duration(secs):
    """
    Format a duration in seconds as minutes and seconds.
    """
    secs = int(secs)

    if secs > 60:
        mins = secs / 60
        secs = secs - (mins * 60)

        return '%im %02is' % (mins, secs)

    return '%02is' % secs  

@task
def human(path):
    """
    Print analytics from a saved file.
    """
    with open(path) as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    print 'Report for "%(slug)s" beginning %(start_date)s and running for %(ndays)i days' % (data)

    print ''
    print 'Totals:'

    totals = data['totals'] 

    for k, v in totals.items():
        print '{:>15,d}    {:s}'.format(v, k)

    print ''
    print '{:>15s}    {:s}'.format(_format_duration(data['time_on_site']), 'ga:avgSessionDuration')
    
    print ''
    print 'Top devices:'

    for column, devices in data['top_devices'].items():
        print '    %s' % column

        for d, v in devices.items():
            print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print '    ga:avgSessionDuration'
    
    for d, v in data['time_on_site_devices'].items(): 
        print '{:>15s}    {:s}'.format(_format_duration(v), d)

    print ''
    print 'Top sources (pageviews):'

    sources = data['top_sources']['ga:pageviews']

    for d, v in sources.items():
        print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print 'Top browsers (pageviews):'

    browsers = data['top_browsers']['ga:pageviews']

    for d, v in browsers.items():
        print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print 'Top pageviews:'

    for page, pageviews in data['top_pageviews'].items():
        print '{:>15,d}    {:s}'.format(pageviews, page)

    print ''
    print 'Performance (seconds):'

    metrics = data['performance'] 

    for k, v in metrics.items():
        print '{:>15.1f}    {:s}'.format(v, k)


@task(default=True)
def report(ndays=None):
    """
    Print current analytics to the console.
    """
    machine('.temp_report.json', ndays)
    human('.temp_report.json')
    os.remove('.temp_report.json')


