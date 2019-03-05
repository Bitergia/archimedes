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

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.errors import (NotFoundError,
                               ObjectTypeError)
from archimedes.manager import (logger,
                                Manager,
                                VISUALIZATIONS_FOLDER,
                                SEARCHES_FOLDER,
                                INDEX_PATTERNS_FOLDER,
                                JSON_EXT)


EXPECTED_DASHBOARD = 'dashboard_Maniphest-Backlog.json'

EXPECTED_VISUALIZATIONS = [
    'visualization_maniphest_openissues_statistics.json',
    'visualization_maniphest_openissues_per_project.json',
    'visualization_maniphest_openissues_backlog.json',
    'visualization_maniphest_backlog.json',
    'visualization_maniphest_openissues_backlog_accumulated_time.json',
    'visualization_maniphest_openissues_submitters.json',
    'visualization_maniphest_openissues_assignee_orgs.json',
    'visualization_maniphest_openissues_per_organization.json'

]

EXPECTED_SEARCH = 'search_Maniphest-Search:_status:Open.json'
EXPECTED_INDEX_PATTERN = 'index-pattern_maniphest.json'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestManager(unittest.TestCase):
    """Manager tests"""

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

        manager = Manager(self.tmp_full)

        self.assertEqual(manager.root_path, self.tmp_full)
        self.assertEqual(manager.visualizations_folder, os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER))
        self.assertEqual(manager.searches_folder, os.path.join(self.tmp_full, SEARCHES_FOLDER))
        self.assertEqual(manager.index_patterns_folder, os.path.join(self.tmp_full, INDEX_PATTERNS_FOLDER))

    def test_find_dashboard_files(self):
        """Test whether the files containing the objects referenced in the dashboard are retrieved"""

        manager = Manager(self.tmp_full)

        dashboard_file_path = os.path.join(self.tmp_full, EXPECTED_DASHBOARD)
        dashboard_files = manager.find_dashboard_files(dashboard_file_path)

        self.assertEqual(len(dashboard_files), 11)
        self.assertIn(dashboard_file_path, dashboard_files)

        index_pattern_file_path = os.path.join(self.tmp_full, INDEX_PATTERNS_FOLDER, EXPECTED_INDEX_PATTERN)
        self.assertIn(index_pattern_file_path, dashboard_files)

        search_file_path = os.path.join(self.tmp_full, SEARCHES_FOLDER, EXPECTED_SEARCH)
        self.assertIn(search_file_path, dashboard_files)

        for visualization_file_name in EXPECTED_VISUALIZATIONS:
            visualization_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER, visualization_file_name)
            self.assertIn(visualization_path, dashboard_files)

    def test_find_dashboard_files_no_viz(self):
        """Test whether only the dashboard file is returned when the visualization folder does not exit"""

        manager = Manager(self.tmp_only_dash)

        dashboard_file_path = os.path.join(self.tmp_only_dash, EXPECTED_DASHBOARD)

        with self.assertLogs(logger, level='INFO') as cm:
            dashboard_files = manager.find_dashboard_files(dashboard_file_path)
            self.assertEqual(len(dashboard_files), 1)
            self.assertIn(dashboard_file_path, dashboard_files)

            self.assertEqual(cm.output[0], "INFO:archimedes.manager:Visualizations not loaded "
                                           "for " + dashboard_file_path + ", visualizations folder doesn't exist")

    def test_find_visualization_files(self):
        """Test whether the files containing the objects referenced in the visualization are retrieved"""

        manager = Manager(self.tmp_full)

        visualization_file_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER, EXPECTED_VISUALIZATIONS[0])
        visualization_files = manager.find_visualization_files(visualization_file_path)

        self.assertEqual(len(visualization_files), 3)

        self.assertIn(visualization_file_path, visualization_files)
        index_pattern_file_path = os.path.join(self.tmp_full, INDEX_PATTERNS_FOLDER, EXPECTED_INDEX_PATTERN)
        self.assertIn(index_pattern_file_path, visualization_files)

        search_file_path = os.path.join(self.tmp_full, SEARCHES_FOLDER, EXPECTED_SEARCH)
        self.assertIn(search_file_path, visualization_files)

    def test_find_visualization_only_files(self):
        """Test whether only the dashboard and visualizations are returned when the other folders don't exist"""

        manager = Manager(self.tmp_only_viz)

        visualization_file_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER, EXPECTED_VISUALIZATIONS[0])

        with self.assertLogs(logger, level='INFO') as cm:
            visualization_files = manager.find_visualization_files(visualization_file_path)

            self.assertEqual(len(visualization_files), 1)
            self.assertIn(visualization_file_path, visualization_files)

            self.assertEqual(cm.output[0], "INFO:archimedes.manager:Searches won't be loaded "
                                           "for " + visualization_file_path + ", searches folder doesn't exist")
            self.assertEqual(cm.output[1], "INFO:archimedes.manager:Index patterns won't be loaded "
                                           "for " + visualization_file_path + ", index patterns folder doesn't exist")
            self.assertEqual(cm.output[2], "INFO:archimedes.manager:No index pattern declared "
                                           "for " + visualization_file_path)

    def test_find_search_files(self):
        """Test whether the files containing the objects referenced in the search are retrieved"""

        manager = Manager(self.tmp_full)

        search_file_path = os.path.join(self.tmp_full, SEARCHES_FOLDER, EXPECTED_SEARCH)
        search_files = manager.find_search_files(search_file_path)

        self.assertEqual(len(search_files), 2)
        self.assertIn(search_file_path, search_files)

        index_pattern_file_path = os.path.join(self.tmp_full, INDEX_PATTERNS_FOLDER, EXPECTED_INDEX_PATTERN)
        self.assertIn(index_pattern_file_path, search_files)

    def test_find_index_pattern(self):
        """Test whether the index pattern id is retrieved from an object"""

        visualization = read_file('data/object_visualization')
        manager = Manager(self.tmp_full)

        index_pattern = manager.find_index_pattern(json.loads(visualization))
        self.assertEqual(index_pattern, "7c2496c0-b013-11e8-8771-a349686d998a")

    def test_build_folder_path(self):
        """Test whether the folder path is properly built"""

        manager = Manager(self.tmp_full)

        expected = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER)
        self.assertEqual(manager.build_folder_path(VISUALIZATION), expected)

        expected = os.path.join(self.tmp_full, SEARCHES_FOLDER)
        self.assertEqual(manager.build_folder_path(SEARCH), expected)

        expected = os.path.join(self.tmp_full, INDEX_PATTERNS_FOLDER)
        self.assertEqual(manager.build_folder_path(INDEX_PATTERN), expected)

        expected = os.path.join(self.tmp_full, '')
        self.assertEqual(manager.build_folder_path(DASHBOARD), expected)

        with self.assertRaises(ObjectTypeError):
            _ = manager.build_folder_path("xxx")

    def test_save_obj(self):
        """Test whether the object is correctly saved"""

        obj = read_file('data/object_visualization')
        obj_content = json.loads(obj)
        manager = Manager(self.tmp_full)

        dest_name = obj_content['type'] + '_' + obj_content['id'] + JSON_EXT
        dest_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER, dest_name)

        self.assertFalse(os.path.exists(dest_path))

        with self.assertLogs(logger, level='INFO') as cm:
            manager.save_obj(obj_content)
            self.assertEqual(cm.output[0], "INFO:archimedes.manager:Object saved at " + dest_path)
            self.assertTrue(os.path.exists(dest_path))

        with self.assertLogs(logger, level='INFO') as cm:
            manager.save_obj(obj_content)
            self.assertEqual(cm.output[0], "WARNING:archimedes.manager:Object already "
                                           "exists at " + dest_path + ", it won't be overwritten")

        with self.assertLogs(logger, level='INFO') as cm:
            manager.save_obj(obj_content, force=True)
            self.assertEqual(cm.output[0], "INFO:archimedes.manager:Object saved at " + dest_path)

    def test_find_file_by_content_title(self):
        """Test whether a file is found by its content title"""

        manager = Manager(self.tmp_full)
        folder_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER)

        target_content_title = "maniphest_backlog"
        target_file_name = "visualization_maniphest_backlog.json"

        found = manager.find_file_by_content_title(folder_path, target_content_title)
        self.assertEqual(found, os.path.join(folder_path, target_file_name))

        target_content_title = "not_found"

        with self.assertRaises(NotFoundError):
            _ = manager.find_file_by_content_title(folder_path, target_content_title)

        folder_path = "wrong_path"
        with self.assertRaises(NotFoundError):
            _ = manager.find_file_by_content_title(folder_path, target_content_title)

    def test_find_file_by_name(self):
        """Test whether a file is found by its name"""

        manager = Manager(self.tmp_full)
        folder_path = os.path.join(self.tmp_full, VISUALIZATIONS_FOLDER)

        target_file_name = "visualization_maniphest_backlog.json"

        found = manager.find_file_by_name(folder_path, target_file_name)
        self.assertEqual(found, os.path.join(folder_path, target_file_name))

        target_file_name = "not_found"

        with self.assertRaises(NotFoundError):
            _ = manager.find_file_by_name(folder_path, target_file_name)

        folder_path = "wrong_path"
        with self.assertRaises(NotFoundError):
            _ = manager.find_file_by_name(folder_path, target_file_name)

    def test_build_file_name(self):
        """Test whether the file name is properly built"""

        manager = Manager(self.tmp_repo_path)

        expected = INDEX_PATTERN + '_' + "ip.json"
        self.assertEqual(manager.build_file_name(INDEX_PATTERN, "ip"), expected)

    def test_folder_exists(self):
        """Test whether the method `folder_exists` properly works"""

        manager = Manager(self.tmp_full)

        self.assertTrue(manager.folder_exists(manager.visualizations_folder))
        self.assertFalse(manager.folder_exists('xxx'))

    def test_get_files(self):
        """Test whether files are correctly returned"""

        manager = Manager(self.tmp_full)

        expected = [EXPECTED_INDEX_PATTERN]
        self.assertListEqual(manager.get_files(manager.index_patterns_folder), expected)

        expected = [EXPECTED_SEARCH]
        self.assertListEqual(manager.get_files(manager.searches_folder), expected)

        expected = EXPECTED_VISUALIZATIONS
        expected.sort()

        actual = manager.get_files(manager.visualizations_folder)
        actual.sort()
        self.assertListEqual(actual, expected)

    def test_find_all(self):
        """Test whether all objects are found on disk"""

        manager = Manager(self.tmp_full)
        objs = [t[1] for t in manager.find_all()]

        self.assertEqual(len(objs), 11)

        dashboards = [obj for obj in objs if obj['type'] == DASHBOARD]
        self.assertEqual(len(dashboards), 1)

        visualizations = [obj for obj in objs if obj['type'] == VISUALIZATION]
        self.assertEqual(len(visualizations), 8)

        index_patterns = [obj for obj in objs if obj['type'] == INDEX_PATTERN]
        self.assertEqual(len(index_patterns), 1)

        searches = [obj for obj in objs if obj['type'] == SEARCH]
        self.assertEqual(len(searches), 1)

    def test_find_all_empty(self):
        """Test whether no objects are found when the archimedes folder is empty"""

        os.mkdir(self.tmp_empty)

        manager = Manager(self.tmp_empty)
        objs = [f for f in manager.find_all()]

        self.assertEqual(len(objs), 0)

        shutil.rmtree(self.tmp_empty)

    def test_find_all_empty_other_files(self):
        """Test whether no objects are found when the archimedes folder includes files not
        being dashboards, visualizations, searches or index patterns
        """
        os.mkdir(self.tmp_empty)

        registry_path = os.path.join(self.tmp_empty, '.registry')
        open(registry_path, 'w+').close()

        self.assertTrue(os.path.exists(registry_path))

        manager = Manager(self.tmp_empty)
        objs = [f for f in manager.find_all()]

        self.assertEqual(len(objs), 0)

        shutil.rmtree(self.tmp_empty)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
