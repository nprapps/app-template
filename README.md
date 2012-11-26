nprapps' Project Template
=========================

About this template
-------------------

This template provides a a project skeleton suitable for any project that is to be served entirely as flat files. Facilities are provided for rendering html from data, compiling LESS into CSS, deploying to S3, etc.

What's in here?
---------------

The project contains the following folders and important files:

* ``data`` -- Data files, such as those used to generate HTML
* ``js`` -- Javascript files, will be concatenated for deployment
* ``jst`` -- Javascript ([Underscore.js](http://documentcloud.github.com/underscore/#template)) templates 
* ``less`` -- LESS files, will be compiled to CSS and concatenated for deployment
* ``templates`` -- HTML ([Jinja2](http://jinja.pocoo.org/docs/)) templates, to be compiled locally
* ``www`` -- Static and compiled assets to be deployed (a.k.a. "the output")
* ``app_config.py`` -- Global project configuration for scripts, deployment, etc.
* ``fabfile.py`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands automating setup and deployment
* ``grunt.js`` -- [Grunt.js](http://gruntjs.com/) commands automating asset compilation

Copying the template
--------------------

```
git clone git@github.com:nprapps/app-template.git $NEW_PROJECT_NAME
cd $NEW_PROJECT_NAME
git remote rm origin
git remote add origin https://github.com/nprapps/$NEW_PROJECT_NAME.git
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
```

Then install the project requirements:

```
npm install less grunt grunt-contrib-less grunt-contrib-jst
mkvirtualenv $NEW_PROJECT_NAME
pip install -r requirements.txt
```

Generating index.html
---------------------

* Run ``fab make_index`` to generate a blank index page.
* <strong>Or</strong>, for a table, run ``fab make_table:data/example.csv`` to use the table template.
* Uncomment and update the ad code and Facebook tags at the top of ``www/index.html`` (or make yourself a ticket to do it later).

Running the project locally
---------------------------

```
workon $NEW_PROJECT_NAME
fab grunt 
cd www
python -m SimpleHTTPServer
```

Visit ``localhost:8000`` in your browser.

Working with static assets
--------------------------

The asset pipeline is now handled with [grunt](http://gruntjs.com). 

To compile LESS to CSS, compile javascript templates to JS and minify all assets, run:

```
workon $NEW_PROJECT_NAME
fab grunt
```

To automatically run these processes when you change files, simply run:

```
workon $NEW_PROJECT_NAME
fab watch
```

Deploying the project
---------------------

```
fab staging master deploy
```

Deploying to a server
---------------------

The current configuration is for running cron jobs only. Web server configuration is not included.

* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app. 
