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

import json
import logging
import os

from archimedes.errors import NotFoundError, RegistryError
from archimedes.kibana_obj_meta import KibanaObjMeta
from archimedes.utils import load_json

logger = logging.getLogger(__name__)

REGISTRY_NAME = ".registry"


class Registry:

    def __init__(self, root_path):
        """Registry class.

        This class allows to handle the meta objects associated to the Kibana objects using aliases,
        thus avoiding the user to deal with their IDs and titles. The registry is saved in the root
        folder of Archimedes, with name .registry. The content of the registry is as following:
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

        :param root_path: path where the registry will be stored
        """
        self.path = os.path.join(root_path, REGISTRY_NAME)

        if not os.path.exists(self.path):
            self.__create_registry()

        self.content = load_json(self.path)

    def find_all(self, obj_type=None):
        """Find all meta information related to the Kibana objects stored in the registry.

        This method returns the KibanaObjMeta in the registry. If `obj_type` is None, it returns the
        content of all the registry. Otherwise, it returns the entries related to the
        aliases with the given `obj_type`.

        :param obj_type: target object type

        :returns a generator of tuples of aliases and metadata in the registry
        """
        if obj_type:
            for alias in self.content.keys():
                if self.content[alias]['type'] == obj_type:
                    meta = KibanaObjMeta.create_from_registry(self.content[alias])
                    yield alias, meta
        else:
            for alias in self.content.keys():
                meta = KibanaObjMeta.create_from_registry(self.content[alias])
                yield alias, meta

    def find(self, alias):
        """Find the meta information of a Kibana object based on its alias.

        This method retrieves from the registry the target alias and
        KibanaObjMeta linked to it.

        :param alias: target alias

        :returns a tuple composed of an alias and metadata
        """
        if alias not in self.content:
            cause = "Alias %s not found in registry" % alias
            logger.error(cause)
            raise NotFoundError(cause=cause)

        meta = KibanaObjMeta.create_from_registry(self.content[alias])
        return alias, meta

    def clear(self):
        """Clear the registry content."""

        self.content.clear()

        self.__save_registry(self.content)
        logger.info("Registry cleared")
        return

    def delete(self, alias=None):
        """Delete an alias from the registry.

        This method deletes an alias (and its associated KibanaObjMeta) from the registry
        based on a given `alias`.

        A `NotFoundError` is thrown if the alias is not found.

        :param alias: target alias
        """
        if alias not in self.content:
            cause = "Alias %s not found in registry" % alias
            logger.error(cause)
            raise NotFoundError(cause=cause)

        self.content.pop(alias)

        self.__save_registry(self.content)
        logger.info("Alias %s deleted", alias)

    def add(self, meta_obj, force=False):
        """Add the meta information of a kibana object to the registry.

        This method adds the KibanaObjMeta to the registry. The alias is automatically assigned
        based on the current number of aliases in the registry.

        A `RegistryError` is thrown when a KibanaObjMeta already exists in the registry.

        :param meta_obj: the target meta object
        :param force: overwrite an existing registry entry if already exists
        """
        duplicate_alias = self.__check_duplicates('id', meta_obj.id)

        if not duplicate_alias:
            next_key = str(len(self.content.keys()) + 1)
            self.content[next_key] = json.loads(repr(meta_obj))

            self.__save_registry(self.content)
            logger.info("Metadata for object %s with alias %s added to the registry", meta_obj.id, next_key)
            return

        if force:
            self.content[duplicate_alias] = json.loads(repr(meta_obj))

            logger.info("Metadata for object %s already exists in the registry. Overwriting alias %s",
                        meta_obj.id, duplicate_alias)
            self.__save_registry(self.content)
        else:
            cause = "Metadata for object %s already exists in the registry" % meta_obj.id
            logger.error(cause)
            raise RegistryError(cause=cause)

    def update(self, old_alias, new_alias):
        """Update the name of an alias with a new one.

        This method replaces the name of `old_alias` with `new_alias`.

        A `NotFoundError` is thrown if the `old_alias` is not found in the registry.
        A `RegistryError` is thrown if the `new_alias` is already in use.

        :param old_alias: target alias
        :param new_alias: new alias
        """
        if old_alias not in self.content:
            cause = "Alias %s not found in registry" % old_alias
            logger.error(cause)
            raise NotFoundError(cause=cause)

        if new_alias in self.content:
            cause = "Alias %s already in use" % new_alias
            logger.error(cause)
            raise RegistryError(cause=cause)

        self.content[new_alias] = self.content.pop(old_alias)

        self.__save_registry(self.content)
        logger.info("Alias %s updated with %s", old_alias, new_alias)

    def __create_registry(self):
        with open(self.path, 'w+') as f:
            f.write('{}')
            logger.info("Registry created at %s", self.path)

    def __save_registry(self, content):
        with open(self.path, 'w') as f:
            dumped = json.dumps(content, sort_keys=True, indent=4)
            f.write(dumped)
            logger.info("Registry saved")

    def __check_duplicates(self, attr, value):
        alias = None
        for k in self.content.keys():
            entry = self.content[k]
            if entry[attr] == value:
                alias = k
                break

        return alias
