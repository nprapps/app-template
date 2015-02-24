#!/usr/bin/env python

import os
import requests

from exceptions import KeyError

SPREADSHEET_URL_TEMPLATE = 'https://docs.google.com/feeds/download/spreadsheets/Export?exportFormat=xlsx&key=%s'

class GoogleDoc(object):
    """
    A class for accessing a Google document as an object.
    Includes the bits necessary for accessing the document and auth and such.
    For example:

        doc = {
            "key": "123456abcdef",
            "file_path": "data/copy.xlsx",
            "automatic": authomatic_instance,
            "credentials": "serialized-credentials",
        }
        g = GoogleDoc(**doc)
        g.get_document()

    Will download your google doc to `file_path`.
    """

    def __init__(self, key, authomatic, credentials, file_path):
        self.key = key
        self.authomatic = authomatic
        self.credentials = credentials
        self.file_path = file_path

    def get_document(self):
        """
        Uses Authomatic to get the google doc
        """

        response = self.authomatic.access(self.credentials, SPREADSHEET_URL_TEMPLATE % self.key)
        #import ipdb; ipdb.set_trace();

        #if r.status != 200:
            #raise KeyError("Error! Your Google Doc does not exist.")

        with open(self.file_path, 'wb') as writefile:
            writefile.write(response.content)
