nprapps' Project Template
=========================

About this template
-------------------

This template provides a a project skeleton suitable for any project that is to be served entirely as flat files. Facilities are provided for rendering html from data, compiling LESS into CSS, deploying to S3, etc.

What's in here?
---------------

The project contains the following folders and important files:

* ``data`` -- Data files, such as those used to generate HTML
* ``etc`` -- Miscellaneous scripts and metadata for project bootstrapping.
* ``jst`` -- Javascript ([Underscore.js](http://documentcloud.github.com/underscore/#template)) templates 
* ``less`` -- [LESS](http://lesscss.org/) files, will be compiled to CSS and concatenated for deployment
* ``templates`` -- HTML ([Jinja2](http://jinja.pocoo.org/docs/)) templates, to be compiled locally
* ``www`` -- Static and compiled assets to be deployed (a.k.a. "the output")
* ``app.py`` -- A [Flask](http://flask.pocoo.org/) app for rendering the project locally.
* ``app_config.py`` -- Global project configuration for scripts, deployment, etc.
* ``fabfile.py`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands automating setup and deployment

Copy the template
-----------------

```
git clone git@github.com:nprapps/app-template.git $NEW_PROJECT_NAME
cd $NEW_PROJECT_NAME
rm -rf .git
git init
git add *
git add .gitignore
git commit -am "Initial import from app-template."
git remote add origin git@github.com:nprapps/$NEW_PROJECT_NAME.git
git push -u origin master
```

Configure the project
---------------------

* Update ``app_config.py`` with the name of the new project.

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

Bootstrap your project issues
-----------------------------

The app-template can automatically setup your Github repo with our default labels and tickets.

* Run ``fab bootstrap_issues`` and enter your Github username and password.

Generate index.html
-------------------

The app-template ships with several example templates and corresponding views.

* Choose from the available templates which one to base your project on, e.g. ``templates/table.html``. Move this template to ``templates/index.html`` and delete the others.
* Never edit ``www/index.html`` or other dynamically generated assets. Instead edit the templates.
* Choose the view from ``app.py`` that matches your chosen index template. Rename it to ``index``, apply the ``@app.route('/')`` decorator to it and delete the others.  
* Uncomment and update the ad code and Facebook tags at the top of ``templates/_base.html``. (or make yourself a ticket to do it later).

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

Visit ``localhost:8000`` in your browser.

Compile with static assets
--------------------------

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

Deploy to a server
------------------

The current configuration is for running cron jobs only. Web server configuration is not included.

* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app. 
