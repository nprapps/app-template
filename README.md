nprapps' Project Template
=========================

* [About this template](#about-this-template)
* [Assumptions](#assumptions)
* [What's in here?](#whats-in-here)
* [Copy the template](#copy-the-template)
* [Configure the project](#configure-the-project)
* [Install requirements](#install-requirements)
* [Project secrets](#project-secrets)
* [Bootstrap issues](#bootstrap-issues)
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

About this template
-------------------

This template provides a a project skeleton suitable for any project that is to be served entirely as flat files. Facilities are provided for rendering html from data, compiling LESS into CSS, deploying to S3, etc. (It actually supports deploying to servers too, but that's less well-tested.)

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.

What's in here?
---------------

The project contains the following folders and important files:

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
* ``crontab`` -- Cron jobs to be installed as part of the project.
* ``fabfile.py`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands automating setup and deployment.

Copy the template
-----------------

Create a new repository on Github. Everywhere you see ``$NEW_PROJECT_NAME`` in the following script, replace it with the name of the repository you just created.

```
git clone git@github.com:nprapps/app-template.git $NEW_PROJECT_NAME
cd $NEW_PROJECT_NAME

# Optional: checkout an initial project branch
# git checkout [init-map|init-table|init-chat]

rm -rf .git
git init
git add * .gitignore
git commit -am "Initial import from app-template."
git remote add origin git@github.com:nprapps/$NEW_PROJECT_NAME.git
git push -u origin master
```

Configure the project
---------------------

Edit ``app_config.py`` and update ``PROJECT_NAME``, ``DEPLOYED_NAME``, ``REPOSITORY_NAME`` any other relevant configuration details.

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
npm install less universal-jst
mkvirtualenv $NEW_PROJECT_NAME
pip install -r requirements.txt
```

Project secrets
---------------

Project secrets should **never** be stored in ``app_config.py`` or anywhere else in the repository. They will be leaked to the client if you do. Instead, always store passwords, keys, etc. in environment variables and document that they are needed here in the README.

Bootstrap issues
----------------

The app-template can automatically setup your Github repo with our default labels and tickets by running ``fab bootstrap_issues``. You will be prompted for your Github username and password.

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

* The first column is the "key"
* The second column is the "value"
* We have two sheets – attribution and content
* This sheet is "published to the web" using Google Docs' interface

This document is specified in ``app_config`` with the variable ``COPY_GOOGLE_DOC_KEY``. To use your own spreadsheet, change this value to reflect your document's key (found in the Google Docs URL after ``&key=``).

The app template is outfitted with a few ``fab`` utility functions that make pulling changes and updating your local data easy.

To update the latest document, simply run:

```
fab update_copy
```

Note: this ``update_copy`` runs automatically whenever ``fab render`` is called.

At the template level, Jinja maintains a ``COPY`` object that you can use to access your values in the templates.

Using our example sheet, to use the ``byline`` key in ``templates/index.html``:

```
{{ COPY.attribution.byline }}
```

More generally, you can access anything defined in your Google Doc like so:

```
{{ COPY.sheet_name.key_name }}
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
You can deploy to EC2 for a variety of reasons. We cover two cases: Running a dynamic Web application and executing cron jobs.

For running a Web application:
* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Also in ``fabfile.py`` set ``env.deploy_web_services`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

For running cron jobs:
* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Also in ``fabfile.py``, set ``env.install_crontab`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

You can configure your EC2 instance to both run Web services and execute cron jobs; just set both environment variables in the fabfile.

Install cron jobs
-----------------

Cron jobs are defined in the file `crontab`. Each task should use the `cron.sh` shim to ensure the project's virtualenv is properly activated prior to execution. For example:

```
* * * * * ubuntu bash /home/ubuntu/apps/$PROJECT_NAME/repository/cron.sh fab $DEPLOYMENT_TARGET cron_test
```

**Note:** In this example you will need to replace `$PROJECT_NAME` with your actual deployed project name.

To install your crontab set `env.install_crontab` to `True` at the top of `fabfile.py`. Cron jobs will be automatically installed each time you deploy to EC2.

Install web services
---------------------

Web services are configured in the `confs/` folder. Currently, there are two: `nginx.conf` and `uwsgi.conf`.

Running ``fab setup`` will deploy your confs if you have set ``env.deploy_to_servers`` and ``env.deploy_web_services`` both to ``True`` at the top of ``fabfile.py``.

To check that these files are being properly rendered, you can render them locally and see the results in the `confs/rendered/` directory.

```
fab render_confs
```

You can also deploy the configuration files independently of the setup command by running:

```
fab deploy_confs
```
