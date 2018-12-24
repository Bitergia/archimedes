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

from archimedes.clients.dashboard import (Dashboard,
                                          DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.clients.saved_objects import SavedObjects
from archimedes.errors import NotFoundError, TypeObjectError
from grimoirelab_toolkit.uris import urijoin

logger = logging.getLogger(__name__)


class Kibana:
    """Kibana client.

    This class defines operations performed against the Dashboard and the SavedObjects API, such
    as exporting and importing objects.

    :param base_url: the Kibana URL
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.dashboard = Dashboard(base_url)
        self.saved_objects = SavedObjects(base_url)

    def export_by_id(self, obj_type, obj_id):
        """Export an object identified by its ID.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        """
        if obj_type == DASHBOARD:
            obj = self.dashboard.export_dashboard(obj_id)
        elif obj_type in [INDEX_PATTERN, SEARCH, VISUALIZATION]:
            obj = self.saved_objects.get_object(obj_type, obj_id)
        else:
            cause = "Unknown type %s" % obj_type
            logger.error(cause)
            raise TypeObjectError(cause=cause)

        if not obj:
            cause = "Impossible to export %s with id %s, not found" % (obj_type, obj_id)
            logger.error(cause)
            raise NotFoundError(cause=cause)

        return obj

    def export_by_title(self, obj_type, obj_title):
        """Export an object identified by its title.

        :param obj_type: type of the target object
        :param obj_title: title of the target object
        """
        obj = self.find_by_title(obj_type, obj_title)

        if not obj:
            cause = "Impossible to export %s with title %s, not found" % (obj_type, obj_title)
            logger.error(cause)
            raise NotFoundError(cause=cause)

        if obj_type == DASHBOARD:
            obj_id = obj['id']
            obj = self.dashboard.export_dashboard(obj_id)
        elif obj_type not in [INDEX_PATTERN, SEARCH, VISUALIZATION]:
            cause = "Unknown type %s" % obj_type
            logger.error(cause)
            raise TypeObjectError(cause=cause)

        return obj

    def import_objects(self, objects, force=False):
        """Import a list of objects to Kibana.

        :param objects: list of objects to import
        :param force: overwrite any existing objects on ID conflict
        """
        logger.info("Importing %s object(s)", len(objects))
        self.dashboard.import_objects(objects, force=force)

    def find_by_title(self, obj_type, obj_title):
        """Find an object by its type and title.

        :param obj_type: type of the target object
        :param obj_title: title of the target object

        :returns the target object or None if not found
        """
        url = urijoin(self.base_url, self.saved_objects.API_SAVED_OBJECTS_URL)
        found_obj = None

        for page_objs in self.saved_objects.fetch_objs(url):
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
        url = urijoin(self.base_url, self.saved_objects.API_SAVED_OBJECTS_URL)
        found_obj = None

        for page_objs in self.saved_objects.fetch_objs(url):
            for obj in page_objs:
                if obj['type'] == obj_type and obj['id'] == obj_id:
                    found_obj = obj
                    break

        if not found_obj:
            logger.warning("No %s found with title: %s", obj_type, obj_id)

        return found_obj
