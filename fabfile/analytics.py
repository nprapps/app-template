#!/usr/bin/env python

"""
Analytics reporting tasks
"""

from collections import OrderedDict
from datetime import date, timedelta
import json

from fabric.api import task

import app_config
from etc.ga import GoogleAnalytics

@task(name='json')
def machine(start_date=None, ndays=None, slug=None):
    """
    Write analytics to a JSON file.
    """
    end_date = None

    if start_date:
        start_date = date(*map(int, start_date.split('-')))

    if ndays:
        end_date = start_date + timedelta(days=int(ndays))

    if not slug:
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

    with open('analytics.json', 'w') as f:
        json.dump(output, f, indent=4)

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

@task(name='txt')
def human(path='analytics.json'):
    """
    Write analytics from a JSON file to a human-readable text file.
    """
    with open(path) as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    with open('analytics.txt', 'w') as f:
        f.write('Report for "%s"\n' % data['slug'])
        
        if data['start_date']:
            f.write('Beginning %s\n' % data['start_date'])

        if data['ndays']:
            f.write('Running for %i days\n' % data['ndays'])

        f.write('\nTotals:\n')

        totals = data['totals'] 

        for k, v in totals.items():
            f.write('{:>15,d}    {:s}\n'.format(v, k))

        f.write('\n{:>15s}    {:s}\n'.format(_format_duration(data['time_on_site']), 'ga:avgSessionDuration'))
        
        f.write('\nTop devices:\n')

        for column, devices in data['top_devices'].items():
            f.write('    %s\n' % column)

            for d, v in devices.items():
                f.write('{:>15.1%}    {:s}\n'.format(v, d))

        f.write('\n    ga:avgSessionDuration\n')
        
        for d, v in data['time_on_site_devices'].items(): 
            f.write('{:>15s}    {:s}\n'.format(_format_duration(v), d))

        f.write('\nTop sources (pageviews):\n')

        sources = data['top_sources']['ga:pageviews']

        for d, v in sources.items():
            f.write('{:>15.1%}    {:s}\n'.format(v, d))

        f.write('\nTop browsers (pageviews):\n')

        browsers = data['top_browsers']['ga:pageviews']

        for d, v in browsers.items():
            f.write('{:>15.1%}    {:s}\n'.format(v, d))

        f.write('\nTop pageviews:\n')

        for page, pageviews in data['top_pageviews'].items():
            f.write('{:>15,d}    {:s}\n'.format(pageviews, page))

        f.write('\nPerformance (seconds):\n')

        metrics = data['performance'] 

        for k, v in metrics.items():
            f.write('{:>15.1f}    {:s}\n'.format(v, k))

@task(default=True)
def report(start_date=None, ndays=None, slug=None):
    """
    Write both JSON and human-readable analytics.
    """
    machine(start_date, ndays, slug)
    human()


