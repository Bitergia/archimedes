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

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.errors import (ExportError,
                               ImportError,
                               ObjectTypeError)
from archimedes.kibana import Kibana
from archimedes.kibana_obj_meta import KibanaObjMeta
from archimedes.manager import Manager
from archimedes.registry import Registry
from archimedes.utils import load_json

logger = logging.getLogger(__name__)


class Archimedes:
    """This class allows the import and export objects such as
    dashboards, visualizations, searches and index patterns to
    and from a Kibana instance.

    ::param url: the Kibana URL
    :param root_path: the folder where visualizations, searches and index patterns are stored
    """
    def __init__(self, url, root_path):
        self.kibana = Kibana(url)
        self.manager = Manager(root_path)
        self.registry = Registry(root_path)

    def import_from_disk(self, obj_type=None, obj_id=None, obj_title=None, obj_alias=None, find=False, force=False):
        """Locate an object based on its type and ID, title or alias on disk and import it to Kibana.
        If `find` is set to true, it also loads the related objects (i.e., visualizations,
        search and index pattern) using the `manager`.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to true.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        :param obj_title: title of the target object
        :param obj_alias: alias of the target object
        :param find: find the objects referenced in the file

        :param force: overwrite any existing objects on ID conflict
        """
        if obj_alias:
            alias, meta = self.registry.find(obj_alias)
            target_obj_type = meta.type
            target_obj_id = meta.id
            target_obj_title = None
        else:
            target_obj_type = obj_type
            target_obj_id = obj_id
            target_obj_title = obj_title

        folder_path = self.manager.build_folder_path(target_obj_type)

        if target_obj_id:
            file_name = self.manager.build_file_name(target_obj_type, target_obj_id)
            file_path = self.manager.find_file_by_name(folder_path, file_name)
        elif target_obj_title:
            file_path = self.manager.find_file_by_content_title(folder_path, target_obj_title)
        else:
            cause = "Object id, title or alias cannot be null"
            logger.error(cause)
            raise ImportError(cause=cause)

        json_content = load_json(file_path)

        if not json_content:
            logger.warning("File %s is empty", file_path)
            return

        if not find:
            logger.info("Do not find related files")
            self.__import_objects([file_path], force)
            return

        if target_obj_type == DASHBOARD:
            files = self.manager.find_dashboard_files(file_path)
        elif target_obj_type == VISUALIZATION:
            files = self.manager.find_visualization_files(file_path)
        elif target_obj_type == SEARCH:
            files = self.manager.find_search_files(file_path)
        elif target_obj_type == INDEX_PATTERN:
            cause = "Find not supported for %s" % target_obj_type
            logger.error(cause)
            raise ImportError(cause=cause)
        else:
            cause = "Object type %s not known" % target_obj_type
            logger.error(cause)
            raise ObjectTypeError(cause=cause)

        self.__import_objects(files, force=force)

    def export_to_disk(self, obj_type=None, obj_id=None, obj_title=None, obj_alias=None, force=False, index_pattern=False):
        """Locate an object based on its type and ID, title or alias in Kibana and export it to disk.
        The exported data is divided into several folders according to the type of the objects exported
        (i.e., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param obj_type: type of the target object
        :param obj_id: ID of the target object
        :param obj_title: title of the target object
        :param obj_alias: alias of the target object
        :param force: overwrite an existing file on file name conflict
        :param index_pattern: export also the index pattern
        """
        if obj_id:
            obj = self.kibana.export_by_id(obj_type, obj_id)
        elif obj_title:
            obj = self.kibana.export_by_title(obj_type, obj_title)
        elif obj_alias:
            alias, meta = self.registry.find(obj_alias)
            obj = self.kibana.export_by_id(meta.type, meta.id)
        else:
            cause = "Object id, title or alias cannot be null"
            logger.error(cause)
            raise ExportError(cause=cause)

        self.__export_objects(obj, force, index_pattern)

    def __import_objects(self, obj_paths, force=False):
        """Import dashboard, index pattern, visualization and search objects from a list
        of JSON files to Kibana. Each JSON file can be either a list of objects or a
        dict having a key 'objects' with a list of objects as value (e.g,, {'objects': [...]}.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to true.

        :param obj_paths: target object paths
        :param force: overwrite any existing objects on ID conflict
        """
        logger.info("Importing %s objects", len(obj_paths))
        for obj_path in obj_paths:
            json_content = load_json(obj_path)

            if not json_content:
                logger.warning("No objects in %s", obj_path)
                continue

            if 'objects' not in json_content:
                objects = {'objects': [json_content]}
            else:
                objects = json_content

            logger.info("Importing %s", obj_path)
            self.kibana.import_objects(objects, force)

    def __export_objects(self, data, force, index_pattern=False):
        """Export Kibana objects to disk. The exported data is divided into several
        folders according to the type of the objects exported (e.g., visualizations,
        searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to true.

        :param data: data to export (it can be a single object or a list)
        :param force: overwrite an existing file on file name conflict
        :param index_pattern: export also the corresponding index pattern
        """
        if 'objects' not in data:
            objs = [data]
        else:
            objs = data['objects']

        logger.info("Exporting objects")
        for obj in objs:
            self.manager.save_obj(obj, force)

            if index_pattern:
                logger.info("Retrieving and exporting index pattern too")
                index_pattern_id = self.manager.find_index_pattern(obj)
                index_pattern_obj = self.kibana.find_by_id(INDEX_PATTERN, index_pattern_id)
                self.manager.save_obj(index_pattern_obj, force)
