#!/usr/bin/env python

import csv
from exceptions import KeyError
import os

import requests

class GoogleDoc(object):
    """
    A class for accessing a Google document as an object.
    Includes the bits necessary for accessing the document and auth and such.
    For example:

        doc = {
            "key": "123456abcdef",
            "gid": "4",
            "file_format": "csv",
            "file_name": "my_google_doc"
        }
        g = GoogleDoc(**doc)
        g.get_auth()
        g.get_document()

    Will download your google doc to data/my_google_doc.csv in the CSV format.
    """

    # You can update these values with kwargs.
    # In fact, you better pass a key or else it won't work!
    key = None
    gid = "0"
    file_format = "xls"
    file_name = "copy"

    # You can change these with kwargs but it's not recommended.
    spreadsheet_url = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%s"
    auth = None
    email = os.environ.get('APPS_GOOGLE_EMAIL', None)
    password = os.environ.get('APPS_GOOGLE_PASS', None)
    scope = "https://spreadsheets.google.com/feeds/"
    service = "wise"
    session = "1"

    def __init__(self, **kwargs):
        """
        Because sometimes, just sometimes, you need to update the class when you instantiate it.
        In this case, we need, minimally, a document key.
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

        else:
            headers = {}
            headers['Authorization'] = "GoogleLogin auth=%s" % self.auth

            r = requests.get(self.spreadsheet_url % (self.key, self.file_format, self.gid), headers=headers)

            if r.status_code != 200:
                raise KeyError("Error! Your Google Doc does not exist.")

            else:
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
    doc['file_name'] = 'gdoc_%s.%s' % (doc['key'], doc['file_format'])

    g = GoogleDoc(**doc)
    g.get_auth()
    g.get_document()
    g.parse_document()
