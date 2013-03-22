#!/usr/bin/env python

import datetime
import logging
import os
import re
import time

from flask import Flask, redirect, render_template
from tumblpy import Tumblpy
from tumblpy import TumblpyError
from werkzeug import secure_filename

import app_config

app = Flask(app_config.PROJECT_NAME)
app.config['PROPAGATE_EXCEPTIONS'] = True

logger = logging.getLogger('tumblr')
file_handler = logging.FileHandler('/var/log/familymeal.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


@app.route('/family-meal/', methods=['POST'])
def _post_to_tumblr():
    """
    Handles the POST to Tumblr.
    """
    def clean(string):
        """
        Formats a string all pretty.
        """
        return string.replace('-', ' ').replace("id ", "I'd ").replace("didnt", "didn't").replace('i ', 'I ')

    def strip_html(value):
        """
        Strips HTML from a string.
        """
        return re.compile(r'</?\S([^=]*=(\s*"[^"]*"|\s*\'[^\']*\'|\S*)|[^>])*?>', re.IGNORECASE).sub('', value)

    def strip_breaks(value):
        """
        Converts newlines, returns and other breaks to <br/>.
        """
        value = re.sub(r'\r\n|\r|\n', '\n', value)
        return value.replace('\n', '<br />')

    try:
        # Request is a global. Import it down here where we need it.
        from flask import request

        context = {
            'message': strip_breaks(strip_html(request.form['message'])),
            'name': strip_html(request.form['signed_name']),
            'location': strip_html(request.form['location']),
            'app_config': app_config
        }

        caption = render_template('caption.html', **context)
        t = Tumblpy(
            app_key=app_config.TUMBLR_KEY,
            app_secret=os.environ['TUMBLR_APP_SECRET'],
            oauth_token=os.environ['TUMBLR_OAUTH_TOKEN'],
            oauth_token_secret=os.environ['TUMBLR_OAUTH_TOKEN_SECRET'])

        file_path = '/upload/%s/%s_%s' % (
            app_config.PROJECT_SLUG,
            str(time.mktime(datetime.datetime.now().timetuple())).replace('.', ''),
            secure_filename(request.files['image'].filename.replace(' ', '-'))
        )

        with open('/tmp%s' % file_path, 'w') as f:
            f.write(request.files['image'].read())

        params = {
            "type": "photo",
            "caption": caption,
            "tags": app_config.TUMBLR_TAGS,
            "source": "http://%s%s" % (app_config.SERVERS[0], file_path)
        }

        try:
            tumblr_post = t.post('post', blog_url=app_config.TUMBLR_URL, params=params)
            tumblr_url = u"http://%s/%s" % (app_config.TUMBLR_URL, tumblr_post['id'])
            logger.info('200 %s' % tumblr_url)

            return redirect('%s#posts' % tumblr_url, code=301)

        except TumblpyError, e:
            logger.error('%s %s' % (e.error_code, e.msg))
            return 'TUMBLR ERROR'

        return redirect('%s#posts' % tumblr_url, code=301)

    except Exception, e:
        logger.error('%s' % e)
        return 'ERROR'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=app_config.DEBUG)
