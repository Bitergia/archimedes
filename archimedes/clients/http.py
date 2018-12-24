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

import json

import requests
import urllib3.util


HEADERS = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true"
}

SLEEP_TIME = 1
MAX_RETRIES = 5


class HttpClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self._create_http_session()

    def _create_http_session(self):
        """Create a http session and initialize the retry object."""

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        retries = urllib3.util.Retry(total=MAX_RETRIES,
                                     backoff_factor=SLEEP_TIME)

        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

    def _close_http_session(self):
        """Close the http session."""

        if self.session:
            self.session.keep_alive = False

    def fetch(self, url, params=None, headers=HEADERS):
        """Fetch the data from a given URL.

        :param url: link to the resource
        :param params: params of the request
        :param headers: headers of the request

        :returns a response object
        """
        response = self.session.get(url, params=params, headers=headers)
        return response.json()

    def delete(self, url, headers=HEADERS):
        """Delete the target object pointed by the url.

        :param url: link to the resource
        :param headers: headers of the request

        :returns a response object
        """
        response = self.session.delete(url, headers=headers)
        return response.json()

    def put(self, url, data, headers=HEADERS):
        """Update the target object pointed by the url.

        :param url: link to the resource
        :param data: data to upload
        :param headers: headers of the request

        :returns a response object
        """
        response = self.session.put(url, data=json.dumps(data), headers=headers)
        return response.json()

    def post(self, url, data, params, headers=HEADERS):
        """Update the target object pointed by the url.

        :param url: link to the resource
        :param data: data to upload
        :param params: params of the request
        :param headers: headers of the request

        :returns a response object
        """
        response = self.session.post(url, params=params, data=json.dumps(data), headers=headers)
        return response.json()
