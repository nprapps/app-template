#!/usr/bin/env python

import csv
from exceptions import KeyError
import os

import requests

class GoogleDoc(object):
    """
    A class for accessing a Google document as an object.
    Includes the bits necessary for accessing the document and auth and such.
    """
    key = None
    gid = "0"

    spreadsheet_url = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=csv&gid=%s"

    auth = None
    email = os.environ.get('APPS_GOOGLE_EMAIL', None)
    password = os.environ.get('APPS_GOOGLE_PASS', None)
    scope = "https://spreadsheets.google.com/feeds/"
    service = "wise"
    session = "1"

    file_format = "xls"
    file_name = "copy"

    def __init__(self, **kwargs):
        """
        Because sometimes, just sometimes, you need to update the class when you instantiate it.
        In this case, we need, minimally, a document key and a gid -- sheet number.
        """
        if kwargs:
            if kwargs.items():
                for key, value in kwargs.items():
                    setattr(self, key, value)

    def get_auth(self):
        """
        Gets an authorization token and adds it to the class.
        """
        data = {}
        if not self.email or not self.password:
            raise KeyError("Error! You're missing some variables. You need to export APPS_GOOGLE_EMAIL and APPS_GOOGLE_PASS.")

        else:
            data['Email'] = self.email
            data['Passwd'] = self.password
            data['scope'] = self.scope
            data['service'] = self.service
            data['session'] = self.session

            r = requests.post("https://www.google.com/accounts/ClientLogin", data=data)

            self.auth = r.content.split('\n')[2].split('Auth=')[1]

    def get_document(self):
        """
        Uses the authentication token to fetch a google doc.
        """

        # Handle basically all the things that can go wrong.
        if not self.auth:
            raise KeyError("Error! You didn't get an auth token. Something very bad happened. File a bug?")

        elif not self.key:
            raise KeyError("Error! You forgot to pass a key to the class.")

        elif not self.gid:
            raise KeyError("Error! You forgot to pass a gid (sheet number) to the class.")

        else:
            headers = {}
            headers['Authorization'] = "GoogleLogin auth=%s" % self.auth

            r = requests.get(self.spreadsheet_url % (self.key, self.gid), headers=headers)

            with open('data/%s.%s' % (self.file_name, self.file_format), 'wb') as writefile:
                writefile.write(r.content)

    def parse_document(self):
        """
        A stub method for reading the document after it's been downloaded.
        """
        with open('data/gdoc_%s.csv' % self.key, 'rb') as readfile:
            csv_file = list(csv.DictReader(readfile))

        print csv_file


if __name__ == "__main__":
    """
    Here's an example of how to use the class.
    Don't forget to pass a key and a gid!
    """
    doc = {}
    doc['key'] = '0ArVJ2rZZnZpDdEFxUlY5eDBDN1NCSG55ZXNvTnlyWnc'
    doc['gid'] = '4'
    doc['file_format'] = 'csv'

    g = GoogleDoc(**doc)
    g.get_auth()
    g.get_document()
    g.parse_document()