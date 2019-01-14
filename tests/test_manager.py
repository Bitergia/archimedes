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
from archimedes.errors import ObjectTypeError
from archimedes.manager import (Manager,
                                VISUALIZATIONS_FOLDER,
                                SEARCHES_FOLDER,
                                INDEX_PATTERNS_FOLDER)


DASHBOARD_1_FILE_NAME = 'dashboard_Maniphest.json'
DASHBOARD_2_FILE_NAME = 'dashboard_Maniphest-Backlog.json'
DASHBOARD_3_FILE_NAME = 'dashboard_Maniphest-Timing.json'

VISUALIZATIONS_DASHBOARD_1 = [
    'visualization_maniphest_main_numbers.json',
    'visualization_maniphest_submitters.json',
    'visualization_maniphest_issues.json',
    'visualization_maniphest_issues_organizations_assignee.json',
    'visualization_maniphest_openissues_projects.json',
    'visualization_maniphest_issues_submitters.json',
    'visualization_maniphest_assigned_issues_orgs.json',
    'visualization_maniphest_issues_organizations.json'
]

VISUALIZATIONS_DASHBOARD_2 = [
    'visualization_maniphest_openissues_statistics.json',
    'visualization_maniphest_openissues_per_project.json',
    'visualization_maniphest_openissues_backlog.json',
    'visualization_maniphest_backlog.json',
    'visualization_maniphest_openissues_backlog_accumulated_time.json',
    'visualization_maniphest_openissues_submitters.json',
    'visualization_maniphest_openissues_assignee_orgs.json',
    'visualization_maniphest_openissues_per_organization.json'
]

VISUALIZATIONS_DASHBOARD_3 = [
    'visualization_maniphest_issues_submitters.json',
    'visualization_maniphest_main_numbers_timing.json',
    'visualization_maniphest_issues_status.json',
    'visualization_maniphest_issues_assigned_organizations.json',
    'visualization_maniphest_openissues_projects.json',
    'visualization_maniphest_issues_open_in_median.json',
    'visualization_maniphest_issues_open_in_median_80_percentile.json',
    'visualization_maniphest_openissues_per_organization.json',
    'visualization_maniphest_submitters.json',
    'visualization_maniphest_issues_evolutionary.json',
    'visualization_17545120-752d-11e8-a4e7-6b1c6a13c58d.json',
    'visualization_f5f83530-752e-11e8-a4e7-6b1c6a13c58d.json'
]


