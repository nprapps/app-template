nprapps' Project Template
=========================

* [About this template](#about-this-template)
* [Copy the template](#copy-the-template)
* [Configure the project](#configure-the-project)
* [Tumblog setup](#tumblog-setup)
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
* [Deploy the app](#deploy-the-app)
* [Deploy to S3](#deploy-to-s3)
* [Deploy to EC2](#deploy-to-ec2)
* [Install cron jobs](#install-cron-jobs)
* [Install web services](#install-web-services)
* [Deploy Tumblr themes](#deploy-tumblr-themes)
* [Bootstrap issues](#bootstrap-issues)
* [Develop with the template](#develop-with-the-template)
* [Merging init branches](#merging-init-branches)

About this template
-------------------

This template provides a a project skeleton suitable for NPR projects that are designed to be served as flat files. Facilities are provided for rendering html from data, compiling LESS into CSS, deploying to S3, installing cron jobs on servers, copy-editing via Google Spreadsheets and a whole bunch of other stuff.

**Please note:** This project is not intended to be a generic solution. We strongly encourage those who love the app-template to use it as a basis for their own project template. We have no plans to remove NPR-specific code from this project.

Copy the template
-----------------

Create a new repository on Github. Everywhere you see ``$NEW_PROJECT_NAME`` in the following script, replace it with the name of the repository you just created.

```
git clone git@github.com:nprapps/app-template.git $NEW_PROJECT_NAME
cd $NEW_PROJECT_NAME

# Optional: checkout an initial project branch
# git checkout [init-map|init-table|init-chat|init-tumblr]

rm -rf .git
git init
mv PROJECT_README.md README.md
git add * .gitignore
git commit -am "Initial import from app-template."
git remote add origin git@github.com:nprapps/$NEW_PROJECT_NAME.git
git push -u origin master
```

Configure the project
---------------------

Edit ``app_config.py`` and update ``PROJECT_NAME``, ``DEPLOYED_NAME``, ``REPOSITORY_NAME`` any other relevant configuration details.

<<<<<<< HEAD
NPR apps-specific: Update relevant environment variables with API keys, etc., from Dropbox:
tumblog-setup
You can either source ``~/Dropbox/nprapps/tumblr_oauth_keys.txt`` (variables will only be set for the life of your current shell):

```
. ~/Dropbox/nprapps/tumblr_oauth_keys.txt
```

Or you can append its contents to your bash_profile|bashrc|zshrc:

```
cat ~/Dropbox/nprapps/tumblr_oauth_keys.txt >> ~/.zshrc
```

Tumblog setup
-------------------

Log into our NPR apps tumblr account and create two new blogs:

* $NEW_TUMBLOG_NAME.tumblr.com (this will be our production blog)
* $NEW_TUMBLOG_NAME-staging.tumblr.com (this will be our staging blog)

## Theme edits

Copy and paste our custom Tumblr theme into Tumblr's blog editor.

## Disqus setup

Navigate to "customize blog" and enter our Disqus shortname (found in Dropbox) under "Disqus shortname."

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
=======
Edit ``README.md`` and document the project name and what it will do.
>>>>>>> master

Bootstrap issues
----------------

The app-template can automatically setup your Github repo with our default labels and tickets by running ``fab bootstrap_issues``. You will be prompted for your Github username and password.

Develop with the template
----------------------------
If you followed the [Copy the template](#copy-the-template) instructions above you will have replaced `README.md` (this file) with `PROJECT_README.md`. See that file for all the details of how build projects with the app-template.

On the ``init-tumblr`` branch, ``app.py`` is used for the Tumblr form which will be baked out to a flat file that can then be embedded in the tumblog.

To run the simple app that will post to Tumblr (via an intermediate server for image uplaods):

```
python public_app.py
```

This will run the simple app on [localhost:8001](http://localhost:8001).

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

Deploy the app
-----------------

There are two parts – deploy the form to S3 and the simple app (`public_app.py`) to EC2. See the next two sections for more details on S3 and EC2, but a high level workflow is:

* Run ``fab <ENV> master setup`` to configure the server (where ``<ENV>`` is either staging or production).
* Run ``fab <ENV> master deploy`` to deploy the app.
* Run ``fab <ENV> deploy_confs`` to render the server conf files (nginx and uwsgi) and then deploy them to the server. This will also restart the app on the server.

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

Deploy Tumblr themes
---------------------

The base Tumblr theme is in the `tumblr/theme.html` file. There are included templates in `templates/`: `_form.html`, `_prompt.html` and `_social.html`. There are also two new constants in `app_config.py`: `PROJECT_CREDITS` and `PROJECT_SHORTLINK`. These should be changed on a per-project basis.

To deploy a Tumblr theme with **local** URLs, type `fab staging copy_theme` and the theme will be copied to your clipboard to paste into Tumblr. **Note:** This only works on Mac OSX. On Linux or Windows, use `fab staging write_theme` and manually copy the theme HTML from `tumblr/rendered-theme.html`.

To deploy a Tumblr theme with **production** URLs, type `fab production copy_theme` and the theme will be copied to your clipbaord to paste into Tumblr. **Note:** This only works on Mac OSX. On Linux or Windows, use `fab production write_theme` and manually copy the theme HTML from `tumblr/rendered-theme.html`.
-------------------------

If you followed the [Copy the template](#copy-the-template) instructions above you will have replaced `README.md` (this file) with `PROJECT_README.md`. See that file for all the details of how build projects with the app-template.

Merging init branches
---------------------

To merge changes on ``master`` into each of the ``init-`` branches, use the following process:

```
git fetch
git checkout master

# For each branch
git checkout init-foo
git merge origin/init-foo --no-edit
git merge master --no-edit

git checkout master
git push --all
```
