#!/usr/bin/env python

"""
A very thin client wrapper for Google Analytics.
"""

import argparse
from collections import OrderedDict
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client.clientsecrets import InvalidClientSecretsError
from oauth2client.file import Storage
from oauth2client import tools

CLIENT_SECRETS = os.path.expanduser('~/.google_analytics_secrets.json')
DAT = os.path.expanduser('~/.google_analytics_auth.dat')

SERVICE_NAME = 'analytics'
SERVICE_VERSION = 'v3'
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
NPR_ORG_LIVE_ID = '53470309'

TOTAL_METRICS = [
    'ga:pageviews',
    'ga:uniquePageviews',
    'ga:users',
    'ga:sessions'
]

class GoogleAnalytics(object):
    def __init__(self, property_id=NPR_ORG_LIVE_ID, domain=None, slug=None):
        self.property_id = property_id
        self.domain = domain
        self.slug = slug

        self.storage = Storage(DAT)
        self.credentials = self.storage.get()
        
        if not self.credentials or self.credentials.invalid:
            self.credentials = self._authorize()
            
        http = self.credentials.authorize(http=httplib2.Http())

        self.service = discovery.build(SERVICE_NAME, SERVICE_VERSION, http=http)

    def _authorize(self):
        """
        Authorize with OAuth2.
        """
        parent_parsers = [tools.argparser]
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=parent_parsers)

        flags = parser.parse_args(sys.argv[1:])

        try:
            flow = client.flow_from_clientsecrets(
                CLIENT_SECRETS,
                scope=SCOPE
            )
        except InvalidClientSecretsError:
            print 'Client secrets not found at %s' % CLIENT_SECRETS
        
        return tools.run_flow(flow, self.storage, flags)

    def query(self, start_date=None, end_date=None, metrics=[], dimensions=[], filters=None, sort=[], start_index=1, max_results=10):
        """
        Execute a query
        """
        if start_date:
            start_date = start_date.strftime('%Y-%m-%d')
        else:
            start_date = '2005-01-01'

        if end_date:
            end_date = end_date.strftime('%Y-%m-%d')
        else:
            end_date = 'today' 

        if self.domain:
            domain_filter = 'ga:hostname=%s' % self.domain

            if filters:
                filters = '%s;%s' % (domain_filter, filters)
            else:
                filters = domain_filter

        if self.slug:
            slug_filter = 'ga:pagePath=~^/%s/' % self.slug
                
            if filters:
                filters = '%s;%s' % (slug_filter, filters)
            else:
                filters = slug_filter

        return self.service.data().ga().get(
            ids='ga:' + self.property_id,
            start_date=start_date,
            end_date=end_date,
            metrics=','.join(metrics) or None,
            dimensions=','.join(dimensions) or None,
            filters=filters,
            sort=','.join(sort) or None,
            start_index=str(start_index),
            max_results=str(max_results)
        ).execute()

    def totals(self):
        results = self.query(
            metrics=TOTAL_METRICS
        )

        d = OrderedDict()

        for i, k in enumerate(TOTAL_METRICS):
            d[k] = int(results['rows'][0][i])

        return d

    def totals_by_device_category(self, totals):
        results = self.query(
            metrics=TOTAL_METRICS,
            dimensions=['ga:deviceCategory'],
            sort=['-ga:pageviews']
        )
        
        d = OrderedDict()

        for i, column in enumerate(TOTAL_METRICS):
            d[column] = OrderedDict()

            for row in results['rows']:
                d[column][row[0]] = float(row[1 + i]) / totals[column]

        return d

    def totals_by_browser(self, totals):
        results = self.query(
            metrics=TOTAL_METRICS,
            dimensions=['ga:browser'],
            sort=['-ga:pageviews']
        )
        
        d = OrderedDict()

        for i, column in enumerate(TOTAL_METRICS):
            d[column] = OrderedDict()

            for row in results['rows']:
                d[column][row[0]] = float(row[1 + i]) / totals[column]

        return d

    def totals_by_source(self, totals):
        results = self.query(
            metrics=TOTAL_METRICS,
            dimensions=['ga:source'],
            sort=['-ga:pageviews']
        )
        
        d = OrderedDict()

        for i, column in enumerate(TOTAL_METRICS):
            d[column] = OrderedDict()

            for row in results['rows']:
                d[column][row[0]] = float(row[1 + i]) / totals[column]

        return d

    def top_pageviews(self):
        results = self.query(
            metrics=['ga:pageviews'],
            dimensions=['ga:pagePath'],
            sort=['-ga:pageviews']
        )

        return OrderedDict([(r[0], int(r[1])) for r in results['rows']])

    def performance(self):
        metrics = ['ga:avgPageLoadTime', 'ga:avgPageDownloadTime', 'ga:avgDomInteractiveTime', 'ga:avgDomContentLoadedTime']

        results = self.query(
            metrics=metrics
        )

        d = OrderedDict()

        for i, k in enumerate(metrics):
            d[k] = float(results['rows'][0][i])

        return d

    def time_on_site(self):
        results = self.query(
            metrics=['ga:avgSessionDuration']
        )

        return float(results['rows'][0][0])

        
    def time_on_site_by_device_category(self):
        results = self.query(
            metrics=['ga:avgSessionDuration'],
            dimensions=['ga:deviceCategory'],
            sort=['-ga:avgSessionDuration']
        )
        
        d = OrderedDict()

        for row in results['rows']:
            d[row[0]] = float(row[1])

        return d