SEARCH_DASHBOARD = 'search_Maniphest-Search:_status:Open.json'
INDEX_PATTERN_DASHBOARD = 'index-pattern_maniphest.json'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestManager(unittest.TestCase):
    """Manager tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='archimedes_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'collection')

        data_path = os.path.dirname(os.path.abspath(__file__))
        tar_path = os.path.join(data_path, 'data/collection.tar.gz')
        subprocess.check_call(['tar', '-xzf', tar_path, '-C', cls.tmp_path])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initializated"""

        manager = Manager(self.tmp_repo_path)

        self.assertEqual(manager.root_path, self.tmp_repo_path)
        self.assertEqual(manager.visualizations_folder, os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER))
        self.assertEqual(manager.searches_folder, os.path.join(self.tmp_repo_path, SEARCHES_FOLDER))
        self.assertEqual(manager.index_patterns_folder, os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER))

    def test_find_dashboard_files(self):
        """Test whether the files containing the objects referenced in the dashboard are retrieved"""

        manager = Manager(self.tmp_repo_path)

        # first dashboard
        dashboard_file_path = os.path.join(self.tmp_repo_path, DASHBOARD_1_FILE_NAME)
        dashboard_files = manager.find_dashboard_files(dashboard_file_path)

        self.assertEqual(len(dashboard_files), 10)
        self.assertIn(dashboard_file_path, dashboard_files)

        index_pattern_file_path = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER, INDEX_PATTERN_DASHBOARD)
        self.assertIn(index_pattern_file_path, dashboard_files)

        search_file_path = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER, SEARCH_DASHBOARD)
        self.assertNotIn(search_file_path, dashboard_files)

        for visualization_file_name in VISUALIZATIONS_DASHBOARD_1:
            visualization_path = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER, visualization_file_name)
            self.assertIn(visualization_path, dashboard_files)

        # second dashboard
        dashboard_file_path = os.path.join(self.tmp_repo_path, DASHBOARD_2_FILE_NAME)
        dashboard_files = manager.find_dashboard_files(dashboard_file_path)

        self.assertEqual(len(dashboard_files), 10)
        self.assertIn(dashboard_file_path, dashboard_files)

        index_pattern_file_path = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER, INDEX_PATTERN_DASHBOARD)
        self.assertNotIn(index_pattern_file_path, dashboard_files)

        search_file_path = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER, SEARCH_DASHBOARD)
        self.assertIn(search_file_path, dashboard_files)

        for visualization_file_name in VISUALIZATIONS_DASHBOARD_2:
            visualization_path = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER, visualization_file_name)
            self.assertIn(visualization_path, dashboard_files)

        # third dashboard
        dashboard_file_path = os.path.join(self.tmp_repo_path, DASHBOARD_3_FILE_NAME)
        dashboard_files = manager.find_dashboard_files(dashboard_file_path)

        self.assertEqual(len(dashboard_files), 15)
        self.assertIn(dashboard_file_path, dashboard_files)

        index_pattern_file_path = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER, INDEX_PATTERN_DASHBOARD)
        self.assertIn(index_pattern_file_path, dashboard_files)

        search_file_path = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER, SEARCH_DASHBOARD)
        self.assertIn(search_file_path, dashboard_files)

        for visualization_file_name in VISUALIZATIONS_DASHBOARD_3:
            visualization_path = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER, visualization_file_name)
            self.assertIn(visualization_path, dashboard_files)

    def test_find_visualization_files(self):
        """Test whether the files containing the objects referenced in the visualization are retrieved"""

        manager = Manager(self.tmp_repo_path)

        # first visualization
        visualization_file_name = VISUALIZATIONS_DASHBOARD_1[0]
        visualization_file_path = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER, visualization_file_name)
        visualization_files = manager.find_visualization_files(visualization_file_path)

        self.assertEqual(len(visualization_files), 2)
        self.assertIn(visualization_file_path, visualization_files)

        index_pattern_file_path = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER, INDEX_PATTERN_DASHBOARD)
        self.assertIn(index_pattern_file_path, visualization_files)

        # second visualization
        visualization_file_name = VISUALIZATIONS_DASHBOARD_2[0]
        visualization_file_path = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER, visualization_file_name)
        visualization_files = manager.find_visualization_files(visualization_file_path)

        self.assertEqual(len(visualization_files), 2)
        self.assertIn(visualization_file_path, visualization_files)

        search_file_path = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER, SEARCH_DASHBOARD)
        self.assertIn(search_file_path, visualization_files)

    def test_find_search_files(self):
        """Test whether the files containing the objects referenced in the search are retrieved"""

        manager = Manager(self.tmp_repo_path)

        search_file_path = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER, SEARCH_DASHBOARD)
        search_files = manager.find_search_files(search_file_path)

        self.assertEqual(len(search_files), 2)
        self.assertIn(search_file_path, search_files)

        index_pattern_file_path = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER, INDEX_PATTERN_DASHBOARD)
        self.assertIn(index_pattern_file_path, search_files)

    def test_find_index_pattern(self):
        """Test whether the index pattern id is retrieved from an object"""

        visualization = read_file('data/object_visualization')
        manager = Manager(self.tmp_repo_path)

        index_pattern = manager.find_index_pattern(json.loads(visualization))
        self.assertEqual(index_pattern, "git")

    def test_build_folder_path(self):
        """Test whether the folder path is properly built"""

        manager = Manager(self.tmp_repo_path)

        expected = os.path.join(self.tmp_repo_path, VISUALIZATIONS_FOLDER)
        self.assertEqual(manager.build_folder_path(VISUALIZATION), expected)

        expected = os.path.join(self.tmp_repo_path, SEARCHES_FOLDER)
        self.assertEqual(manager.build_folder_path(SEARCH), expected)

        expected = os.path.join(self.tmp_repo_path, INDEX_PATTERNS_FOLDER)
        self.assertEqual(manager.build_folder_path(INDEX_PATTERN), expected)

        expected = os.path.join(self.tmp_repo_path, '')
        self.assertEqual(manager.build_folder_path(DASHBOARD), expected)

        with self.assertRaises(ObjectTypeError):
            _ = manager.build_folder_path("xxx")

    def test_build_file_name(self):
        """Test whether the file name is properly built"""

        manager = Manager(self.tmp_repo_path)

        expected = INDEX_PATTERN + '_' + "ip.json"
        self.assertEqual(manager.build_file_name(INDEX_PATTERN, "ip"), expected)

    def test_folder_exists(self):
        """Test whether the method `folder_exists` properly works"""

        manager = Manager(self.tmp_repo_path)

        self.assertTrue(manager.folder_exists(manager.visualizations_folder))
        self.assertFalse(manager.folder_exists('xxx'))

    def test_get_files(self):
        """Test whether files are correctly returned"""

        manager = Manager(self.tmp_repo_path)

        expected = [INDEX_PATTERN_DASHBOARD]
        self.assertListEqual(manager.get_files(manager.index_patterns_folder), expected)

        expected = [SEARCH_DASHBOARD]
        self.assertListEqual(manager.get_files(manager.searches_folder), expected)

        expected = list.copy(VISUALIZATIONS_DASHBOARD_1)
        expected.extend(VISUALIZATIONS_DASHBOARD_2)
        expected.extend(VISUALIZATIONS_DASHBOARD_3)
        expected = list(set(expected))
        expected.sort()

        actual = manager.get_files(manager.visualizations_folder)
        actual.sort()
        self.assertListEqual(actual, expected)

    def test_load_json(self):
        """Test whether the content of JSON is correctly loaded"""

        obj_file = read_file('data/object_visualization')
        manager = Manager(self.tmp_repo_path)

        expected = json.loads(obj_file)
        self.assertDictEqual(manager.load_json('data/object_visualization'), expected)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
