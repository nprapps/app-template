Copyright 2013 NPR.  All rights reserved.  No part of these materials may be reproduced, modified, stored in a retrieval system, or retransmitted, in any form or by any means, electronic, mechanical or otherwise, without prior written permission from NPR.

(Want to use this code? Send an email to nprapps@npr.org!)

$NEW_PROJECT_NAME
========================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [What's in here?](#whats-in-here)
* [Install requirements](#install-requirements)
* [Project secrets](#project-secrets)
* [Adding a template/view](#adding-a-templateview)
* [Run the project locally](#run-the-project-locally)
* [Editing workflow](#editing-workflow)
* [Run Javascript tests](#run-javascript-tests)
* [Run Python tests](#run-python-tests)
* [Compile static assets](#compile-static-assets)
* [Test the rendered app](#test-the-rendered-app)
* [Deploy to S3](#deploy-to-s3)
* [Deploy to EC2](#deploy-to-ec2)
* [Install cron jobs](#install-cron-jobs)
* [Install web services](#install-web-services)
* [Run a remote fab command](#run-a-remote-fab-command)

What is this?
-------------

**Describe $NEW_PROJECT_NAME here.**

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

What's in here?
---------------

The project contains the following folders and important files:

* ``confs`` -- Server configuration files for nginx and uwsgi. Edit the templates then ``fab <ENV> render_confs``, don't edit anything in ``confs/rendered`` directly.
* ``data`` -- Data files, such as those used to generate HTML.
* ``etc`` -- Miscellaneous scripts and metadata for project bootstrapping.
* ``jst`` -- Javascript ([Underscore.js](http://documentcloud.github.com/underscore/#template)) templates.
* ``less`` -- [LESS](http://lesscss.org/) files, will be compiled to CSS and concatenated for deployment.
* ``templates`` -- HTML ([Jinja2](http://jinja.pocoo.org/docs/)) templates, to be compiled locally.
* ``tests`` -- Python unit tests.
* ``www`` -- Static and compiled assets to be deployed. (a.k.a. "the output")
* ``www/live-data`` -- "Live" data deployed to S3 via cron jobs or other mechanisms. (Not deployed with the rest of the project.)
* ``www/test`` -- Javascript tests and supporting files.
* ``app.py`` -- A [Flask](http://flask.pocoo.org/) app for rendering the project locally.
* ``app_config.py`` -- Global project configuration for scripts, deployment, etc.
* ``copytext.py`` -- Code supporting the [Editing workflow](#editing-workflow)
* ``crontab`` -- Cron jobs to be installed as part of the project.
* ``fabfile.py`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands automating setup and deployment.
* ``public_app.py`` -- A [Flask](http://flask.pocoo.org/) app for running server-side code.
* ``render_utils.py`` -- Code supporting template rendering.
* ``requirements.txt`` -- Python requirements.

Install requirements
--------------------

Node.js is required for the static asset pipeline. If you don't already have it, get it like this:

```
brew install node
curl https://npmjs.org/install.sh | sh
```

Then install the project requirements:

```
cd $NEW_PROJECT_NAME
npm install less universal-jst -g --prefix node_modules
mkvirtualenv --no-site-packages $NEW_PROJECT_NAME
pip install -r requirements.txt
```

Project secrets
---------------

Project secrets should **never** be stored in ``app_config.py`` or anywhere else in the repository. They will be leaked to the client if you do. Instead, always store passwords, keys, etc. in environment variables and document that they are needed here in the README.

Adding a template/view
----------------------

A site can have any number of rendered templates (i.e. pages). Each will need a corresponding view. To create a new one:

* Add a template to the ``templates`` directory. Ensure it extends ``_base.html``.
* Add a corresponding view function to ``app.py``. Decorate it with a route to the page name, i.e. ``@app.route('/filename.html')``
* By convention only views that end with ``.html`` and do not start with ``_``  will automatically be rendered when you call ``fab render``.

Run the project locally
-----------------------

A flask app is used to run the project locally. It will automatically recompile templates and assets on demand.

```
workon $NEW_PROJECT_NAME
python app.py
```

Visit [localhost:8000](http://localhost:8000) in your browser.

Editing workflow
-------------------

The app is rigged up to Google Docs for a simple key/value store that provides an editing workflow.

View the sample copy spreadsheet [here](https://docs.google.com/spreadsheet/pub?key=0AlXMOHKxzQVRdHZuX1UycXplRlBfLVB0UVNldHJYZmc#gid=0). A few things to note:

* If there is a column called ``key``, there is expected to be a column called ``value`` and rows will be accessed in templates as key/value pairs
* Rows may also be accessed in templates by row index using iterators (see below)
* You may have any number of worksheets
* This document must be "published to the web" using Google Docs' interface

This document is specified in ``app_config`` with the variable ``COPY_GOOGLE_DOC_KEY``. To use your own spreadsheet, change this value to reflect your document's key (found in the Google Docs URL after ``&key=``).

The app template is outfitted with a few ``fab`` utility functions that make pulling changes and updating your local data easy.

To update the latest document, simply run:

```
fab update_copy
```

Note: ``update_copy`` runs automatically whenever ``fab render`` is called.

At the template level, Jinja maintains a ``COPY`` object that you can use to access your values in the templates. Using our example sheet, to use the ``byline`` key in ``templates/index.html``:

```
{{ COPY.attribution.byline }}
```

More generally, you can access anything defined in your Google Doc like so:

```
{{ COPY.sheet_name.key_name }}
```

You may also access rows using iterators. In this case, the column headers of the spreadsheet become keys and the row cells values. For example:

```
{% for row in COPY.sheet_name %}
{{ row.column_one_header }}
{{ row.column_two_header }}
{% endfor %}
```

Run Javascript tests
--------------------

With the project running, visit [localhost:8000/test/SpecRunner.html](http://localhost:8000/test/SpecRunner.html).

Run Python tests
----------------

Python unit tests are stored in the ``tests`` directory. Run them with ``fab tests``.

Compile static assets
---------------------

Compile LESS to CSS, compile javascript templates to Javascript and minify all assets:

```
workon $NEW_PROJECT_NAME
fab render
```

(This is done automatically whenever you deploy to S3.)

Test the rendered app
---------------------

If you want to test the app once you've rendered it out, just use the Python webserver:

```
cd www
python -m SimpleHTTPServer
```

Deploy to S3
------------

```
fab staging master deploy
```

Deploy to EC2
-------------

You can deploy to EC2 for a variety of reasons. We cover two cases: Running a dynamic web application (`public_app.py`) and executing cron jobs (`crontab`).

Servers capable of running the app can be setup using our [servers](https://github.com/nprapps/servers) project.

For running a Web application:

* In ``app_config.py`` set ``DEPLOY_TO_SERVERS`` to ``True``.
* Also in ``app_config.py`` set ``DEPLOY_WEB_SERVICES`` to ``True``.
* Run ``fab staging master setup_server`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

For running cron jobs:

* In ``app_config.py`` set ``DEPLOY_TO_SERVERS`` to ``True``.
* Also in ``app_config.py``, set ``INSTALL_CRONTAB`` to ``True``
* Run ``fab staging master setup_server`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

You can configure your EC2 instance to both run Web services and execute cron jobs; just set both environment variables in the fabfile.

Install cron jobs
-----------------

Cron jobs are defined in the file `crontab`. Each task should use the `cron.sh` shim to ensure the project's virtualenv is properly activated prior to execution. For example:

```
* * * * * ubuntu bash /home/ubuntu/apps/$PROJECT_NAME/repository/cron.sh fab $DEPLOYMENT_TARGET cron_test
```

**Note:** In this example you will need to replace `$PROJECT_NAME` with your actual deployed project name.

To install your crontab set `INSTALL_CRONTAB` to `True` in `app_config.py`. Cron jobs will be automatically installed each time you deploy to EC2.

Install web services
---------------------

Web services are configured in the `confs/` folder. 

Running ``fab setup_server`` will deploy your confs if you have set ``DEPLOY_TO_SERVERS`` and ``DEPLOY_WEB_SERVICES`` both to ``True`` at the top of ``app_config.py``.

To check that these files are being properly rendered, you can render them locally and see the results in the `confs/rendered/` directory.

```
fab render_confs
```

You can also deploy the configuration files independently of the setup command by running:

```
fab deploy_confs
```

Run a  remote fab command
-------------------------

Sometimes it makes sense to run a fabric command on the server, for instance, when you need to render using a production database. You can do this with the `fabcast` fabric command. For example:

```
fab staging master fabcast:deploy
```

If any of the commands you run themselves require executing on the server, the server will SSH into itself to run them.
