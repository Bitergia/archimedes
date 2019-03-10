# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2019 Bitergia
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

import logging
import json
import os

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.errors import NotFoundError, ObjectTypeError
from archimedes.utils import load_json

VISUALIZATIONS_FOLDER = 'visualizations'
INDEX_PATTERNS_FOLDER = 'index-patterns'
SEARCHES_FOLDER = 'searches'

JSON_EXT = '.json'

logger = logging.getLogger(__name__)


class Manager:
    """Manager class.

    This class allows to find and manage dashboard, visualization,
    search and index pattern files saved on disk.

    ::param root_path: folder where visualizations, searches and index patterns are stored
    """
    def __init__(self, folder_path):
        self.root_path = folder_path
        self.visualizations_folder = os.path.join(folder_path, VISUALIZATIONS_FOLDER)
        self.searches_folder = os.path.join(folder_path, SEARCHES_FOLDER)
        self.index_patterns_folder = os.path.join(folder_path, INDEX_PATTERNS_FOLDER)

    def find_dashboard_files(self, dashboard_path):
        """Find the dashboard-related files (visualizations, searches, index patterns) saved on disk.

        This method locates the files containing the objects referenced in `dashboard_path`
        by looking into `visualizations_folder`, `searches_folder` and
        `index_patterns_folder`.

        :param dashboard_path: path of the dashboard to import

        :returns the list of files containing the objects that compose a dashboard
        """
        dashboard_files = []
        dash_content = load_json(dashboard_path)

        if not self.folder_exists(self.visualizations_folder):
            logger.info("Visualizations not loaded for %s, visualizations folder doesn't exist", dashboard_path)
            dashboard_files.append(dashboard_path)
            return dashboard_files

        panels = json.loads(dash_content['attributes']['panelsJSON'])
        for panel in panels:
            if panel['type'] == VISUALIZATION:
                panel_path = self.find_file_by_name(self.visualizations_folder, self.build_file_name(VISUALIZATION, panel['id']))
                panel_files = self.find_visualization_files(panel_path)
            elif panel['type'] == SEARCH:
                panel_path = self.find_file_by_name(self.searches_folder, self.build_file_name(SEARCH, panel['id']))
                panel_files = self.find_search_files(panel_path)
            else:
                cause = "Panel type %s not handled" % (panel['type'])
                logger.error(cause)
                raise ObjectTypeError(cause=cause)

            [dashboard_files.append(p) for p in panel_files if p not in dashboard_files]

        dashboard_files.append(dashboard_path)

        return dashboard_files

    def find_visualization_files(self, visualization_path):
        """Find the visualization-related files (searches, index patterns) saved on disk.

        This method locates the files containing the objects referenced in `visualization_path`
        by looking into `searches_folder` and `index_patterns_folder`.

        :param visualization_path: path of the visualization to import

        :returns the list of files containing the objects that compose a visualization
        """
        visualization_files = []
        vis_content = load_json(visualization_path)

        if not self.folder_exists(self.searches_folder):
            logger.info("Searches won't be loaded for %s, searches folder doesn't exist",
                        visualization_path)

        if not self.folder_exists(self.index_patterns_folder):
            logger.info("Index patterns won't be loaded for %s, index patterns folder doesn't exist",
                        visualization_path)

        if 'savedSearchId' in vis_content['attributes'] and self.folder_exists(self.searches_folder):
            search_id = vis_content['attributes']['savedSearchId']
            search_path = self.find_file_by_name(self.searches_folder, self.build_file_name(SEARCH, search_id))
            if search_path not in visualization_files:
                visualization_files.append(search_path)
                search_files = self.find_search_files(search_path)
                [visualization_files.append(sf) for sf in search_files if sf not in visualization_files]

        search_files = self.find_search_files(visualization_path)
        [visualization_files.append(sf) for sf in search_files if sf not in visualization_files]

        return visualization_files

    def find_search_files(self, search_path):
        """Find the search-related files (index patterns) saved on disk.

        This method locates the files containing the objects referenced in `search_path`
        by looking into `index_patterns_folder`.

        :returns the list of files containing the objects that compose a search
        """
        search_files = []
        search_content = load_json(search_path)

        index_pattern_id = self.find_index_pattern(search_content)
        if not index_pattern_id:
            logger.info("No index pattern declared for %s", search_path)
            search_files.append(search_path)
            return search_files

        ip_path = self.find_file_by_name(self.index_patterns_folder, self.build_file_name(INDEX_PATTERN, index_pattern_id))
        if ip_path not in search_files:
            search_files.append(ip_path)

        search_files.append(search_path)

        return search_files

    def find_index_pattern(self, obj):
        """Find the index pattern id in an `obj`.

        This method extracts the index pattern defined in a Kibana object.

        :param obj: Kibana object

        :returns the index pattern id
        """
        index_pattern = None
        if 'kibanaSavedObjectMeta' in obj['attributes'] \
                and 'searchSourceJSON' in obj['attributes']['kibanaSavedObjectMeta']:
            search_content = json.loads(obj['attributes']['kibanaSavedObjectMeta']['searchSourceJSON'])
            if 'index' not in search_content:
                return index_pattern

            index_pattern = search_content['index']

        return index_pattern

    def build_folder_path(self, obj_type):
        """Build the path of a folder according to the object type.

        This method builds the folder using the `obj_type` passed in input.

        :param obj_type: type of the object
        """
        folder_path = self.root_path

        if obj_type == VISUALIZATION:
            name = VISUALIZATIONS_FOLDER
        elif obj_type == INDEX_PATTERN:
            name = INDEX_PATTERNS_FOLDER
        elif obj_type == SEARCH:
            name = SEARCHES_FOLDER
        elif obj_type == DASHBOARD:
            name = ''
        else:
            cause = "Unknown type %s" % obj_type
            logger.error(cause)
            raise ObjectTypeError(cause=cause)

        folder_path = os.path.join(folder_path, name)

        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def save_obj(self, obj, force=False):
        """Save the object to disk.

        This method serializes a Kibana object to disk. It can overwrite previous versions of
        existing object by setting the parameter `force` to True. In case `force` is not True,
        and the object exists, a warning message is logged to notify the user that the object
        cannot be overwritte.

        :param obj: the object to be saved
        :param force: overwrite an existing object if already exists on disk
        """
        folder = self.build_folder_path(obj['type'])
        file_path = os.path.join(self.root_path, folder, self.build_file_name(obj['type'], obj['id']))

        content = json.dumps(obj, sort_keys=True, indent=4)

        if os.path.exists(file_path) and not force:
            logger.warning("Object already exists at %s, it won't be overwritten", file_path)
            return

        with open(file_path, "w+") as f:
            f.write(content)
            logger.info("Object saved at %s", file_path)

    @staticmethod
    def find_file_by_content_title(folder_path, content_title):
        """Find a file on disk by its content title.

        This method locates a file with a title equal to `content_title` in
        a `folder_path`. The method raises a `NotFoundError` in case the file
        is not found.

        :param folder_path: the folder where to look for the file
        :param content_title: the content title of the target file

        :returns: the file path of the file
        """
        if not Manager.folder_exists(folder_path):
            cause = "Folder %s not found" % folder_path
            logger.error(cause)
            raise NotFoundError(cause=cause)

        files = Manager.get_files(folder_path)
        found = None
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            content = load_json(file_path)
            if content['attributes']['title'] == content_title:
                found = file_path
                break

        if not found:
            cause = "File with content title %s not found in %s" % (content_title, folder_path)
            logger.error(cause)
            raise NotFoundError(cause=cause)

        return found

    @staticmethod
    def find_file_by_name(folder_path, target_name):
        """Find a file on disk by its name.

        This method locates a file with `target_name` in a `folder_path`. The method
        raises a `NotFoundError` in case the file is not found.

        :param folder_path: the folder where to look for the file
        :param target_name: the name of the target file

        :returns: the file path of the file
        """
        if not Manager.folder_exists(folder_path):
            cause = "Folder %s not found" % folder_path
            logger.error(cause)
            raise NotFoundError(cause=cause)

        files = Manager.get_files(folder_path)
        found = None
        for name in files:
            if target_name == name:
                found = os.path.join(folder_path, target_name)
                break

        if not found:
            cause = "File %s not found in %s" % (target_name, folder_path)
            logger.error(cause)
            raise NotFoundError(cause=cause)

        return found

    def find_all(self):
        """Find all objects on disk.

        This method returns all objects stored on disk together with their corresponding file paths.

        :returns: a generator of tuples composed by Kibana objects and their file paths
        """
        for path, subdirs, files in os.walk(self.root_path):
            for name in files:
                if not any(name.startswith(t) for t in [VISUALIZATION, INDEX_PATTERN, SEARCH, DASHBOARD]):
                    continue

                file_path = os.path.join(path, name)
                with open(file_path, 'r') as f:
                    content = f.read()
                content = json.loads(content)
                yield file_path, content

    @staticmethod
    def build_file_name(obj_type, obj_id):
        """Build the file name where a Kibana object is stored.

        This method builds the name of a file according to the object type and ID.

        :param obj_type: type of the object
        :param obj_id: ID of the object
        """
        name = obj_type + '_' + obj_id + JSON_EXT
        return name

    @staticmethod
    def folder_exists(folder_path):
        """Check that a folder exists.

        :param folder_path: the path of a folder
        """
        return os.path.isdir(folder_path)

    @staticmethod
    def get_files(folder_path):
        """Get the files in `folder_path`.

        :param folder_path: the path of a folder
        """
        files = [f for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(JSON_EXT)]
        return files
