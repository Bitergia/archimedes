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

from archimedes.clients.dashboard import (DASHBOARD,
                                          INDEX_PATTERN,
                                          SEARCH,
                                          VISUALIZATION)
from archimedes.errors import (DataExportError,
                               DataImportError,
                               ObjectTypeError)
from archimedes.kibana import Kibana
from archimedes.kibana_obj_meta import KibanaObjMeta
from archimedes.manager import Manager
from archimedes.registry import Registry
from archimedes.utils import load_json

logger = logging.getLogger(__name__)


class Archimedes:
    """Archimedes class.

    This class handles Kibana objects (such as dashboards, visualizations, searches and index patterns)
    stored in a Kibana instance and/or on disk (the `root_path` of Archimedes). Archimedes allows to
    import (from disk to Kibana), export (from Kibana to disk) and list Kibana objects. Furthermore,
    Archimedes provides also a registry, in charge of managing the metadata of Kibana objects to which
    the user can assign aliases to simply import and export operations of the corresponding objects.

    ::param url: the Kibana URL
    :param root_path: the folder where visualizations, searches and index patterns are stored
    """
    def __init__(self, url, root_path):
        self.kibana = Kibana(url)
        self.manager = Manager(root_path)
        self.registry = Registry(root_path)

    def import_from_disk(self, obj_type=None, obj_id=None, obj_title=None, obj_alias=None, find=False, force=False):
        """Import Kibana objects stored on disk.

        Locate an object on disk based on its type and ID, title or alias and import it to Kibana.
        If `find` is set to True, it also loads the related objects (i.e., visualizations,
        search and index pattern) using the `manager`.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to True.

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
            cause = "Object id, title or alias cannot be None"
            logger.error(cause)
            raise DataImportError(cause=cause)

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
            raise DataImportError(cause=cause)
        else:
            cause = "Object type %s not known" % target_obj_type
            logger.error(cause)
            raise ObjectTypeError(cause=cause)

        self.__import_objects(files, force=force)

    def export_to_disk(self, obj_type=None, obj_id=None, obj_title=None, obj_alias=None, force=False, index_pattern=False):
        """Export Kibana objects stored in a Kibana instance to disk.

        Locate an object in Kibana based on its type and ID, title or alias and export it to disk.
        The exported data is divided into several folders according to the type of the objects exported
        (e.g., visualizations, searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to True.

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
            cause = "Object id, title or alias cannot be None"
            logger.error(cause)
            raise DataExportError(cause=cause)

        self.__export_objects(obj, force, index_pattern)

    def inspect(self, local=False, remote=False):
        """List the Kibana objects stored remotely (in the Kibana instance) or locally (on disk).

        The method lists objects handled by Archimedes. The param `local` shows the ones on disk,
        while the param `remote` the ones in Kibana.

        :param local: if True, list the objects on disk
        :param remote: if True, list the objects in Kibana

        :returns a generator of Kibana objects
        """
        objs = []
        if remote:
            objs = self.__find_remote_objs()
        elif local:
            objs = self.__find_local_objs()

        return objs

    def populate_registry(self, force=False):
        """Populate the content of the registry using the remote Kibana objects.

        The method populates the .registry file using the objects in the Kibana instance. The
        registry includes a list of entries which contain metadata of the Kibana objects, where
        each entry has an alias associated, as the example below:

        [
            "1": {
                    'id': 'Search:_pull_request:false',
                    'title': 'Search:_pull_request:false',
                    'type': 'search',
                    'version': 1
            },
            "2": {
                    'id': '8539ada0-9960-11e8-8771-a349686d998a',
                    'title': 'dockerhub',
                    'type': 'index-pattern',
                    'version': 1
            },
            ...
        ]

        :param force: overwrite an existing registry entry if already exists
        """
        for obj in self.__find_remote_objs():
            logger.info("Adding object %s to registry", obj.id)
            self.registry.add(obj, force=force)
            logger.info("Object %s added to registry", obj.id)

    def query_registry(self, alias):
        """Query the content of the registry.

        This method queries the content of the registry to return the metadata
        information associated to a single `alias`.

        :param alias: the name of the target alias

        :returns: a KibanaObjMeta obj
        """
        return self.registry.find(alias)

    def list_registry(self, obj_type=None):
        """List the content of the registry.

        This method lists the content of the .registry file. If `obj_type` is None, it returns the
        content of all the registry. Otherwise, it returns the information related to the
        aliases with the given `obj_type`.

        :param obj_type: the type of the objects to show

        :returns: a generator of aliases in the registry
        """
        if obj_type:
            if obj_type not in [DASHBOARD, VISUALIZATION, SEARCH, INDEX_PATTERN]:
                cause = "Object type %s is unknown" % obj_type
                logger.error(cause)
                raise ObjectTypeError(cause=cause)

        for alias, meta in self.registry.find_all(obj_type):
            yield alias, meta

    def clear_registry(self):
        """Clear the content of the registry."""

        logger.info("Clearing registry")
        self.registry.clear()
        return

    def delete_registry(self, alias=None):
        """Delete an alias from the registry.

        This method removes the information associated to an alias.

        :param alias: the name of the target alias
        """
        logger.info("Deleting alias %s from registry", alias)
        self.registry.delete(alias)

    def update_registry(self, alias, new_alias):
        """Update an alias saved in the registry.

        This method allows to rename an alias with a new one. If the
        new alias is already in use, a RegistryError is thrown.

        :param alias: the name of the target alias
        :param new_alias: the new name of the alias
        """
        logger.info("Updating alias %s with %s", alias, new_alias)
        self.registry.update(alias, new_alias)

    def __import_objects(self, obj_paths, force=False):
        """Import Kibana object to the Kibana instance.

        This method imports dashboard, index pattern, visualization and search objects from a list
        of JSON files to Kibana. Each JSON file can be either a list of objects or a
        dict having a key 'objects' with a list of objects as value (e.g,, {'objects': [...]}.

        The method can overwrite previous versions of existing objects by setting
        the parameter `force` to True.

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
        """Export Kibana objects to disk.

        This method exports the Kibana objects stored remotely. They are saved to several
        folders according to the type of the objects exported (e.g., visualizations,
        searches and index patterns).

        The method can overwrite previous versions of existing files by setting the
        parameter `force` to True.

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

    def __find_remote_objs(self):
        """Return the meta information of the Kibana objects stored in Kibana."""

        for obj in self.kibana.find_all():
            if obj['type'] not in [VISUALIZATION, INDEX_PATTERN, SEARCH, DASHBOARD]:
                continue

            meta_obj = KibanaObjMeta.create_from_obj(obj)
            yield meta_obj

    def __find_local_objs(self):
        """Return the meta information of the Kibana objects stored on disk."""

        for path, obj in self.manager.find_all():
            meta_obj = KibanaObjMeta.create_from_obj(obj)
            yield meta_obj
