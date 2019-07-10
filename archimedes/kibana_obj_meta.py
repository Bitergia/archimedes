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


class KibanaObjMeta:
    """KibanaObjMeta class.

    This class models the metadata information of Kibana objects which includes the ID,
    title, type and version of the object plus when the object was updated if not None.

    :param id: object id
    :param title: object title
    :param type: object type
    :param version: object version
    :param updated_at: time when the object was updated, it can be None
    """
    def __init__(self, id, title, type, version, updated_at=None):
        self.id = id
        self.title = title
        self.type = type
        self.version = version
        self.updated_at = updated_at

    def __repr__(self):
        meta = {
            'id': self.id,
            'type': self.type,
            'version': self.version,
            'title': self.title
        }

        if self.updated_at:
            meta['updated_at'] = self.updated_at

        return json.dumps(meta, sort_keys=True, indent=4)

    @classmethod
    def create_from_obj(cls, obj):
        """Create meta information corresponding to a Kibana object.

        This method creates a KibanaObjMeta from a Kibana object using
        its `id`, `title`, `type`, `version` and `updated_at`.

        :param obj: Kibana object
        """
        updated_at = obj['updated_at'] if 'updated_at' in obj else None

        return KibanaObjMeta(obj['id'], obj['attributes']['title'], obj['type'], obj['version'], updated_at)

    @classmethod
    def create_from_registry(cls, entry):
        """Create a meta information corresponding to a entry in the registry.

        This method creates a KibanaObjMeta from an entry in the registry (the serialization of
        a KibanaObjMeta) using its `id`, `title`, `type`, `version` and `updated_at`.

        :param entry: registry entry
        """
        updated_at = entry['updated_at'] if 'updated_at' in entry else None

        return KibanaObjMeta(entry['id'], entry['title'], entry['type'], entry['version'], updated_at)
