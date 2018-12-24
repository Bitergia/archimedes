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

import requests

from archimedes.clients.http import KibanaClient

from grimoirelab_toolkit.uris import urijoin

DASHBOARD = "dashboard"
SEARCH = "search"
VISUALIZATION = "visualization"
INDEX_PATTERN = "index-pattern"

logger = logging.getLogger(__name__)


class SavedObjects(KibanaClient):
    """SavedObjects API wrapper.

    This class allows to perform operations against the SavedObjects API, such
    as finding, deleting or updating objects stored in Kibana.

    :param base_url: the Kibana URL
    """
    API_SAVED_OBJECTS_URL = 'api/saved_objects'
    API_SEARCH_COMMAND = '_search'

    def __init__(self, base_url):
        super().__init__(base_url)

    def find_by_title(self, obj_type, obj_title):
        """Find an object by its type and title.

        :param obj_type: type of the target object
        :param obj_title: title of the target object

        :returns the target object or None if not found
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL)
        found_obj = None

        for page_objs in self.fetch_objs(url):
            for obj in page_objs:
                if obj['type'] == obj_type and obj['attributes']['title'] == obj_title:
                    found_obj = obj
                    break

        if not found_obj:
            logger.warning("No %s found with title: %s", obj_type, obj_title)

        return found_obj

    def find_by_id(self, obj_type, obj_id):
        """Find an object by its type and title.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object

        :returns the target object or None if not found
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL)
        found_obj = None

        for page_objs in self.fetch_objs(url):
            for obj in page_objs:
                if obj['type'] == obj_type and obj['id'] == obj_id:
                    found_obj = obj
                    break

        if not found_obj:
            logger.warning("No %s found with title: %s", obj_type, obj_id)

        return found_obj

    def fetch_objs(self, url):
        """Find an object by its type and title.

        :param url: saved_objects endpoint

        :returns an iterator of the saved objects
        """
        fetched_objs = 0
        params = {
            'page': 1
        }

        while True:
            try:
                r_json = self.fetch(url, params=params)
            except requests.exceptions.HTTPError as error:
                if error.response.status_code == 500:
                    logger.warning("Impossible to retrieve objects at page %s, url %s", params['page'], url)
                    params['page'] = params['page'] + 1
                    continue

            yield r_json['saved_objects']
            current_page = r_json['page']
            fetched_objs += len(r_json['saved_objects'])

            if not r_json['saved_objects']:
                break

            params['page'] = current_page + 1

    def get_object(self, obj_type, obj_id):
        """Get the object by its type and id.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object

        :returns the target object
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, obj_type, obj_id)

        r = None
        try:
            r = self.fetch(url)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.warning("No %s found with id: %s", obj_type, obj_id)
            else:
                raise error

        return r

    def delete_object(self, obj_type, obj_id):
        """Delete the object with a given type and id.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, obj_type, obj_id)
        try:
            self.delete(url)
            logger.info("Object %s with id %s deleted", obj_type, obj_id)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.warning("No %s found with id: %s", obj_type, obj_id)
            else:
                raise error

    def update_object(self, obj_type, obj_id, attr, value):
        """Update an attribute of a target object of a given type and id.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        :param attr: attribute to update
        :param value: new value of attribute

        :returns the updated object
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, obj_type, obj_id)
        params = {
            "attributes": {
                attr: value
            }
        }
        r = None

        try:
            r = self.put(url, data=params)
            logger.info("Object %s with id %s updated", obj_type, obj_id)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.warning("No %s found with id: %s", obj_type, obj_id)
            elif error.response.status_code == 400:
                logger.warning("Impossible to update attribute %s with value %s, for %s with id %s",
                               attr, value, obj_type, obj_id)
            else:
                raise error

        return r


class Dashboard(KibanaClient):
    """Dashboard API wrapper.

    This class allows to perform operations against the Dashboard API, such
    as exporting and importing dashboard.

    :param base_url: the Kibana URL
    """
    API_DASHBOARDS_URL = 'api/kibana/dashboards'
    API_IMPORT_COMMAND = 'import'
    API_EXPORT_COMMAND = 'export'

    def __init__(self, base_url):
        self.base_url = base_url
        self.saved_objects = SavedObjects(self.base_url)

    def export_object(self, ref_type, obj_type, obj_ref):

    def export_dashboard_by_title(self, dashboard_title):
        """Export a dashboard identified by its title.

        :param dashboard_title: title of the dashboard

        :returns the dashboard exported
        """
        dashboard = self.saved_objects.find_by_title("dashboard", dashboard_title)

        if not dashboard:
            logger.error("Impossible to export dashboard with title %s, not found", dashboard_title)
            return

        dashboard_id = dashboard['id']
        dashboard = self.export_dashboard_by_id(dashboard_id)

        return dashboard

    def export_dashboard_by_id(self, dashboard_id):
        """Export a dashboard identified by its ID.

        :param dashboard_id: ID of the dashboard

        :returns the dashboard exported
        """
        url = urijoin(self.base_url, self.API_DASHBOARDS_URL, self.API_EXPORT_COMMAND + '?dashboard=' + dashboard_id)

        dashboard = None
        try:
            dashboard = self.fetch(url)

            if 'error' in dashboard['objects'][0]:
                msg = dashboard['objects'][0]['error']['message'].lower()
                logger.error("Impossible to export dashboard with id %s, %s", dashboard_id, msg)
                dashboard = None
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 400:
                logger.error("Impossible to export dashboard with id %s", dashboard_id)
            else:
                raise error

        return dashboard

    def import_objects(self, data, exclude_dashboards=False, exclude_index_patterns=False,
                       exclude_visualizations=False, exclude_searches=False, force=False):
        """Import objects from a dictionary.

        :param data: dictionary
        :param exclude_dashboards: do not import dashboards
        :param exclude_index_patterns: do not import index patterns
        :param exclude_visualizations: do not import visualizations
        :param exclude_searches: do not import searches
        :param force: overwrite any existing objects on ID conflict
        """
        url = urijoin(self.base_url, self.API_DASHBOARDS_URL, self.API_IMPORT_COMMAND)
        params = {
            'exclude': [],
            'force': 'false'
        }

        if exclude_dashboards:
            params['exclude'].append(DASHBOARD)
        if exclude_index_patterns:
            params['exclude'].append(INDEX_PATTERN)
        if exclude_visualizations:
            params['exclude'].append(VISUALIZATION)
        if exclude_searches:
            params['exclude'].append(SEARCH)

        if force:
            params['force'] = 'true'

        response = self.post(url, data, params)

        total = len(response['objects'])
        for obj in response['objects']:
            if 'error' not in obj:
                continue

            response['objects'].remove(obj)
            logger.error("%s with id %s not imported, %s", obj['type'], obj['id'], obj['error']['message'])

        logger.info("%s/%s object(s) imported", len(response['objects']), total)
