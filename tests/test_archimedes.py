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
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.manager import (INDEX_PATTERNS_FOLDER,
                                VISUALIZATIONS_FOLDER)
from archimedes.archimedes import (logger,
                                   Archimedes)
from archimedes.errors import (ExportError,
                               ImportError,
                               NotFoundError,
                               ObjectTypeError,
                               RegistryError)
from archimedes.kibana import Kibana
from archimedes.manager import Manager
from archimedes.registry import REGISTRY_NAME

KIBANA_URL = 'http://example.com/'

DASHBOARD_ID = 'Maniphest-Backlog'
DASHBOARD_TITLE = 'Maniphest Backlog'
DASHBOARD_ALIAS = '11'

SEARCH_ID = "Maniphest-Search:_status:Open"
SEARCH_TITLE = "Maniphest Search:_status:Open"
SEARCH_ALIAS = '10'

INDEX_PATTERN_ID_TITLE = 'maniphest'
VISUALIZATION_ID_TITLE = 'maniphest_openissues_statistics'
VISUALIZATION_ALIAS = '6'

INDEX_PATTERN_ID_EXPORT = '7c2496c0-b013-11e8-8771-a349686d998a'
INDEX_PATTERN_ALIAS_EXPORT = '2'
VISUALIZATION_ID_EXPORT = '0b84fff0-b1b6-11e8-8aac-ef7fd4d8cbad'
VISUALIZATION_TITLE_EXPORT = 'gitlab-issues_submitters_by_organization'
VISUALIZATION_ALIAS_EXPORT = '1'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


def copy_content(filename, target_path):
    content = read_file(filename)

    with open(target_path, 'w') as f:
        f.write(content)


class MockedArchimedes(Archimedes):
    def __init__(self, url, root_path):
        super().__init__(url, root_path)

        self.kibana = MockedKibana(url)
        self.manager = MockedManager(root_path)


class MockedArchimedesEmpty(Archimedes):
    def __init__(self, url, root_path):
        super().__init__(url, root_path)

        self.kibana = MockedKibana(url)
        self.manager = MockedManagerEmptyJSON(root_path)


class MockedManager(Manager):
    def __init__(self, folder_path):
        super().__init__(folder_path)


class MockedManagerEmptyJSON(Manager):
    def __init__(self, folder_path):
        super().__init__(folder_path)

    def save_obj(self, obj, force=False):
        return


class MockedKibana(Kibana):
    def __init__(self, base_url):
        super().__init__(base_url)

    def import_objects(self, objects, force=False):
        return

    def export_by_id(self, obj_type, obj_id):
        obj = read_file('data/object_visualization')
        return json.loads(obj)

    def export_by_title(self, obj_type, obj_title):
        obj = read_file('data/object_visualization')
        return json.loads(obj)

    def find_by_id(self, obj_type, obj_id):
        obj = read_file('data/object_index-pattern')
        return json.loads(obj)

    def find_all(self):
        index_pattern = read_file('data/object_index-pattern')
        visualization = read_file('data/object_visualization')

        return [json.loads(index_pattern), json.loads(visualization)]


