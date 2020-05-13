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
import json
import requests
import yaml

from archimedes.archimedes import Archimedes, logger
from archimedes.clients.dashboard import DASHBOARD
from grimoirelab_toolkit.uris import urijoin


METADASHBOARD = 'metadashboard'
PROJECTNAME = 'projectname'
CONTENT_TYPE_HEADER = {"Content-Type": "application/json"}


def get_params():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('kibana_url', help='Kibana URL')
    parser.add_argument('archimedes_root_path', help='Archimedes folder')
    parser.add_argument('top_menu_path', help='Top menu yaml file')
    parser.add_argument('--kibiter-index', dest='kibiter_index', help='Kibiter index', default='.kibiter')
    parser.add_argument('--project-name', dest='project_name', help='Project name', default=None)
    parser.add_argument('--elasticsearch-url', dest='elasticsearch_url', help='ElasticSearch URL', default=None)
    parser.add_argument('--import-dashboards', dest='import_dashboards', action='store_true', help='Import dashboards')
    parser.add_argument('--set-top-menu', dest='set_top_menu', action='store_true', help='Set top menu')
    parser.add_argument('--set-project-name', dest='set_project_name', action='store_true', help='Set project name')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='Overwrite existing Kibana obj')

    args = parser.parse_args()

    if args.set_project_name and not args.project_name:
        logger.error("Project name not declared")
        return

    if args.set_top_menu and not args.elasticsearch_url:
        logger.error("ElasticSearch URL not declared")
        return

    if not args.import_dashboards and not args.set_top_menu and not args.set_project_name:
        logger.error("Set at least one of --import-dashboards, --set-project-name, --set-top-menu")

    return args


def load_yaml(file_path):
    with open(file_path, 'r') as f:
        try:
            menu = yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.YAMLError as ex:
            logger.error(ex)
            return

    return menu


def set_kibiter_endpoint(elasticsearch_url, kibiter_index, endpoint, data):
    endpoint_url = urijoin(elasticsearch_url, kibiter_index, 'doc', endpoint)
    response = requests.put(endpoint_url, data=json.dumps(data), headers=CONTENT_TYPE_HEADER, verify=False)
    try:
        response.raise_for_status()
    except Exception as ex:
        logger.error("%s not set: %s" % (endpoint, ex))
    logger.info("%s successfully set" % endpoint)


def upload(kibana_url, kibiter_index, elasticsearch_url, archimedes_path, menu_yaml,
           import_dashboards=False, overwrite=False, set_top_menu=False,
           project_name=None, set_project_name=False):
    menu = load_yaml(menu_yaml)
    archimedes = Archimedes(kibana_url, archimedes_path)

    top_menu = []
    for tab in menu['tabs']:
        dashboard = tab.get('dashboard', None)
        if dashboard:
            if import_dashboards:
                archimedes.import_from_disk(obj_type=DASHBOARD, obj_title=dashboard, find=True, force=overwrite)
            obj = archimedes.kibana.find_by_title(obj_type=DASHBOARD, obj_title=dashboard)
            entry = {
                'title': tab['tab'],
                'name': tab['tab'],
                'description': '',
                'type': 'entry',
                'panel_id': obj['id']
            }
            top_menu.append(entry)
        else:
            sections = tab.get('sections', [])
            sub_menu = {
                'title': tab['tab'],
                'type': 'menu',
                'name': tab['tab'],
                'description': ''
            }
            dashboards = []
            for sect in sections:
                dashboard = sect.get('dashboard', None)
                if dashboard:
                    if import_dashboards:
                        archimedes.import_from_disk(obj_type=DASHBOARD, obj_title=dashboard, find=True, force=overwrite)
                    obj = archimedes.kibana.find_by_title(obj_type=DASHBOARD, obj_title=dashboard)
                    entry = {
                        'title': sect['name'],
                        'name': sect['name'],
                        'description': '',
                        'type': 'entry',
                        'panel_id': obj['id']
                    }
                    dashboards.append(entry)
            sub_menu['dashboards'] = dashboards
            top_menu.append(sub_menu)

    if set_top_menu:
        set_kibiter_endpoint(elasticsearch_url, kibiter_index, METADASHBOARD, {"metadashboard": top_menu})

    if set_project_name:
        set_kibiter_endpoint(elasticsearch_url, kibiter_index, PROJECTNAME, {"projectname": {"name": project_name}})


def main():
    """Pythagoras helps Archimedes to import dashboards (overwriting the existing ones if needed) based on
    the top menu passed as input. Furthermore, it also helps to set the top menu and project name in Kibiter.

    Examples:
    pythagoras http://admin:admin@localhost:7890 /tmp/archimedes_folder ./menu.yaml
    --elasticsearch-url https://admin:admin@localhost:6789
    --project-name Test
    --set-project-name
    --set-top-menu
    --import-dashboards
    --kibiter-index .kibana_1
    --overwrite
    """
    args = get_params()
    upload(args.kibana_url, args.kibiter_index, args.elasticsearch_url, args.archimedes_root_path,
           args.top_menu_path, args.import_dashboards, args.overwrite, args.set_top_menu,
           args.project_name, args.set_project_name)


if __name__ == "__main__":
    main()
