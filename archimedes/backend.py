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


DEBUG_LOG_FORMAT = "[%(asctime)s - %(name)s - %(levelname)s] - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=DEBUG_LOG_FORMAT)

JSON_EXT = '.json'


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
            logging.warning("File %s is empty", file_path)
            return

        if 'objects' not in json_content:
            objects = {'objects': [json_content]}
        else:
            objects = json_content

        dashboard = Dashboard(self.url)
        logging.info("Importing %s", file_path)
        dashboard.import_objects(objects, exclude_dashboards, exclude_index_patterns,
                                 exclude_visualizations, exclude_searches, force)

    def import_dashboard(self, dashboard_path, visualizations_folder=None, searches_folder=None,
                         index_patterns_folder=None, force=False):
        """Import a dashboard from a JSON file and the related objects (i.e., visualizations,
        search and index pattern) located in different folders.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to true.

        :param dashboard_path: path of the dashboard to import
        :param visualizations_folder: folder where visualizations are stored
        :param searches_folder: folder: folder where searches are stored
        :param index_patterns_folder: folder where index patterns are stored
        :param force: overwrite any existing objects on ID conflict
        """
        if not visualizations_folder:
            logging.error("Dashboard objects not loaded, visualizations folder not set")
            return

        if not searches_folder:
            logging.info("Dashboard searches won't be loaded, searches folder not set")

        if not index_patterns_folder:
            logging.info("Dashboard index pattern won't be loaded, index patterns folder not set")

        dashboard_files = self.find_dashboard_files(dashboard_path, visualizations_folder,
                                                    searches_folder, index_patterns_folder)
        for df in dashboard_files:
            logging.info("Importing %s", df)
            self.import_objects_from_file(df, force=force)

    def find_dashboard_files(self, dashboard_path, visualizations_folder=None,
                             searches_folder=None, index_patterns_folder=None):
        """Find the files containing the objects referenced in `dashboard_path`
        by looking into `visualizations_folder`, `searches_folder` and
        `index_patterns_folder`.

        :param dashboard_path: path of the dashboard to import
        :param visualizations_folder: folder where visualizations are stored
        :param searches_folder: folder: folder where searches are stored
        :param index_patterns_folder: folder where index patterns are stored

        :returns the list of files containing the objects that compose a dashboard
        """
        dashboard_files = []
        dash_content = load_json(dashboard_path)

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
                    and 'searchSourceJSON' in vis_content['attributes']['kibanaSavedObjectMeta'] \
                    and index_patterns_folder:
                index_content = json.loads(vis_content['attributes']['kibanaSavedObjectMeta']['searchSourceJSON'])
                index_pattern_id = index_content['index']
                ip_path = find_file(index_patterns_folder, self.file_name(INDEX_PATTERN, index_pattern_id))
                if ip_path not in dashboard_files:
                    dashboard_files.append(ip_path)

            dashboard_files.append(vis_path)

        dashboard_files.append(dashboard_path)

        return list(dashboard_files)

    def export_dashboard_by_id(self, dash_id, local_path, one_file=False, force=False):
        """Locate a dashboard by its ID in Kibana and export it to a `local path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders according
        to the type of the objects exported (i.e., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param dash_id: ID of the dashboard to export
        :param local_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        dashboard = Dashboard(self.url)
        dashboard_content = dashboard.export_dashboard_by_id(dash_id)

        if not dashboard_content:
            logging.error("Dashboard with id %s not found", dash_id)
            return

        self.__export_dashboard_content(dashboard_content, local_path, one_file, force)

    def export_dashboard_by_title(self, dash_title, local_path, one_file=False, force=False):
        """Locate a dashboard by its title in Kibana and export it to a `local path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders according to the
        type of the objects exported (i.e., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param dash_title: title of the dashboard to export
        :param local_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        dashboard = Dashboard(self.url)
        dashboard_content = dashboard.export_dashboard_by_title(dash_title)

        if not dashboard_content:
            logging.error("Dashboard with title %s not found", dash_title)
            return

        self.__export_dashboard_content(dashboard_content, local_path, one_file, force)

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

    def __export_dashboard_content(self, content, local_path, one_file, force):
        """Export the content of a dashboard to a `local path`. The exported data
        can be saved in a single file (`one_file` = True) or divided into several folders
        according to the type of the objects exported (i.e., visualizations, searches
        and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param content: title of the dashboard to export
        :param local_path: folder where to export the dashboard objects
        :param one_file: export the dashboard objects to a file
        :param force: overwrite an existing file on file name conflict
        """
        if one_file:
            logging.info("Exporting one-file dashboard to folder %s", local_path)
            dash = [obj for obj in content['objects'] if obj['type'] == 'dashboard'][0]
            file_path = os.path.join(local_path, self.file_name(dash['type'], dash['id']))
            save_to_file(content, file_path, force)
            return

        for obj in content['objects']:
            folder = self.folder_path(local_path, obj['type'])
            file_path = os.path.join(folder, self.file_name(obj['type'], obj['id']))
            save_to_file(obj, file_path, force)


def main():
    KIBITER_URL = "http://admin:admin@localhost:5601"
    archimedes = Archimedes(KIBITER_URL)

    archimedes.export_dashboard_by_title("Git", local_path='./', one_file=True, force=True)
    archimedes.import_objects_from_file('./dashboard_git.json', force=True)

    archimedes.export_dashboard_by_id("Git", local_path='./', force=True)

    archimedes.import_dashboard('./dashboard_git.json',
                                visualizations_folder='./visualizations',
                                index_patterns_folder='./index-patterns',
                                force=True)

    # KIBITER_URL = "http://localhost:5601"
    #
    # example_dashboard = {
    #     "objects": [
    #         {
    #           "id": "80b956f0-b2cd-11e8-ad8e-85441f0c2e5c",
    #           "type": "visualization",
    #           "updated_at": "2018-09-07T18:40:33.247Z",
    #           "version": 1,
    #           "attributes": {
    #             "title": "Count Example",
    #             "visState": "{\"title\":\"Count Example\",\"type\":\"metric\",\"params\":{\"addTooltip\":true,\"addLegend\":false,\"type\":\"metric\",\"metric\":{\"percentageMode\":false,\"useRanges\":false,\"colorSchema\":\"Green to Red\",\"metricColorMode\":\"None\",\"colorsRange\":[{\"from\":0,\"to\":10000}],\"labels\":{\"show\":true},\"invertColors\":false,\"style\":{\"bgFill\":\"#000\",\"bgColor\":false,\"labelColor\":false,\"subText\":\"\",\"fontSize\":60}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}}]}",
    #             "uiStateJSON": "{}",
    #             "description": "",
    #             "version": 1,
    #             "kibanaSavedObjectMeta": {
    #               "searchSourceJSON": "{\"index\":\"90943e30-9a47-11e8-b64d-95841ca0b247\",\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
    #             }
    #           }
    #         },
    #         {
    #           "id": "90943e30-9a47-11e8-b64d-95841ca0b247",
    #           "type": "index-pattern",
    #           "updated_at": "2018-09-07T18:39:47.683Z",
    #           "version": 1,
    #           "attributes": {
    #             "title": "kibana_sample_data_logs",
    #             "timeFieldName": "timestamp",
    #             "fields": "<truncated for example>",
    #             "fieldFormatMap": "{\"hour_of_day\":{}}"
    #           }
    #         },
    #         {
    #           "id": "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c",
    #           "type": "dashboard",
    #           "updated_at": "2018-09-07T18:41:05.887Z",
    #           "version": 1,
    #           "attributes": {
    #             "title": "Example Dashboard",
    #             "hits": 0,
    #             "description": "",
    #             "panelsJSON": "[{\"gridData\":{\"w\":24,\"h\":15,\"x\":0,\"y\":0,\"i\":\"1\"},\"version\":\"7.0.0-alpha1\",\"panelIndex\":\"1\",\"type\":\"visualization\",\"id\":\"80b956f0-b2cd-11e8-ad8e-85441f0c2e5c\",\"embeddableConfig\":{}}]",
    #             "optionsJSON": "{\"darkTheme\":false,\"useMargins\":true,\"hidePanelTitles\":false}",
    #             "version": 1,
    #             "timeRestore": False,
    #             "kibanaSavedObjectMeta": {
    #               "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
    #             }
    #           }
    #         }
    #     ]
    # }
    #
    # dash = Dashboard(KIBITER_URL)
    # dash.import_objects(example_dashboard)
    #
    # # Test SavedObjects
    # found = dash.saved_objects.find_by_title("visualization", "Count Example")
    # not_found = dash.saved_objects.find_by_title("visualization", "Example")
    # found = dash.saved_objects.find_by_id("visualization", "80b956f0-b2cd-11e8-ad8e-85441f0c2e5c")
    # found = dash.saved_objects.get_object("visualization", "80b956f0-b2cd-11e8-ad8e-85441f0c2e5c")
    # not_found = dash.saved_objects.get_object("visualization", "80b956f0-b2cd-11e8-ad8e-85441f0c2e5e")
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "XYZ")
    # not_found = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5x", "title", "XYZ")
    # wrong_attributes = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", {"x": "y"})
    # found = dash.saved_objects.find_by_title("dashboard", "XYZ")
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "Example Dashboard")
    # found = dash.saved_objects.find_by_title("dashboard", "Example Dashboard")
    #
    # # version is not updated in the .kibana, but it is in the object returned by the API
    # # the updated_at value changes at any time there is a modification in the object, and it is reflected in the .kibana
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "ABC")
    # found = dash.saved_objects.find_by_title("dashboard", "ABC")
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "DEF")
    # found = dash.saved_objects.find_by_title("dashboard", "DEF")
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "GHI")
    # found = dash.saved_objects.find_by_title("dashboard", "GHI")
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "title", "LMN")
    # found = dash.saved_objects.find_by_title("dashboard", "LMN")
    # # check update_at is refreshed when forcing the import of an existing object
    # previous_date = found['updated_at']
    # objects = dash.import_objects({'objects': [found]}, force=True)
    # current_date = objects['objects'][0]['updated_at']
    #
    # result = dash.saved_objects.delete_object("visualization", "80b956f0-b2cd-11e8-ad8e-85441f0c2e5c")
    # found = dash.saved_objects.find_by_id("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c")
    # panels = found['attributes']['panelsJSON']
    # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "panelsJSON", '[]')
    # found = dash.saved_objects.find_by_id("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c")
    # # deletions cause problems when exporting the dashboard, if the deleted visualization is not removed from the dashboard
    # # result = dash.saved_objects.update_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c", "panelsJSON", panels)
    # # found = dash.saved_objects.find_by_id("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c")
    #
    # # Test Dashboard
    # result = dash.export_dashboard_by_id("942dcef0-b2cd-11e8-ad8e-85441f0c2e5c")
    # not_found = dash.export_dashboard_by_id("942dcef0-b2cd-11e8-ad8e-85441f0c2e5x")
    # result = dash.export_dashboard_by_title(found['attributes']['title'])
    # result = dash.saved_objects.delete_object("dashboard", "942dcef0-b2cd-11e8-ad8e-85441f0c2e5c")
    # result = dash.saved_objects.delete_object("visualization", "80b956f0-b2cd-11e8-ad8e-85441f0c2e5c")
    # result = dash.saved_objects.delete_object("index-pattern", "90943e30-9a47-11e8-b64d-95841ca0b247")
    #
    # # Test import from Sigils
    # # error in importing Gerrit dashboard, release date not allowed (mapping set to strict)
    # result = dash.import_objects_from_file("gerrit.json", force=True, exclude_src=True)
    # found = dash.saved_objects.find_by_title("visualization", "gerrit_patchsets_per_changeset")
    # # since Gerrit dashboard has not been imported, the object is not found
    # not_found = dash.saved_objects.find_by_title("dashboard", "Gerrit")
    #
    # objects = dash.extract_objects_from_file("gerrit.json")
    # for obj in objects['objects']:
    #     dash.saved_objects.delete_object(obj['type'], obj['id'])
    #
    # dashboard = objects['objects'][0]
    # # setting the updated_at and version values doesn't have any effect
    # dashboard['updated_at'] = dashboard['attributes']['release_date']
    # dashboard['version'] = 100
    # dashboard['attributes'].pop('release_date')
    #
    # # the index pattern is needed to visualize the data
    # index_pattern = dash.extract_objects_from_file("gerrit-index-pattern.json")
    # index_pattern['objects'][0]['attributes'].pop('release_date')
    # objects['objects'].append(index_pattern['objects'][0])
    #
    # result = dash.import_objects(objects, force=True)
    # result = dash.export_dashboard_by_title("Gerrit")


if __name__ == "__main__":
    main()
