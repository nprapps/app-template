nprapps' Project Template
=========================

* [About this template](#about-this-template)
* [Copy the template](#copy-the-template)
* [Configure the project](#configure-the-project)
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

mkvirtualenv --no-site-packages $NEW_PROJECT_NAME
pip install -r requirements.txt

fab app_template_bootstrap
```

Bootstrap issues
----------------

The app-template can automatically setup your Github repo with our default labels and tickets by running ``fab bootstrap_issues``. You will be prompted for your Github username and password.

Develop with the template
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

