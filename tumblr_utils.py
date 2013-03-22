#!/usr/bin/env python

import datetime
import json
import os
from sets import *
import time as pytime
import urlparse

import oauth2 as oauth
from tumblpy import Tumblpy

import app_config


def _parse_log():
    with open(app_config.LOG_PATH, 'rb') as f:
        output_dict = {}
        for line in f:
            entry_dict = {}
            l = line.split(' ')
            date = l[0]
            time = l[1]
            timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%Y-%m-%d %H:%M:%S,%f")
            entry_dict['timestamp'] = pytime.mktime(timestamp.timetuple())
            entry_dict['msg_type'] = l[2]
            entry_dict['msg_code'] = l[3]
            info = l[4:]
            output_dict.setdefault(date, {})
            output_dict[date].setdefault(str(timestamp.hour), {})
            output_dict[date][str(timestamp.hour)].setdefault('items', [])
            output_dict[date][str(timestamp.hour)]['items'].append(entry_dict)

        return output_dict

def parse_log_last_24():
    data = _parse_log()

    today = datetime.date.today()
    todaytetime = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)

    daily_errors = 0
    daily_success = 0

    today_logs = data.get('%s-%s-%s' % (today.year, today.month, today.day), None)

    if not today_logs:
        print 'No logs today. Sorry!'

    if today_logs:
        for hour in today_logs:
            errors = []
            success = []
            for item in today_logs[hour]['items']:
                if item['msg_type'] == 'INFO':
                    success.append(item)
                else:
                    errors.append(item)

            print hour + ":00"
            print '  %s errors.' % len(errors)
            daily_errors += len(errors)
            print '  %s successes.' % len(success)
            daily_success += len(success)


        total = daily_errors + daily_success
        print '\n-----------------\n%s total errors.' % daily_errors
        print '%s total success.' % daily_success
        print '%s total posts.' % total


def parse_log_to_json():
    data = _parse_log()
    with open('data/%s-log.json' % app_config.PROJECT_SLUG, 'wb') as f:
        f.write(json.dumps(data))

def generate_new_oauth_tokens():
    """
    Script to generate new OAuth tokens.
    Code from this gist: https://gist.github.com/4219558
    """
    consumer_key = os.environ['TUMBLR_CONSUMER_KEY']
    consumer_secret = os.environ['TUMBLR_APP_SECRET']

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "POST")
    if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    print

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    accepted = 'n'
    while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
            oauth_verifier = raw_input('What is the OAuth Verifier? ')

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above."
    print


def dump_tumblr_json():
    t = Tumblpy(
            app_key=app_config.TUMBLR_KEY,
            app_secret=os.environ['TUMBLR_APP_SECRET'],
            oauth_token=os.environ['TUMBLR_OAUTH_TOKEN'],
            oauth_token_secret=os.environ['TUMBLR_OAUTH_TOKEN_SECRET'])

    limit = 10
    pages = range(0, 20)

    for page in pages:
        offset = page * limit
        posts = t.get('posts', blog_url=app_config.TUMBLR_URL, params={'limit': limit, 'offset': offset})

        with open('data/backups/tumblr_prod_%s.json' % page, 'w') as f:
            f.write(json.dumps(posts))
