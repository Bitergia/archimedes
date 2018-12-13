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


import requests
import json

HEADERS = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true"
}


class KibanaClient:

    @staticmethod
    def fetch(url, params=None, headers=HEADERS):
        """Fetch the data from a given URL.

        :param url: link to the resource
        :param params: params of the request
        :param headers: headers of the request

        :returns a response object
        """
        response = requests.get(url, params=params, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise error

        return response.json()

    @staticmethod
    def delete(url, headers=HEADERS):
        """Delete the target object pointed by the url.

        :param url: link to the resource
        :param headers: headers of the request

        :returns a response object
        """
        response = requests.delete(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise error

        return response.json()

    @staticmethod
    def put(url, data, headers=HEADERS):
        """Update the target object pointed by the url.

        :param url: link to the resource
        :param data: data to upload
        :param headers: headers of the request

        :returns a response object
        """
        response = requests.put(url, data=json.dumps(data), headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise error

        return response.json()

    @staticmethod
    def post(url, data, params, headers=HEADERS):
        """Update the target object pointed by the url.

        :param url: link to the resource
        :param data: data to upload
        :param params: params of the request
        :param headers: headers of the request

        :returns a response object
        """
        response = requests.post(url, params=params, data=json.dumps(data), headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise error

        return response.json()
