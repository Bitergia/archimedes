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
    API_SEARCH_COMMAND = '_search'

    def __init__(self, base_url):
        super().__init__(base_url)

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
                else:
                    raise error

            if 'statusCode' in r_json:
                logger.error("Impossible to retrieve objects at page %s, url %s, %s",
                             params['page'], url, r_json['message'])
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
