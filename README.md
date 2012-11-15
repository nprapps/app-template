nprapps' Project Template
=========================

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
* Uncomment and update the ad code and Facebook tags at the top of ``www/index.html`` (or make yourself a note to do it later).

Install requirements
--------------------

```
mkvirtualenv $NEW_PROJECT_NAME
pip install -r requirements.txt
```

Running the project locally
---------------------------

```
workon $NEW_PROJECT_NAME
fab build_assets
cd www
python -m SimpleHTTPServer
```

Visit ``localhost:8000`` in your browser.

Deploying the project
---------------------

```
fab staging master deploy
```

Deploying to a server
---------------------

The current configuration is for running cron jobs only. Web server configuration is not yet included.

* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app. 
