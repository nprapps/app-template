#!/usr/bin/env python

import datetime
import gzip
import json
import os
from sets import *
import time as pytime
import urlparse

import boto
import oauth2 as oauth
import requests
from tumblpy import Tumblpy

import app_config

secrets = app_config.get_secrets()


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


def parse_log_to_json():
    data = _parse_log()
    with open('data/%s-log.json' % app_config.PROJECT_SLUG, 'wb') as f:
        f.write(json.dumps(data))


def generate_new_oauth_tokens():
    """
    Script to generate new OAuth tokens.
    Code from this gist: https://gist.github.com/4219558
    """
    consumer_key = os.environ['%s_TUMBLR_APP_KEY' % app_config.CONFIG_NAME]
    consumer_secret = os.environ['%s_TUMBLR_APP_SECRET' % app_config.CONFIG_NAME]

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
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
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
        app_key=secrets['TUMBLR_APP_KEY'],
        app_secret=secrets['TUMBLR_APP_SECRET'],
        oauth_token=secrets['TUMBLR_OAUTH_TOKEN'],
        oauth_token_secret=secrets['TUMBLR_OAUTH_TOKEN_SECRET'])

    limit = 10
    pages = range(0, 20)

    for page in pages:
        offset = page * limit
        posts = t.get('posts', blog_url=app_config.TUMBLR_URL, params={'limit': limit, 'offset': offset})

        with open('data/backups/tumblr_prod_%s.json' % page, 'w') as f:
            f.write(json.dumps(posts))


def write_json_data():

    output = {
        'meta': {
            'total_posts': 0,
        },
        'mostpopular': []
    }

    """
    Top posts.
    """

    TUMBLR_FILENAME = app_config.TUMBLR_FILENAME

    print "Starting."
    # Set constants
    base_url = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/posts/photo' % app_config.TUMBLR_BLOG_ID
    key_param = '?api_key=%s' % secrets['TUMBLR_APP_KEY']
    limit_param = '&limit=20'
    limit = 20
    new_limit = limit
    post_list = []

    # Figure out the total number of posts.
    r = requests.get(base_url + key_param)
    total_count = int(json.loads(r.content)['response']['total_posts'])
    print "%s total posts available." % total_count
    output['meta']['total_posts'] = total_count

    # Do the pagination math.
    pages_count = (total_count / limit)
    pages_remainder = (total_count % limit)
    if pages_remainder > 0:
        pages_count += 1
    pages = range(0, pages_count)
    print "%s pages required." % len(pages)

    # Start requesting pages.
    # Note: Maximum of 20 posts per page.
    print "Requesting pages."
    for page in pages:

        # Update all of the pagination shenanigans.
        start_number = new_limit - limit
        end_number = new_limit
        if end_number > total_count:
            end_number = total_count
        new_limit = new_limit + limit
        page_param = '&offset=%s' % start_number
        page_url = base_url + key_param + limit_param + page_param

        # Actually fetch the page URL.
        r = requests.get(page_url)
        posts = json.loads(r.content)

        for post in posts['response']['posts']:
            try:
                post_list.append(post)
            except KeyError:
                pass

    # Sort the results first.
    print "Finished requesting pages."
    print "Sorting list."
    post_list = sorted(post_list, key=lambda post: post['note_count'], reverse=True)

    # Render the sorted list, but slice to just 24 objects per bb.
    print "Rendering posts from sorted list."
    for post in post_list[0:24]:
        default_photo_url = post['photos'][0]['original_size']['url']
        simple_post = {
            'id': post['id'],
            'url': post['post_url'],
            'text': post['caption'],
            'timestamp': post['timestamp'],
            'note_count': post['note_count'],
            'photo_url': default_photo_url,
            'photo_url_250': default_photo_url,
            'photo_url_500': default_photo_url,
            'photo_url_1280': default_photo_url
        }

        # Handle the new photo assignment.
        for photo in post['photos'][0]['alt_sizes']:
            if int(photo['width']) == 100:
                simple_post['photo-url-100'] = photo['url']
            if int(photo['width']) == 250:
                simple_post['photo_url_250'] = photo['url']
            if int(photo['width']) == 500:
                simple_post['photo_url_500'] = photo['url']
            if int(photo['width']) == 1280:
                simple_post['photo_url_1280'] = photo['url']
        output['mostpopular'].append(simple_post)

    # Ensure the proper sort on our output list.
    print "Ordering output."
    output['mostpopular'] = sorted(output['mostpopular'], key=lambda post: post['note_count'], reverse=True)

    # Write the JSON file.
    print "Producing JSON file at %s" % TUMBLR_FILENAME
    json_output = json.dumps(output)
    with open(TUMBLR_FILENAME, 'w') as f:
        f.write(json_output)
    print "JSON file written."


def deploy_json_data(s3_buckets):

    TUMBLR_FILENAME = app_config.TUMBLR_FILENAME

    with open(TUMBLR_FILENAME, 'r') as json_output:
        with gzip.open(TUMBLR_FILENAME + '.gz', 'wb') as f:
            f.write(json_output.read())

    for bucket in s3_buckets:
        conn = boto.connect_s3()
        bucket = conn.get_bucket(bucket)
        key = boto.s3.key.Key(bucket)
        key.key = '%s/live-data/%s-data.json' % (app_config.PROJECT_SLUG, app_config.PROJECT_SLUG)
        key.set_contents_from_filename(
            TUMBLR_FILENAME + '.gz',
            policy='public-read',
            headers={
                'Cache-Control': 'max-age=5 no-cache no-store must-revalidate',
                'Content-Encoding': 'gzip'
            }
        )

    os.remove(TUMBLR_FILENAME + '.gz')