class TestArchimedes(unittest.TestCase):
    """Archimedes tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='archimedes_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'collections')

        data_path = os.path.dirname(os.path.abspath(__file__))
        tar_path = os.path.join(data_path, 'data/collections.tar.gz')
        subprocess.check_call(['tar', '-xzf', tar_path, '-C', cls.tmp_path])

        cls.tmp_full = os.path.join(cls.tmp_repo_path, 'collection-full')
        cls.tmp_only_viz = os.path.join(cls.tmp_repo_path, 'collection-viz')
        cls.tmp_only_dash = os.path.join(cls.tmp_repo_path, 'collection-dashboard')
        cls.tmp_empty = os.path.join(cls.tmp_repo_path, 'collection-empty')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initialized"""

        archimedes = Archimedes(KIBANA_URL, self.tmp_full)

        self.assertIsNotNone(archimedes.manager)
        self.assertIsNotNone(archimedes.kibana)

    def test_import_from_disk_dashboard_by_title(self):
        """Test whether the method to import Kibana dashboard by title properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_title=DASHBOARD_TITLE)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

    def test_import_from_disk_dashboard_by_title_find(self):
        """Test whether the method to import Kibana dashboard by title using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_title=DASHBOARD_TITLE, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 11 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')
            self.assertEqual(cm.output[4], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_project.json')
            self.assertEqual(cm.output[5], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog.json')
            self.assertEqual(cm.output[6], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_backlog.json')
            self.assertEqual(cm.output[7], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog_accumulated_time.json')
            self.assertEqual(cm.output[8], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_submitters.json')
            self.assertEqual(cm.output[9], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_assignee_orgs.json')
            self.assertEqual(cm.output[10], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_organization.json')
            self.assertEqual(cm.output[11], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

    def test_import_from_disk_dashboard_by_alias(self):
        """Test whether the method to import Kibana dashboard by alias properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=DASHBOARD_ALIAS)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

        os.remove(registry_path)

    def test_import_from_disk_dashboard_by_alias_find(self):
        """Test whether the method to import Kibana dashboard by alias using the find option properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=DASHBOARD_ALIAS, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 11 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')
            self.assertEqual(cm.output[4], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_project.json')
            self.assertEqual(cm.output[5], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog.json')
            self.assertEqual(cm.output[6], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_backlog.json')
            self.assertEqual(cm.output[7], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog_accumulated_time.json')
            self.assertEqual(cm.output[8], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_submitters.json')
            self.assertEqual(cm.output[9], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_assignee_orgs.json')
            self.assertEqual(cm.output[10], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_organization.json')
            self.assertEqual(cm.output[11], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

        os.remove(registry_path)

    def test_import_from_disk_visualization_by_title(self):
        """Test whether the method to import Kibana visualization by title properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_title=VISUALIZATION_ID_TITLE)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

    def test_import_from_disk_visualization_by_title_find(self):
        """Test whether the method to import Kibana visualization by title using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_title=VISUALIZATION_ID_TITLE, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 3 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

    def test_import_from_disk_visualization_by_alias(self):
        """Test whether the method to import Kibana visualization by alias properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=VISUALIZATION_ALIAS)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

        os.remove(registry_path)

    def test_import_from_disk_visualization_by_alias_find(self):
        """Test whether the method to import Kibana visualization by alias using the find option properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=VISUALIZATION_ALIAS, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 3 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

        os.remove(registry_path)

    def test_import_from_disk_search_by_title(self):
        """Test whether the method to import Kibana search by title properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_title=SEARCH_TITLE)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

    def test_import_from_disk_search_by_title_find(self):
        """Test whether the method to import Kibana search by title using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_title=SEARCH_TITLE, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 2 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

    def test_import_from_disk_search_by_alias(self):
        """Test whether the method to import Kibana search by alias properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=SEARCH_ALIAS)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

        os.remove(registry_path)

    def test_import_from_disk_search_by_alias_find(self):
        """Test whether the method to import Kibana search by alias using the find option properly works"""

        registry_path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', registry_path)
        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(obj_alias=SEARCH_ALIAS, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 2 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

        os.remove(registry_path)

    def test_import_from_disk_dashboard_by_id(self):
        """Test whether the method to import Kibana dashboard by id properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_id=DASHBOARD_ID)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

    def test_import_from_disk_dashboard_by_id_find(self):
        """Test whether the method to import Kibana dashboard by id using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_id=DASHBOARD_ID, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 11 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')
            self.assertEqual(cm.output[4], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_project.json')
            self.assertEqual(cm.output[5], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog.json')
            self.assertEqual(cm.output[6], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_backlog.json')
            self.assertEqual(cm.output[7], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_backlog_accumulated_time.json')
            self.assertEqual(cm.output[8], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_submitters.json')
            self.assertEqual(cm.output[9], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_assignee_orgs.json')
            self.assertEqual(cm.output[10], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_per_organization.json')
            self.assertEqual(cm.output[11], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

    def test_import_from_disk_visualization_by_id(self):
        """Test whether the method to import Kibana visualization by id properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_id=VISUALIZATION_ID_TITLE)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

    def test_import_from_disk_visualization_by_id_find(self):
        """Test whether the method to import Kibana visualization by id using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_id=VISUALIZATION_ID_TITLE, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 3 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

    def test_import_from_disk_search_by_id(self):
        """Test whether the method to import Kibana search by id properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_id=SEARCH_ID)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

    def test_import_from_disk_search_by_id_find(self):
        """Test whether the method to import Kibana search by id using the find option properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_id=SEARCH_ID, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 2 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

    def test_import_from_disk_no_id_no_title(self):
        """Test whether the method to import Kibana objects raises an error when the id and title is not provided"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        with self.assertRaises(ImportError):
            archimedes.import_from_disk(VISUALIZATION)

    def test_import_from_disk_find_index_pattern(self):
        """Test whether an error is thrown when importing an index pattern with the flag `find` enabled"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        with self.assertRaises(ImportError):
            archimedes.import_from_disk(INDEX_PATTERN, obj_id=INDEX_PATTERN_ID_TITLE, find=True)

    def test_import_from_disk_not_found(self):
        """Test whether the method to import Kibana objects raises an error when the object is not found on disk"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        target_obj_title = DASHBOARD_ID

        with self.assertRaises(NotFoundError):
            archimedes.import_from_disk(DASHBOARD, obj_title=target_obj_title)

    @unittest.mock.patch('archimedes.archimedes.load_json')
    def test_import_empty_json(self, mock_load_json):
        """Test whether a warning message is logged when the file to import is empty"""

        mock_load_json.return_value = {}

        archimedes = MockedArchimedesEmpty(KIBANA_URL, self.tmp_full)
        target_obj_id = DASHBOARD_ID

        with self.assertLogs(logger, level='WARNING') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_id=target_obj_id)

            self.assertEqual(cm.output[0], 'WARNING:archimedes.archimedes:File ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json is empty')

    def test_export_to_disk_by_id(self):
        """Test whether the method to export a Kibana object by id properly works"""

        os.mkdir(self.tmp_empty)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)
        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        archimedes.export_to_disk(VISUALIZATION, obj_id=VISUALIZATION_ID_EXPORT)
        self.assertTrue(os.path.exists(obj_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_to_disk_by_alias(self):
        """Test whether the method to export a Kibana object by alias properly works"""

        os.mkdir(self.tmp_empty)
        path = os.path.join(self.tmp_empty, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)

        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        archimedes.export_to_disk(obj_alias=VISUALIZATION_ALIAS_EXPORT)
        self.assertTrue(os.path.exists(obj_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_to_disk_by_id_ip(self):
        """Test whether the method to export a Kibana object by id and its index pattern properly works"""

        os.mkdir(self.tmp_empty)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)
        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')
        ip_path = os.path.join(self.tmp_empty, INDEX_PATTERNS_FOLDER,
                               INDEX_PATTERN + '_' + INDEX_PATTERN_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        self.assertFalse(os.path.exists(ip_path))

        archimedes.export_to_disk(VISUALIZATION, obj_id=VISUALIZATION_ID_EXPORT, index_pattern=True)

        self.assertTrue(os.path.exists(obj_path))
        self.assertTrue(os.path.exists(ip_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_to_disk_by_alias_ip(self):
        """Test whether the method to export a Kibana object by alias and its index pattern properly works"""

        os.mkdir(self.tmp_empty)
        path = os.path.join(self.tmp_empty, REGISTRY_NAME)
        copy_content('data/registry_slim', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)

        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')
        ip_path = os.path.join(self.tmp_empty, INDEX_PATTERNS_FOLDER,
                               INDEX_PATTERN + '_' + INDEX_PATTERN_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        self.assertFalse(os.path.exists(ip_path))

        archimedes.export_to_disk(VISUALIZATION, obj_alias=VISUALIZATION_ALIAS_EXPORT, index_pattern=True)

        self.assertTrue(os.path.exists(obj_path))
        self.assertTrue(os.path.exists(ip_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_to_disk_by_title(self):
        """Test whether the method to export a Kibana object by title properly works"""

        os.mkdir(self.tmp_empty)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)
        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        archimedes.export_to_disk(VISUALIZATION, obj_title=VISUALIZATION_TITLE_EXPORT)
        self.assertTrue(os.path.exists(obj_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_to_disk_by_title_ip(self):
        """Test whether the method to export a Kibana object by title and its index pattern properly works"""

        os.mkdir(self.tmp_empty)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_empty)
        obj_path = os.path.join(self.tmp_empty, VISUALIZATIONS_FOLDER,
                                VISUALIZATION + '_' + VISUALIZATION_ID_EXPORT + '.json')
        ip_path = os.path.join(self.tmp_empty, INDEX_PATTERNS_FOLDER,
                               INDEX_PATTERN + '_' + INDEX_PATTERN_ID_EXPORT + '.json')

        self.assertFalse(os.path.exists(obj_path))
        self.assertFalse(os.path.exists(ip_path))

        archimedes.export_to_disk(VISUALIZATION, obj_title=VISUALIZATION_TITLE_EXPORT, index_pattern=True)

        self.assertTrue(os.path.exists(obj_path))
        self.assertTrue(os.path.exists(ip_path))

        shutil.rmtree(self.tmp_empty)

    def test_export_from_disk_no_id_no_title(self):
        """Test whether the method to export Kibana objects raises an error when the id and title is not provided"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        with self.assertRaises(ExportError):
            archimedes.export_to_disk(VISUALIZATION)

    def test_export_from_disk_alias_not_found(self):
        """Test whether the method to export Kibana objects raises an error when the alias is not found"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        target_obj_alias = DASHBOARD_ALIAS

        with self.assertRaises(NotFoundError):
            archimedes.export_to_disk(obj_alias=target_obj_alias)

    def test_inspect_method(self):
        """Test whether the method inspect properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        objs = [obj for obj in archimedes.inspect()]

        self.assertEqual(objs, [])

    def test_inspect_method_remote(self):
        """Test whether the method to inspect the content Kibana properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        objs = [obj for obj in archimedes.inspect(remote=True)]

        self.assertEqual(len(objs), 2)

        # check that the .registry file is not included
        copy_content('data/registry_full', archimedes.registry.path)

        objs = [obj for obj in archimedes.inspect(remote=True)]
        self.assertEqual(len(objs), 2)

    def test_inspect_method_local(self):
        """Test whether the method to inspect the content of the Archimedes folder properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
        objs = [obj for obj in archimedes.inspect(local=True)]

        self.assertEqual(len(objs), 11)

    def test_populate_registry(self):
        """Test whether the method to populate the registry properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        self.assertEqual(archimedes.registry.content, {})

        archimedes.populate_registry()

        self.assertEqual(len(archimedes.registry.content), 2)

        os.remove(archimedes.registry.path)

    def test_populate_registry_duplicates(self):
        """Test whether an exception is thrown when populating the registry with an alias that already exists"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        archimedes.populate_registry()

        self.assertEqual(len(archimedes.registry.content), 2)

        with self.assertRaises(RegistryError):
            archimedes.populate_registry()

        os.remove(archimedes.registry.path)

    def test_populate_registry_force(self):
        """Test whether the method to populate the registry overwrites it when the param force is enabled"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        archimedes.populate_registry()
        self.assertEqual(len(archimedes.registry.content), 2)

        archimedes.populate_registry(force=True)
        self.assertEqual(len(archimedes.registry.content), 2)

        os.remove(archimedes.registry.path)

    def test_query_registry(self):
        """Test whether the method to query the content of the registry properly works"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        tuple = archimedes.query_registry('1')
        alias, meta = tuple

        self.assertEqual(alias, '1')
        self.assertTrue(meta.id, 'maniphest')
        self.assertTrue(meta.title, 'maniphest')
        self.assertTrue(meta.type, INDEX_PATTERN)
        self.assertTrue(meta.updated_at, '2019-02-12T15:38:42.905Z')
        self.assertTrue(meta.version, 1)

        os.remove(archimedes.registry.path)

    def test_query_registry_not_found(self):
        """Test whether an exception is thrown when the alias is not found"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertRaises(NotFoundError):
            _ = archimedes.query_registry('zzz')

        os.remove(archimedes.registry.path)

    def test_list_registry(self):
        """Test whether the method to list the content of the registry properly works"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        tuples = [tuple for tuple in archimedes.list_registry()]
        tuples.sort()

        self.assertTrue(len(tuples), 11)

        alias, meta = tuples[0]

        self.assertEqual(alias, '1')
        self.assertTrue(meta.id, 'maniphest')
        self.assertTrue(meta.title, 'maniphest')
        self.assertTrue(meta.type, INDEX_PATTERN)
        self.assertTrue(meta.updated_at, '2019-02-12T15:38:42.905Z')
        self.assertTrue(meta.version, 1)

        os.remove(archimedes.registry.path)

    def test_list_registry_type(self):
        """Test whether the method returns the information of the aliases of a given type, when the latter is given"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        tuples = [tuple for tuple in archimedes.list_registry(obj_type=DASHBOARD)]
        tuples.sort()

        self.assertTrue(len(tuples), 1)

        alias, meta = tuples[0]

        self.assertEqual(alias, '11')
        self.assertTrue(meta.id, 'Maniphest-Backlog')
        self.assertTrue(meta.title, 'Maniphest Backlog')
        self.assertTrue(meta.type, DASHBOARD)
        self.assertTrue(meta.updated_at, '2019-02-12T15:38:52.132Z')
        self.assertTrue(meta.version, 1)

        os.remove(archimedes.registry.path)

    def test_list_registry_wrong_type(self):
        """Test whether an exception is thrown when the obj type is not known"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertRaises(ObjectTypeError):
            _ = [tuple for tuple in archimedes.list_registry(obj_type='unknown')]

        os.remove(archimedes.registry.path)

    def test_clear_registry(self):
        """Test whether the registry is cleared when no alias is given"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        self.assertEqual(len(archimedes.registry.content), 11)

        archimedes.clear_registry()

        self.assertEqual(len(archimedes.registry.content), 0)

        os.remove(archimedes.registry.path)

    def test_delete_alias(self):
        """Test whether an alias is deleted from the registry"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        self.assertEqual(len(archimedes.registry.content), 11)

        archimedes.delete_registry(alias='1')

        self.assertEqual(len(archimedes.registry.content), 10)
        self.assertNotIn('1', archimedes.registry.content)

        os.remove(archimedes.registry.path)

    def test_delete_no_alias_found(self):
        """Test whether an exception is thrown when the target alias is not found in the registry"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertRaises(NotFoundError):
            archimedes.delete_registry(alias='x')

        os.remove(archimedes.registry.path)

    def test_update_registry(self):
        """Test whether the method to update the registry properly works"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        self.assertIn('1', archimedes.registry.content)
        self.assertNotIn('x', archimedes.registry.content)

        archimedes.update_registry('1', 'x')

        self.assertNotIn('1', archimedes.registry.content)
        self.assertIn('x', archimedes.registry.content)

        os.remove(archimedes.registry.path)

    def test_update_registry_old_alias_not_found(self):
        """Test whether an exception is thrown when the old alias is not found in the registry"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertRaises(NotFoundError):
            archimedes.update_registry(alias='x', new_alias='1')

        os.remove(archimedes.registry.path)

    def test_update_registry_new_alias_already_in_use(self):
        """Test whether an exception is thrown when the new alias is already used in the registry"""

        path = os.path.join(self.tmp_full, REGISTRY_NAME)
        copy_content('data/registry_full', path)

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertRaises(RegistryError):
            archimedes.update_registry(alias='1', new_alias='2')

        os.remove(archimedes.registry.path)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
