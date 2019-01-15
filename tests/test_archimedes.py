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

import os
import shutil
import subprocess
import tempfile
import unittest

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.archimedes import (logger,
                                   Archimedes)
from archimedes.errors import (ExportError,
                               ImportError,
                               NotFoundError)
from archimedes.kibana import Kibana
from archimedes.manager import Manager

KIBANA_URL = 'http://kibana.biterg.io/'

DASHBOARD_ID = 'Maniphest-Backlog'
DASHBOARD_TITLE = 'Maniphest Backlog'

SEARCH_ID = "Maniphest-Search:_status:Open"
SEARCH_TITLE = "Maniphest Search:_status:Open"

INDEX_PATTERN_ID_TITLE = 'maniphest'
VISUALIZATION_ID_TITLE = 'maniphest_openissues_statistics'


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

    def save_obj(self, obj, force=False):
        return


class MockedManagerEmptyJSON(Manager):
    def __init__(self, folder_path):
        super().__init__(folder_path)

    def save_obj(self, obj, force=False):
        return

    @staticmethod
    def load_json(file_path):
        return {}


class MockedKibana(Kibana):
    def __init__(self, base_url):
        super().__init__(base_url)

    def import_objects(self, objects, force=False):
        return

    def export_by_id(self, obj_type, obj_id):
        return {}

    def export_by_title(self, obj_type, obj_title):
        return {}


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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initializated"""

        archimedes = Archimedes(KIBANA_URL, self.tmp_full)

        self.assertIsNotNone(archimedes.manager)
        self.assertIsNotNone(archimedes.kibana)

    def test_import_from_disk_by_title(self):
        """Test whether the method to import Kibana objects by title properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        # dashboard
        target_obj_title = DASHBOARD_TITLE

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_title=target_obj_title)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json')

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_title=target_obj_title, find=True)

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

        # visualization
        target_obj_title = VISUALIZATION_ID_TITLE

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_title=target_obj_title)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(VISUALIZATION, obj_title=target_obj_title, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 3 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/visualizations/visualization_maniphest_openissues_statistics.json')

        # search
        target_obj_title = SEARCH_TITLE

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_title=target_obj_title)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.import_from_disk(SEARCH, obj_title=target_obj_title, find=True)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 2 objects')
            self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/index-patterns/index-pattern_maniphest.json')
            self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                             '/searches/search_Maniphest-Search:_status:Open.json')

    def test_import_from_disk_by_id(self):
            """Test whether the method to import Kibana objects by id properly works"""

            archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

            # dashboard
            target_obj_id = DASHBOARD_ID

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(DASHBOARD, obj_id=target_obj_id)

                self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
                self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
                self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/dashboard_Maniphest-Backlog.json')

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(DASHBOARD, obj_id=target_obj_id, find=True)

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

            # visualization
            target_obj_id = VISUALIZATION_ID_TITLE

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(VISUALIZATION, obj_id=target_obj_id)

                self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
                self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
                self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/visualizations/visualization_maniphest_openissues_statistics.json')

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(VISUALIZATION, obj_id=target_obj_id, find=True)

                self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Importing 3 objects')
                self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/searches/search_Maniphest-Search:_status:Open.json')
                self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/index-patterns/index-pattern_maniphest.json')
                self.assertEqual(cm.output[3], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/visualizations/visualization_maniphest_openissues_statistics.json')

            # search
            target_obj_id = SEARCH_ID

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(SEARCH, obj_id=target_obj_id)

                self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Do not find related files')
                self.assertEqual(cm.output[1], 'INFO:archimedes.archimedes:Importing 1 objects')
                self.assertEqual(cm.output[2], 'INFO:archimedes.archimedes:Importing ' + archimedes.manager.root_path +
                                 '/searches/search_Maniphest-Search:_status:Open.json')

            with self.assertLogs(logger, level='INFO') as cm:
                archimedes.import_from_disk(SEARCH, obj_id=target_obj_id, find=True)

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
            """Test whether the method to import Kibana objects raises an error when the id and title is not provided"""

            archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
            with self.assertRaises(ImportError):
                archimedes.import_from_disk(INDEX_PATTERN, obj_id=INDEX_PATTERN_ID_TITLE, find=True)

    def test_import_from_disk_not_found(self):
            """Test whether the method to import Kibana objects raises an error when the id and title is not provided"""

            archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
            target_obj_title = DASHBOARD_ID

            with self.assertRaises(NotFoundError):
                archimedes.import_from_disk(DASHBOARD, obj_title=target_obj_title)

    def test_import_empty_json(self):
        """Test whether a warning message is logged when the file to import is empty"""

        archimedes = MockedArchimedesEmpty(KIBANA_URL, self.tmp_full)
        target_obj_id = DASHBOARD_ID

        with self.assertLogs(logger, level='WARNING') as cm:
            archimedes.import_from_disk(DASHBOARD, obj_id=target_obj_id)

            self.assertEqual(cm.output[0], 'WARNING:archimedes.archimedes:File ' + archimedes.manager.root_path +
                             '/dashboard_Maniphest-Backlog.json is empty')

    def test_export_to_disk_by_id(self):
        """Test whether the method to export Kibana objects by id properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.export_to_disk(DASHBOARD, obj_id=DASHBOARD_ID)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Exporting objects')

    def test_export_to_disk_by_title(self):
        """Test whether the method to export Kibana objects by title properly works"""

        archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)

        with self.assertLogs(logger, level='INFO') as cm:
            archimedes.export_to_disk(DASHBOARD, obj_title=DASHBOARD_TITLE)

            self.assertEqual(cm.output[0], 'INFO:archimedes.archimedes:Exporting objects')

    def test_export_from_disk_no_id_no_title(self):
            """Test whether the method to export Kibana objects raises an error when the id and title is not provided"""

            archimedes = MockedArchimedes(KIBANA_URL, self.tmp_full)
            with self.assertRaises(ExportError):
                archimedes.export_to_disk(VISUALIZATION)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
