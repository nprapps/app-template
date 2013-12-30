#!/usr/bin/env python

import csv
import os

import requests

class GoogleDoc(object):

    key = None
    guid = None

    spreadsheet_url = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=csv&gid=%s"

    auth = None
    email = os.environ.get('APPS_GOOGLE_EMAIL', None)
    password = os.environ.get('APPS_GOOGLE_PASS', None)
    scope = "https://spreadsheets.google.com/feeds/"
    service = "wise"
    session = "1"

    def __init__(self, **kwargs):
        if kwargs:
            if kwargs.items():
                for key, value in kwargs.items():
                    setattr(self, key, value)

    def get_auth(self):
        data = {}
        if not self.email or not self.password:
            print "You're missing some variables\nYou need to export APPS_GOOGLE_EMAIL and APPS_GOOGLE_PASS."

        else:
            data['Email'] = self.email
            data['Passwd'] = self.password
            data['scope'] = self.scope
            data['service'] = self.service
            data['session'] = self.session

            r = requests.post("https://www.google.com/accounts/ClientLogin", data=data)

            self.auth = r.content.split('\n')[2].split('Auth=')[1]

            print self.auth

    def get_document(self):
        if not self.auth:
            print "Oops, not authenticated."

        else:
            headers = {}
            headers['Authorization'] = "GoogleLogin auth=%s" % self.auth

            r = requests.get(self.spreadsheet_url % (self.key, self.guid), headers=headers)

            with open('data/data.csv', 'wb') as writefile:
                writefile.write(r.content)

    def parse_document(self):
        with open('data/data.csv', 'rb') as readfile:
            csv_file = list(csv.DictReader(readfile))

        print csv_file


if __name__ == "__main__":
    g = GoogleDoc()
    g.get_auth()
    g.get_document()
    g.parse_document()