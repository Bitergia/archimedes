# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
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

import argparse
import requests
import yaml

from archimedes.archimedes import logger
from grimoirelab_toolkit.uris import urijoin

METADASHBOARD = 'metadashboard'
PROJECTNAME = 'projectname'
CONTENT_TYPE_HEADER = {"Content-Type": "application/json"}


def get_params():
    parser = argparse.ArgumentParser(usage="usage: Thales [options]",
                                     description="Generate a menu.yml which can be processed by Archimedes")

    parser.add_argument('elasticsearch_url', help='ElasticSearch URL', default=None)
    parser.add_argument('kibiter_index', help='Kibiter index', default='.kibiter')
    parser.add_argument('top_menu_path', help='Target location where to store the YAML file')
    args = parser.parse_args()

    return args


def get_kibiter_data(elasticsearch_url, kibiter_index, endpoint):
    """Get the data from a Kibiter endpoint

    :param elasticsearch_url: URL of elasticsearch DB
    :param kibiter_index: name of the target index
    :param endpoint: the top-menu Kibiter-related endpoint (`metadashbord` or `projectname`)

    :return the content of the endpoint
    """
    endpoint_url = urijoin(elasticsearch_url, kibiter_index, 'doc', endpoint)
    response = requests.get(endpoint_url, headers=CONTENT_TYPE_HEADER, verify=False)
    r_json = None
    try:
        response.raise_for_status()
        r_json = response.json()['_source'][endpoint]
    except Exception as ex:
        logger.error("No data retrieved from %s, %s" % (endpoint, ex))

    return r_json


def save_yaml(data, file_path):
    """Save the data defined as dict to a YAML file

    :param data: a dictionary containing the top menu data
    :param file_path: path of the YAML file
    """
    menu = yaml.dump(data, default_flow_style=False)
    with open(file_path, 'w') as f:
        try:
            f.write(menu)
        except yaml.YAMLError as ex:
            logger.error(ex)


def generate(elasticsearch_url, kibiter_index):
    """Generate a top menu YAML file that can be processed by Pythagoras

    :param elasticsearch_url: URL of elasticsearch DB
    :param kibiter_index: name of the target index
    """
    metadashboard = get_kibiter_data(elasticsearch_url, kibiter_index, METADASHBOARD)
    project_name = get_kibiter_data(elasticsearch_url, kibiter_index, PROJECTNAME).get('name')

    menu = {'project': project_name}
    tabs = []
    for m in metadashboard:
        tab = {
            'tab': m['name']
        }
        dashboards = m.get('dashboards', [])
        if not dashboards:
            tab['dashboard-id'] = m['panel_id']
            tab['description'] = m['description']
        else:
            sections = []
            for d in dashboards:
                sect = {
                    'name': d['name'],
                    'dashboard-id': d['panel_id'],
                    'description': d['description']
                }
                sections.append(sect)
            tab['sections'] = sections
        tabs.append(tab)
    menu['tabs'] = tabs

    return menu


def main():
    """Thales generates a menu.yaml from the metadashabord and projectname documents stored in the
    Kibiter index. Such a menu can be processed by Pythagoras.

    Examples:
    thales https://admin:admin@localhost:6789 .kibana ./menu.yaml
    """
    args = get_params()
    menu = generate(args.elasticsearch_url, args.kibiter_index)
    save_yaml(menu, args.top_menu_path)


if __name__ == "__main__":
    main()
