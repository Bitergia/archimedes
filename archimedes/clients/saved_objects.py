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

import logging

import requests

from archimedes.clients.http import HttpClient
from grimoirelab_toolkit.uris import urijoin

logger = logging.getLogger(__name__)


class SavedObjects(HttpClient):
    """SavedObjects API client.

    This class allows to perform operations against the SavedObjects API, such
    as finding, deleting or updating objects stored in Kibana.

    :param base_url: the Kibana URL
    """
    API_SAVED_OBJECTS_URL = 'api/saved_objects'
    API_FIND_ENDPOINT = '_find'

    def __init__(self, base_url):
        super().__init__(base_url)

    def find(self, obj_type):
        """Find an object by its type.

        :param obj_type: obj_type

        :returns an iterator of the saved objects
        """
        fetched_objs = 0
        # The objects are retrieved one by one, since when an object cannot be retrieved, also all
        # the remaining objects are not. This happens for the metadashboard and projectname objects,
        # which cannot be retrieved because not recognized by the Kibana API.
        params = {
            'page': 1,
            'per_page': 1,
            'type': obj_type
        }

        find_url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, self.API_FIND_ENDPOINT)
        while True:
            try:
                r_json = self.fetch(find_url, params=params)
            except requests.exceptions.HTTPError as error:
                if error.response.status_code == 500:
                    logger.warning("Impossible to retrieve object at page %s, url %s", params['page'], find_url)
                    params['page'] = params['page'] + 1
                    continue
                else:
                    raise error

            if 'statusCode' in r_json:
                logger.error("Impossible to retrieve objects at page %s, url %s, %s",
                             params['page'], find_url, r_json['message'])
                params['page'] = params['page'] + 1
                continue

            if 'saved_objects' not in r_json or not r_json['saved_objects']:
                break

            yield r_json['saved_objects']
            current_page = r_json['page']
            fetched_objs += len(r_json['saved_objects'])

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

    def update_object(self, obj_type, obj_id, attributes):
        """Update the atttributes of a target object of a given type and id.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        :param attributes: a dict containing the attributes to be updated

        :returns the updated object
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, obj_type, obj_id)
        params = {
            "attributes": attributes
        }
        r = None

        try:
            r = self.put(url, data=params)
            logger.info("Object %s with id %s updated", obj_type, obj_id)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                logger.warning("No %s found with id: %s", obj_type, obj_id)
            elif error.response.status_code == 400:
                logger.warning("Impossible to update the object %s with id %s", obj_type, obj_id)
            else:
                raise error

        return r

    def create_object(self, obj_type, obj_id, attributes, overwrite=False):
        """Create an object of a given type and id with a set of attributes.

        :param obj_type: type of the new obj
        :param obj_id: ID of the new obj
        :param attributes: a dict containing the attributes of the new obj
        :param overwrite: if True, will overwrite the obj with the same ID

        :returns the created obj
        """
        url = urijoin(self.base_url, self.API_SAVED_OBJECTS_URL, obj_type, obj_id)
        data = {
            "attributes": attributes
        }

        params = {
            "overwrite": overwrite
        }

        try:
            r = self.post(url, data=data, params=params)
            logger.info("Object %s with id %s create", obj_type, obj_id)
        except requests.exceptions.HTTPError as error:
            logger.error("Object %s with id %s not created: %s", obj_type, obj_id, error)
            raise error

        return r
