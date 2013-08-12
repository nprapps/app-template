#!/usr/bin/env python

"""
Given an input path and an output path, will put
Gzipped versions of all files from the input path
to the output path.

If the file is not gzippable it will be copied
uncompressed.
"""

from fnmatch import fnmatch
import gzip
import os
import shutil
import sys

class FakeTime:
    def time(self):
        return 1261130520.0

# Hack to override gzip's time implementation
# See: http://stackoverflow.com/questions/264224/setting-the-gzip-timestamp-from-python
gzip.time = FakeTime()

def is_compressable(filename, gzip_globs):
    """
    Determine if a filename is a gzippable type
    by comparing to a known list.
    """
    return any([fnmatch(filename, glob) for glob in gzip_globs])

def compress(file_path):
    """
    Gzip a single file in place.
    """
    f_in = open(file_path, 'rb')
    contents = f_in.readlines()
    f_in.close()
    f_out = gzip.open(file_path, 'wb')
    f_out.writelines(contents)
    f_out.close()

def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open('gzip_types.txt') as f:
        gzip_globs = [glob.strip() for glob in f]

    # Folders
    if os.path.isdir(in_path):
        shutil.rmtree(out_path, ignore_errors=True)
        shutil.copytree(in_path, out_path)

        for path, dirs, files in os.walk(sys.argv[2]):
            for filename in files:
                # Is it a gzippable file type?
                if not is_compressable(filename, gzip_globs):
                    continue

                file_path = os.path.join(path, filename)

                compress(file_path)
    # Single files
    else:
        filename = os.path.split(in_path)[-1]

        try:
            os.remove(out_path)
        except OSError:
            pass

        shutil.copy(in_path, out_path)

        if not is_compressable(filename, gzip_globs):
            return 

        compress(out_path)


if __name__ == '__main__':
    main()
