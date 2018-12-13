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

import logging
import json
import os

from archimedes.apis import (Dashboard,
                             INDEX_PATTERN,
                             SEARCH,
                             VISUALIZATION)
from archimedes.utils import (load_json,
                              save_to_file,
                              find_file)

JSON_EXT = '.json'

logger = logging.getLogger(__name__)


class Archimedes:
    VISUALIZATIONS_FOLDER = 'visualizations'
    INDEX_PATTERNS_FOLDER = 'index-patterns'
    SEARCHES_FOLDER = 'searches'

    def __init__(self, url):
        self.url = url

    def import_objects_from_file(self, file_path, exclude_dashboards=False, exclude_index_patterns=False,
                                 exclude_visualizations=False, exclude_searches=False, force=False):
        """Import dashboards, index patterns, visualizations and searches from a JSON file to Kibana.
        The JSON file should be either a list of objects or a dict having a key 'objects'
        with a list of objects as value (e.g,, {'objects': [...]}.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to true.

        :param file_path: path of the target file
        :param exclude_dashboards: do not import dashboards
        :param exclude_index_patterns: do not import index patterns
        :param exclude_visualizations: do not import visualizations
        :param exclude_searches: do not import searches
        :param force: overwrite any existing objects on ID conflict
        """
        json_content = load_json(file_path)

        if not json_content:
            logger.warning("File %s is empty", file_path)
            return

        if 'objects' not in json_content:
            objects = {'objects': [json_content]}
        else:
            objects = json_content

        dashboard = Dashboard(self.url)
        logger.info("Importing %s", file_path)
        dashboard.import_objects(objects, exclude_dashboards, exclude_index_patterns,
                                 exclude_visualizations, exclude_searches, force)

    def import_dashboard(self, dashboard_path, visualizations_folder=None, searches_folder=None,
                         index_patterns_folder=None, force=False):
        """Import a dashboard from a JSON file and the related objects (i.e., visualizations,
        search and index pattern) located in different folders.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to true.

        :param dashboard_path: path of the dashboard to import
        :param visualizations_folder: folder where visualization objects are stored
        :param searches_folder: folder where search objects are stored
        :param index_patterns_folder: folder where index pattern objects are stored
        :param force: overwrite any existing objects on ID conflict
        """
        dashboard_files = self.find_dashboard_files(dashboard_path, visualizations_folder,
                                                    searches_folder, index_patterns_folder)
        for df in dashboard_files:
            self.import_objects_from_file(df, force=force)

    def find_dashboard_files(self, dashboard_path, visualizations_folder=None,
                             searches_folder=None, index_patterns_folder=None):
        """Find the files containing the objects referenced in `dashboard_path`
        by looking into `visualizations_folder`, `searches_folder` and
        `index_patterns_folder`.

        :param dashboard_path: path of the dashboard to import
        :param visualizations_folder: folder where visualization objects are stored
        :param searches_folder: folder where searches objects are stored
        :param index_patterns_folder: folder where index pattern objects are stored

        :returns the list of files containing the objects that compose a dashboard
        """
        dashboard_files = []
        dash_content = load_json(dashboard_path)

        if not visualizations_folder:
            logger.info("Visualizations not loaded, visualizations folder not set")
            dashboard_files.append(dashboard_path)
            return dashboard_files

        if not searches_folder:
            logger.info("Searches won't be loaded, searches folder not set")

        if not index_patterns_folder:
            logger.info("Index patterns won't be loaded, index patterns folder not set")

        visualizations = json.loads(dash_content['attributes']['panelsJSON'])
        for vis in visualizations:
            vis_path = find_file(visualizations_folder, self.file_name(VISUALIZATION, vis['id']))
            vis_content = load_json(vis_path)

            if 'savedSearchId' in vis_content['attributes'] and searches_folder:
                search_id = vis_content['attributes']['savedSearchId']
                search_path = find_file(searches_folder, self.file_name(SEARCH, search_id))
                if search_path not in dashboard_files:
                    dashboard_files.append(search_path)

            if 'kibanaSavedObjectMeta' in vis_content['attributes'] \
                    and 'searchSourceJSON' in vis_content['attributes']['kibanaSavedObjectMeta'] and index_patterns_folder:
                index_content = json.loads(vis_content['attributes']['kibanaSavedObjectMeta']['searchSourceJSON'])
                index_pattern_id = index_content['index']
                ip_path = find_file(index_patterns_folder, self.file_name(INDEX_PATTERN, index_pattern_id))
                if ip_path not in dashboard_files:
                    dashboard_files.append(ip_path)

            dashboard_files.append(vis_path)

        dashboard_files.append(dashboard_path)

        return list(dashboard_files)

    def export_dashboard_by_id(self, dash_id, folder_path, one_file=False, force=False):
        """Locate a dashboard by its ID in Kibana and export it to a `folder_path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders according
        to the type of the objects exported (i.e., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param dash_id: ID of the dashboard to export
        :param folder_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        dashboard = Dashboard(self.url)
        dashboard_content = dashboard.export_dashboard_by_id(dash_id)

        if not dashboard_content:
            logger.error("Dashboard with id %s not found", dash_id)
            return

        self.__export_dashboard_content(dashboard_content, folder_path, one_file, force)

    def export_dashboard_by_title(self, dash_title, folder_path, one_file=False, force=False):
        """Locate a dashboard by its title in Kibana and export it to a `folder_path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders according to the
        type of the objects exported (i.e., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param dash_title: title of the dashboard to export
        :param folder_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        dashboard = Dashboard(self.url)
        dashboard_content = dashboard.export_dashboard_by_title(dash_title)

        if not dashboard_content:
            logger.error("Dashboard with title %s not found", dash_title)
            return

        self.__export_dashboard_content(dashboard_content, folder_path, one_file, force)

    @staticmethod
    def file_name(obj_type, obj_id):
        """Build the name of a file according the object type and ID.

        :param obj_type: type of the object
        :param obj_id: ID of the object
        """
        name = obj_type + '_' + obj_id + JSON_EXT
        return name.lower()

    @staticmethod
    def folder_path(root_path, obj_type):
        """Build the path of a folder according to the object type.

        :param root_path: root path
        :param obj_type: type of the object
        """
        name = ''
        folder_path = root_path

        if obj_type == VISUALIZATION:
            name = Archimedes.VISUALIZATIONS_FOLDER
        elif obj_type == INDEX_PATTERN:
            name = Archimedes.INDEX_PATTERNS_FOLDER
        elif obj_type == SEARCH:
            name = Archimedes.SEARCHES_FOLDER

        if name:
            folder_path = os.path.join(root_path, name)

        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def __export_dashboard_content(self, content, folder_path, one_file, force):
        """Export the content of a dashboard to a `folder_path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders
        according to the type of the objects exported (i.e., visualizations, searches
        and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param content: title of the dashboard to export
        :param folder_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        if one_file:
            logger.info("Exporting one-file dashboard to folder %s", folder_path)
            dash = [obj for obj in content['objects'] if obj['type'] == 'dashboard'][0]
            file_path = os.path.join(folder_path, self.file_name(dash['type'], dash['id']))
            save_to_file(content, file_path, force)
            return

        for obj in content['objects']:
            folder = self.folder_path(folder_path, obj['type'])
            file_path = os.path.join(folder, self.file_name(obj['type'], obj['id']))
            save_to_file(obj, file_path, force)
