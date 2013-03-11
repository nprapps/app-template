#!/usr/bin/env python

import json
import unittest

import app
import app_config

class IndexTestCase(unittest.TestCase):
    """
    Test the index page.
    """
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    def test_index_exists(self):
        response = self.client.get('/')

        assert app_config.PROJECT_NAME in response.data

class AppConfigTestCase(unittest.TestCase):
    """
    Testing dynamic conversion of Python app_config into Javascript. 
    """
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    def parse_data(self, response):
        """
        Trim leading variable declaration and load JSON data.
        """
        return json.loads(response.data[20:])

    def test_app_config_staging(self):
        response = self.client.get('/js/app_config.js')

        data = self.parse_data(response)

        assert data['DEBUG'] == True 

    def test_app_config_production(self):
        app_config.configure_targets('production')

        response = self.client.get('/js/app_config.js')

        data = self.parse_data(response)

        assert data['DEBUG'] == False 
        
        app_config.configure_targets('staging')

if __name__ == '__main__':
    unittest.main()
