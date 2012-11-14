#!/usr/bin/env python

import os
import gzip
import shutil

class FakeTime:
    def time(self):
        return 1261130520.0

# Hack to override gzip's time implementation
# See: http://stackoverflow.com/questions/264224/setting-the-gzip-timestamp-from-python
gzip.time = FakeTime()

shutil.rmtree('gzip', ignore_errors=True)
shutil.copytree('www', 'gzip')

for path, dirs, files in os.walk('gzip'):
    for filename in files:
        file_path = os.path.join(path, filename)
        
        f_in = open(file_path, 'rb')
        contents = f_in.readlines()
        f_in.close()
        f_out = gzip.open(file_path, 'wb')
        f_out.writelines(contents)
        f_out.close();
