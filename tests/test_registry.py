# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Valerio Cosentino <valcos@bitergia.com>
#

import os
import shutil
import tempfile

import unittest

from archimedes.clients.dashboard import VISUALIZATION
from archimedes.errors import NotFoundError, RegistryError
from archimedes.kibana_obj_meta import KibanaObjMeta
from archimedes.registry import Registry, REGISTRY_NAME


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


def copy_content(filename, target_path):
    content = read_file(filename)

    with open(target_path, 'w') as f:
        f.write(content)


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


VISUALIZATION_OBJ_DUPLICATED = {
    "attributes": {
        "fieldFormatMap": "...",
        "fields": "...",
        "timeFieldName": "grimoire_creation_date",
        "title": "gitlab"
    },
    "id": "7c2496c0-b013-11e8-8771-a349686d998a",
    "type": "index-pattern",
    "version": 1
}


class TestRegistry(unittest.TestCase):
    """Registry tests"""

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp(prefix='archimedes_')

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initialized"""

        registry_path = os.path.join(self.tmp_path, REGISTRY_NAME)
        self.assertFalse(os.path.exists(registry_path))

        registry = Registry(self.tmp_path)

        self.assertEqual(registry.path, registry_path)
        self.assertTrue(os.path.exists(registry_path))

    def test_initialization_nested_dir(self):
        """Test whether a nested directory is created when initializing the registry"""

        nested_path = os.path.join(self.tmp_path, 'nested')
        registry_path = os.path.join(self.tmp_path, 'nested', REGISTRY_NAME)
        self.assertFalse(os.path.exists(nested_path))
        self.assertFalse(os.path.exists(registry_path))

        registry = Registry(nested_path)

        self.assertEqual(registry.path, registry_path)
        self.assertTrue(os.path.exists(registry_path))

    def test_find_all(self):
        """Test whether the find method returns all entries when no obj type is given"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]

        self.assertEqual(len(tuples), 11)

        tuples.sort()
        alias = tuples[0][0]
        expected_alias = '1'
        self.assertEqual(alias, expected_alias)

        info = tuples[0][1]
        expected_info = {
            'id': 'maniphest',
            'title': 'maniphest',
            'type': 'index-pattern',
            'updated_at': '2019-02-12T15:38:42.905Z',
            'version': 1
        }

        self.assertIsInstance(info, KibanaObjMeta)
        self.assertEqual(expected_info['id'], info.id)
        self.assertEqual(expected_info['title'], info.title)
        self.assertEqual(expected_info['type'], info.type)
        self.assertEqual(expected_info['updated_at'], info.updated_at)
        self.assertEqual(expected_info['version'], info.version)

    def test_find_all_type(self):
        """Test whether the find method returns only the aliases linked to a given obj type"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all(obj_type=VISUALIZATION)]

        self.assertEqual(len(tuples), 8)

        tuples.sort()
        alias = tuples[0][0]
        expected_alias = '2'
        self.assertEqual(alias, expected_alias)

        info = tuples[0][1]
        expected_info = {
            'id': 'maniphest_openissues_per_organization',
            'title': 'maniphest_openissues_per_organization',
            'type': 'visualization',
            'updated_at': '2019-02-12T15:38:51.091Z',
            'version': 1
        }

        self.assertIsInstance(info, KibanaObjMeta)
        self.assertEqual(expected_info['id'], info.id)
        self.assertEqual(expected_info['title'], info.title)
        self.assertEqual(expected_info['type'], info.type)
        self.assertEqual(expected_info['updated_at'], info.updated_at)
        self.assertEqual(expected_info['version'], info.version)

    def test_find_alias(self):
        """Test whether the find method returns a single entry when an alias is given"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        alias, meta = registry.find('1')

        expected_alias = '1'
        self.assertEqual(alias, expected_alias)

        expected_info = {
            'id': 'maniphest',
            'title': 'maniphest',
            'type': 'index-pattern',
            'updated_at': '2019-02-12T15:38:42.905Z',
            'version': 1
        }

        self.assertIsInstance(meta, KibanaObjMeta)
        self.assertEqual(expected_info['id'], meta.id)
        self.assertEqual(expected_info['title'], meta.title)
        self.assertEqual(expected_info['type'], meta.type)
        self.assertEqual(expected_info['updated_at'], meta.updated_at)
        self.assertEqual(expected_info['version'], meta.version)

    def test_find_not_found(self):
        """Test whether an exception is thrown when an alias is not found"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        with self.assertRaises(NotFoundError):
            _ = [t for t in registry.find(alias='x')]

    def test_clear(self):
        """Test whether the registry is cleared"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 11)

        registry.clear()

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 0)

    def test_delete_alias(self):
        """Test whether an alias is removed from the registry"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 11)

        registry.delete(alias='1')

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 10)

    def test_delete_not_found(self):
        """Test whether an exception is thrown when an alias is not found"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        with self.assertRaises(NotFoundError):
            _ = [t for t in registry.delete(alias='x')]

    def test_add_alias(self):
        """Test whether an alias is added to the registry"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 11)

        new_alias = '12'
        new_obj = KibanaObjMeta.create_from_obj(DASHBOARD_OBJ)
        registry.add(new_obj)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 12)

        alias, meta = registry.find(new_alias)

        self.assertEqual(meta.id, DASHBOARD_OBJ['id'])
        self.assertEqual(meta.title, DASHBOARD_OBJ['attributes']['title'])
        self.assertEqual(meta.type, DASHBOARD_OBJ['type'])
        self.assertEqual(meta.updated_at, DASHBOARD_OBJ['updated_at'])
        self.assertEqual(meta.version, DASHBOARD_OBJ['version'])

    def test_add_alias_duplicated(self):
        """Test whether an exception is thrown when the same object already exists in the registry"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        registry = Registry(self.tmp_path)

        new_obj = KibanaObjMeta.create_from_obj(VISUALIZATION_OBJ_DUPLICATED)
        with self.assertRaises(RegistryError):
            registry.add(new_obj)

    def test_add_alias_force(self):
        """Test whether an object is overwritten if it already exists in the registry and the param force is on"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 2)

        new_obj = KibanaObjMeta.create_from_obj(VISUALIZATION_OBJ_DUPLICATED)
        registry.add(new_obj, force=True)

        tuples = [t for t in registry.find_all()]
        self.assertEqual(len(tuples), 2)

    def test_update(self):
        """Test whether the name of an alias is updated"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        registry = Registry(self.tmp_path)

        tuples = [t for t in registry.find_all()]
        tuples.sort()

        alias = tuples[0][0]
        self.assertEqual(alias, '1')
        alias = tuples[1][0]
        self.assertEqual(alias, '2')

        registry.update('1', 'x')

        tuples = [t for t in registry.find_all()]

        tuples.sort()
        alias = tuples[0][0]
        self.assertEqual(alias, '2')
        alias = tuples[1][0]
        self.assertEqual(alias, 'x')

    def test_update_not_found(self):
        """Test whether an exception is thrown when an alias is not found"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        registry = Registry(self.tmp_path)

        with self.assertRaises(NotFoundError):
            _ = [t for t in registry.update('3', '4')]

    def test_update_new_alias_in_use(self):
        """Test whether an exception is thrown when the new alias is already used"""

        path = os.path.join(self.tmp_path, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        registry = Registry(self.tmp_path)

        with self.assertRaises(RegistryError):
            _ = [t for t in registry.update('1', '2')]


if __name__ == "__main__":
    unittest.main(warnings='ignore')
