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

import unittest

from archimedes.kibana import Kibana
from archimedes.clients.saved_objects import SavedObjects
from archimedes.clients.dashboard import (Dashboard,
                                          DASHBOARD,
                                          VISUALIZATION)
from archimedes.errors import (ObjectTypeError,
                               NotFoundError)

KIBANA_URL = 'http://example.com/'

DASHBOARD_ID = 'dashboard-id'
DASHBOARD_TITLE = 'dashboard-title'
VISUALIZATION_ID = 'visualization-id'
VISUALIZATION_TITLE = 'visualization-title'

OBJECTS = [
    [
        {
            "attributes": {
                "description": "",
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": "..."
                },
                "title": DASHBOARD_TITLE,
                "uiStateJSON": "{}",
                "version": 1,
                "visState": "..."
            },
            "id": DASHBOARD_ID,
            "type": "dashboard",
            "version": 1
        },
        {
            "attributes": {
                "description": "",
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": "{}"
                },
                "title": VISUALIZATION_TITLE,
                "uiStateJSON": "{}",
                "version": 1,
                "visState": "..."
            },
            "id": VISUALIZATION_ID,
            "type": "visualization",
            "version": 1
        }
    ]
]


class MockedKibana(Kibana):
    def __init__(self, base_url, content):
        super().__init__(base_url)

        self.dashboard = MockedDashboard(base_url, content)
        self.saved_objects = MockedSavedObjects(base_url, content)


class MockedDashboard(Dashboard):
    def __init__(self, base_url, content):
        super().__init__(base_url)
        self.content = content

    def export_dashboard(self, dashboard_id):
        return self.content


class MockedSavedObjects(SavedObjects):
    def __init__(self, base_url, content):
        super().__init__(base_url)
        self.content = content

    def get_object(self, obj_type, obj_id):
        return self.content

    def fetch_objs(self, url):
        return self.content


class TestKibana(unittest.TestCase):
    """Kibana tests"""

    def test_initialization(self):
        """Test whether attributes are initialized"""

        kibana = Kibana(KIBANA_URL)

        self.assertIsNotNone(kibana.dashboard)
        self.assertIsNotNone(kibana.saved_objects)

    def test_export_by_id(self):
        """Test whether the export by id properly works"""

        expected = {"content": "..."}

        kibana = MockedKibana(KIBANA_URL, expected)

        self.assertDictEqual(kibana.export_by_id(DASHBOARD, "dashboard_test"), expected)
        self.assertDictEqual(kibana.export_by_id(VISUALIZATION, "visualization_test"), expected)

    def test_export_by_id_type_error(self):
        """Test whether an error is thrown when the object type is not recognized"""

        expected = {"content": "..."}

        kibana = MockedKibana(KIBANA_URL, expected)

        with self.assertRaises(ObjectTypeError):
            kibana.export_by_id("unknown", "unknown")

    def test_export_by_id_not_found(self):
        """Test whether an error is thrown when the object is not found"""

        expected = {}

        kibana = MockedKibana(KIBANA_URL, expected)

        with self.assertRaises(NotFoundError):
            kibana.export_by_id(DASHBOARD, "unknown")

    def test_export_by_title(self):
        """Test whether the export by title properly works"""

        expected_visualization = OBJECTS[0][1]

        kibana = MockedKibana(KIBANA_URL, OBJECTS)

        self.assertDictEqual(kibana.export_by_title(VISUALIZATION, VISUALIZATION_TITLE), expected_visualization)

    def test_export_by_title_type_error(self):
        """Test whether an error is thrown when the object type is not recognized"""

        kibana = MockedKibana(KIBANA_URL, OBJECTS)

        with self.assertRaises(ObjectTypeError):
            kibana.export_by_title("unknown", "unknown")

    def test_export_by_title_not_found_error(self):
        """Test whether an error is thrown when the object is not found"""

        kibana = MockedKibana(KIBANA_URL, OBJECTS)

        with self.assertRaises(NotFoundError):
            kibana.export_by_title(DASHBOARD, "unknown")

    def test_find_by_title(self):
        """Test whether an object is found by title"""

        expected = OBJECTS[0][0]

        kibana = MockedKibana(KIBANA_URL, OBJECTS)
        obj = kibana.find_by_title(DASHBOARD, DASHBOARD_TITLE)

        self.assertDictEqual(obj, expected)

    def test_find_by_title_not_found(self):
        """Test whether an error is thrown when the object is not found"""

        kibana = MockedKibana(KIBANA_URL, OBJECTS)

        with self.assertRaises(NotFoundError):
            kibana.find_by_title("unknown", "unknown")

    def test_find_by_id(self):
        """Test whether an object is found by id"""

        expected = OBJECTS[0][0]

        kibana = MockedKibana(KIBANA_URL, OBJECTS)
        obj = kibana.find_by_id(DASHBOARD, DASHBOARD_ID)

        self.assertDictEqual(obj, expected)

    def test_find_by_id_not_found(self):
        """Test whether an error is thrown when the object is not found"""

        kibana = MockedKibana(KIBANA_URL, OBJECTS)

        with self.assertRaises(NotFoundError):
            kibana.find_by_id("unknown", "unknown")

    def test_find_all(self):
        """Test whether all objects in Kibana are retrieved"""

        kibana = MockedKibana(KIBANA_URL, OBJECTS)
        objs = [obj for obj in kibana.find_all()]

        self.assertEqual(len(objs), 2)
        self.assertDictEqual(objs[0], OBJECTS[0][0])
        self.assertDictEqual(objs[1], OBJECTS[0][1])


if __name__ == "__main__":
    unittest.main(warnings='ignore')
