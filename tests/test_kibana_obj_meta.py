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

import unittest

from archimedes.kibana_obj_meta import KibanaObjMeta


DASHBOARD_REG_ENTRY = {
    "id": "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad",
    "type": "dashboard",
    "updated_at": "2019-01-24T13:20:08.902Z",
    "version": 9,
    "title": "GitLab Issues"
}

DASHBOARD_REG_ENTRY_NO_UPDATED_AT = {
    "id": "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad",
    "type": "dashboard",
    "version": 9,
    "title": "GitLab Issues"
}

DASHBOARD_OBJ = {
    "attributes": {
        "description": "GitLab Issues panel by Bitergia",
        "hits": 0,
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": "..."
        },
        "optionsJSON": "{\"darkTheme\":false,\"hidePanelTitles\":false,\"useMargins\":true}",
        "panelsJSON": "...",
        "timeRestore": "false",
        "title": "GitLab Issues",
        "uiStateJSON": "...",
        "version": 1
    },
    "id": "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad",
    "type": "dashboard",
    "updated_at": "2019-01-24T13:20:08.902Z",
    "version": 9
}

DASHBOARD_OBJ_NO_UPDATED_AT = {
    "attributes": {
        "description": "GitLab Issues panel by Bitergia",
        "hits": 0,
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": "..."
        },
        "optionsJSON": "{\"darkTheme\":false,\"hidePanelTitles\":false,\"useMargins\":true}",
        "panelsJSON": "...",
        "timeRestore": "false",
        "title": "GitLab Issues",
        "uiStateJSON": "...",
        "version": 1
    },
    "id": "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad",
    "type": "dashboard",
    "version": 9
}


class TestMetaObj(unittest.TestCase):
    """MetaObj tests"""

    def test_initialization(self):
        """Test whether attributes are initialized"""

        obj = KibanaObjMeta(id=DASHBOARD_OBJ['id'],
                            title=DASHBOARD_OBJ['attributes']['title'],
                            type=DASHBOARD_OBJ['type'],
                            version=DASHBOARD_OBJ['version'],
                            updated_at=DASHBOARD_OBJ['updated_at'])

        self.assertEqual(obj.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(obj.title, "GitLab Issues")
        self.assertEqual(obj.type, "dashboard")
        self.assertEqual(obj.version, 9)
        self.assertEqual(obj.updated_at, "2019-01-24T13:20:08.902Z")

    def test_initialization_no_updated_at(self):
        """Test whether attributes are initialized"""

        obj = KibanaObjMeta(id=DASHBOARD_OBJ_NO_UPDATED_AT['id'],
                            title=DASHBOARD_OBJ_NO_UPDATED_AT['attributes']['title'],
                            type=DASHBOARD_OBJ_NO_UPDATED_AT['type'],
                            version=DASHBOARD_OBJ_NO_UPDATED_AT['version'])

        self.assertEqual(obj.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(obj.title, "GitLab Issues")
        self.assertEqual(obj.type, "dashboard")
        self.assertEqual(obj.version, 9)
        self.assertIsNone(obj.updated_at)

    def test_create_from_obj(self):
        """Test whether a meta object is correctly created from a Kibana object"""

        meta = KibanaObjMeta.create_from_obj(DASHBOARD_OBJ)
        self.assertEqual(meta.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(meta.title, "GitLab Issues")
        self.assertEqual(meta.type, "dashboard")
        self.assertEqual(meta.version, 9)
        self.assertEqual(meta.updated_at, "2019-01-24T13:20:08.902Z")

        meta = KibanaObjMeta.create_from_obj(DASHBOARD_OBJ_NO_UPDATED_AT)
        self.assertEqual(meta.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(meta.title, "GitLab Issues")
        self.assertEqual(meta.type, "dashboard")
        self.assertEqual(meta.version, 9)
        self.assertIsNone(meta.updated_at)

    def test_create_from_registry(self):
        """Test whether a meta object is correctly created from a registry entry"""

        meta = KibanaObjMeta.create_from_registry(DASHBOARD_REG_ENTRY)
        self.assertEqual(meta.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(meta.title, "GitLab Issues")
        self.assertEqual(meta.type, "dashboard")
        self.assertEqual(meta.version, 9)
        self.assertEqual(meta.updated_at, "2019-01-24T13:20:08.902Z")

        meta = KibanaObjMeta.create_from_registry(DASHBOARD_REG_ENTRY_NO_UPDATED_AT)
        self.assertEqual(meta.id, "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad")
        self.assertEqual(meta.title, "GitLab Issues")
        self.assertEqual(meta.type, "dashboard")
        self.assertEqual(meta.version, 9)
        self.assertIsNone(meta.updated_at)

    def test_repr(self):
        """Test whether the repr method properly works"""

        obj = KibanaObjMeta.create_from_obj(DASHBOARD_OBJ)
        str_repr = repr(obj)

        expected = {
            'id': obj.id,
            'type': obj.type,
            'version': obj.version,
            'title': obj.title,
            'updated_at': obj.updated_at
        }

        self.assertEqual(str_repr, json.dumps(expected, sort_keys=True, indent=4))

    def test_repr_no_updated_at(self):
        """Test whether the repr method doesn't fail when updated_at is null"""

        obj = KibanaObjMeta.create_from_obj(DASHBOARD_OBJ_NO_UPDATED_AT)
        str_repr = repr(obj)

        expected = {
            'id': obj.id,
            'type': obj.type,
            'version': obj.version,
            'title': obj.title
        }

        self.assertEqual(str_repr, json.dumps(expected, sort_keys=True, indent=4))


if __name__ == "__main__":
    unittest.main(warnings='ignore')
