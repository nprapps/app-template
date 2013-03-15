#!/usr/bin/env python

from dulwich import repo

import envoy
import subprocess
import os
import shutil
import filecmp

shutil.rmtree('.screencaptures', True)
os.mkdir('.screencaptures')

# Make temp copies of script files so they aren't missing in old commits
shutil.copyfile('etc/screencapture.js', '.screencaptures/screencapture.js')
shutil.copyfile('etc/darkness.jpg', '.screencaptures/darkness.jpg')

git = repo.Repo('.')
history = git.revision_history(git.head())

history.reverse()

last_filename = None

for i, commit in enumerate(history):
    sha = commit.id
    timestamp = commit.commit_time
    filename = '.screencaptures/%s.jpg' % timestamp

    print "%i Checking out commit %s" % (i, sha)
    envoy.run('git checkout %s' % sha)

    if not os.path.exists('app.py'):
        print '--> No app.py, skipping.'
        continue
    
    p = subprocess.Popen(['python', 'app.py'])
    r = envoy.run('phantomjs .screencaptures/screencapture.js %s' % filename)
    p.kill()
    
    if not os.path.exists(filename):
        print '--> Phantom failed to generate an image.'
        continue

    if last_filename and filecmp.cmp(last_filename, filename, False):
        print '--> Removing duplicate image %s.' % filename
        os.remove(filename)
    else:
        if filecmp.cmp(filename, '.screencaptures/.darkness.jpg', False):
            print '--> Removing darkness %s (blank image).' % filename
            os.remove(filename)
        else:
            last_filename = filename

# Remove temp files
os.remove('.screencaptures/.screencapture.js')
os.remove('.screencaptures/.darkness.jpg')

shutil.copyfile(last_filename, '.screencaptures/0.jpg')

proc = subprocess.Popen(['ffmpeg', '-f', 'image2', '-r', '2', '-qscale', '2', '-pattern_type', 'glob', '-i', '*.jpg', 'video.mp4'], cwd='.screencaptures')
proc.wait()
