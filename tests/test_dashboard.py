# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Valerio Cosentino <valcos@bitergia.com>
#

import json
import os
import unittest

import httpretty
import requests

from archimedes.clients.http import HEADERS
from archimedes.clients.dashboard import (logger,
                                          Dashboard)
from archimedes.errors import DataExportError


KIBANA_URL = 'http://example.com/'
DASHBOARD_ID = 'Git'
DASHBOARD_EXPORT_URL = \
    KIBANA_URL + Dashboard.API_DASHBOARDS_URL + '/' + Dashboard.API_EXPORT_COMMAND + '?dashboard=' + DASHBOARD_ID
DASHBOARD_IMPORT_URL = KIBANA_URL + Dashboard.API_DASHBOARDS_URL + '/' + Dashboard.API_IMPORT_COMMAND


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestDashboard(unittest.TestCase):
    """Dashboard API tests"""

    def test_initialization(self):
        """Test whether attributes are initialized"""

        client = Dashboard(KIBANA_URL)

        self.assertEqual(client.base_url, KIBANA_URL)
        self.assertIsNotNone(client.session)
        self.assertEqual(client.session.headers['kbn-xsrf'], HEADERS.get('kbn-xsrf'))
        self.assertEqual(client.session.headers['Content-Type'], HEADERS.get('Content-Type'))

    @httpretty.activate
    def test_export_dashboard(self):
        """Test whether a dashboard is correctly exported"""

        dashboard_objs = read_file('data/dashboard')

        httpretty.register_uri(httpretty.GET,
                               DASHBOARD_EXPORT_URL,
                               body=dashboard_objs,
                               status=200)

        client = Dashboard(KIBANA_URL)
        objs = client.export_dashboard(DASHBOARD_ID)
        self.assertDictEqual(objs, json.loads(dashboard_objs))

    @httpretty.activate
    def test_export_dashboard_error(self):
        """Test whether an error message is logged when the export fails"""

        dashboard_objs = read_file('data/dashboard_error')

        httpretty.register_uri(httpretty.GET,
                               DASHBOARD_EXPORT_URL,
                               body=dashboard_objs,
                               status=200)

        client = Dashboard(KIBANA_URL)
        with self.assertRaises(DataExportError):
            _ = client.export_dashboard(DASHBOARD_ID)

    @httpretty.activate
    def test_export_dashboard_impossible(self):
        """Test whether an error message is logged when a 400 HTTP error is returned"""

        dashboard_objs = read_file('data/dashboard_error')

        httpretty.register_uri(httpretty.GET,
                               DASHBOARD_EXPORT_URL,
                               body=dashboard_objs,
                               status=400)

        client = Dashboard(KIBANA_URL)
        with self.assertRaises(DataExportError):
            _ = client.export_dashboard(DASHBOARD_ID)

    @httpretty.activate
    def test_export_dashboard_http_error(self):
        """Test whether an exception is thrown when the HTTP error is not 400"""

        dashboard_objs = read_file('data/dashboard_error')

        httpretty.register_uri(httpretty.GET,
                               DASHBOARD_EXPORT_URL,
                               body=dashboard_objs,
                               status=500)

        client = Dashboard(KIBANA_URL)
        with self.assertRaises(requests.exceptions.HTTPError):
            _ = client.export_dashboard(DASHBOARD_ID)

    @httpretty.activate
    def test_import_objects(self):
        """Test whether the objects that compose a dashboard are correctly imported"""

        dashboard_objs = read_file('data/dashboard')
        dashboard_objs_json = json.loads(dashboard_objs)

        httpretty.register_uri(httpretty.POST,
                               DASHBOARD_IMPORT_URL,
                               body=dashboard_objs,
                               status=200)

        client = Dashboard(KIBANA_URL)

        with self.assertLogs(logger, level='INFO') as cm:
            _ = client.import_objects(dashboard_objs_json)
            expected = {
                'force': [
                    'false'
                ]
            }

            self.assertEqual(cm.output[0],
                             'INFO:archimedes.clients.dashboard:12/12 object(s) imported')
            self.assertDictEqual(httpretty.last_request().querystring, expected)

        with self.assertLogs(logger, level='INFO') as cm:
            _ = client.import_objects(dashboard_objs_json, exclude_dashboards=True, exclude_index_patterns=True,
                                      exclude_visualizations=True, exclude_searches=True, force=True)
            expected = {
                'force': [
                    'true'
                ],
                'exclude': [
                    'dashboard',
                    'index-pattern',
                    'visualization',
                    'search'
                ]
            }

            self.assertEqual(cm.output[0],
                             'INFO:archimedes.clients.dashboard:12/12 object(s) imported')
            self.assertDictEqual(httpretty.last_request().querystring, expected)

    @httpretty.activate
    def test_import_objects_error(self):
        """Test whether errors are logged for the objects which were not imported"""

        dashboard_objs = read_file('data/dashboard_error')
        dashboard_objs_json = json.loads(dashboard_objs)

        httpretty.register_uri(httpretty.POST,
                               DASHBOARD_IMPORT_URL,
                               body=dashboard_objs,
                               status=200)

        client = Dashboard(KIBANA_URL)

        with self.assertLogs(logger, level='INFO') as cm:
            _ = client.import_objects(dashboard_objs_json)
            expected = {
                'force': [
                    'false'
                ]
            }

            self.assertEqual(cm.output[0],
                             'ERROR:archimedes.clients.dashboard:dashboard with id Git not imported, '
                             'an internal server error occurred')
            self.assertEqual(cm.output[1],
                             'INFO:archimedes.clients.dashboard:11/12 object(s) imported')
            self.assertDictEqual(httpretty.last_request().querystring, expected)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
