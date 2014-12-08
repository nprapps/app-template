nprviz's Project Template
=========================

* [About this template](#about-this-template)
* [Assumptions](#assumptions)
* [Copy the template](#copy-the-template)
* [Configure the project](#configure-the-project)
* [Bootstrap issues](#bootstrap-issues)
* [Develop with the template](#develop-with-the-template)

About this template
-------------------

This template provides a a project skeleton suitable for NPR projects that are designed to be served as flat files. Facilities are provided for rendering html from data, compiling LESS into CSS, deploying to S3, installing cron jobs on servers, copy-editing via Google Spreadsheets and a whole bunch of other stuff.

This codebase is licensed under the [MIT open source license](http://opensource.org/licenses/MIT). See the ``LICENSE`` file for the complete license.

Please note: logos, fonts and other media referenced via url from this template are **not** covered by this license. Do not republish NPR media assets without written permission. Open source libraries in this repository are redistributed for convenience and are each governed by their own license.

Also note: Though open source, This project is not intended to be a generic solution. We strongly encourage those who love the app-template to use it as a basis for their own project template. We have no plans to remove NPR-specific code from this project.

If you want to setup a version of the app template for yourself, read [this blog post](http://blog.apps.npr.org/2014/09/08/how-to-setup-the-npr-app-template-for-you-and-your-news-org.html) about how to do so.

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have NPR's AWS credentials stored as environment variables locally.

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

Copy the template
-----------------

Create a new repository on Github. Everywhere you see ``$NEW_PROJECT_NAME`` in the following script, replace it with the name of the repository you just created.

```
git clone git@github.com:nprapps/app-template.git $NEW_PROJECT_NAME
cd $NEW_PROJECT_NAME

mkvirtualenv $NEW_PROJECT_NAME
pip install -r requirements.txt
npm install

fab bootstrap
```

This will setup the new repo and will replace `README.md` (this file) with `PROJECT_README.md`. See that file for usage documentation.

By default `bootstrap` will use `nprapps` as the Github username, and the current directory name as the repository name. **This is a best practice**, but you can override these defaults if you need to:

```
fab bootstrap:$GITHUB_USERNAME,$REPOSITORY_NAME
```

**Problems installing requirements?** You may need to run the pip command as ``ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements.txt`` to work around an issue with OSX.

Bootstrap issues
----------------

The app-template can automatically setup your Github repo with our default labels and tickets by running ``fab issues.bootstrap``. You will be prompted for your Github username and password.

