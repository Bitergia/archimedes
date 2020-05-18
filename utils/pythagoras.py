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
from archimedes.clients.saved_objects import SavedObjects
from grimoirelab_toolkit.uris import urijoin


METADASHBOARD = 'metadashboard'
PROJECTNAME = 'projectname'
CONTENT_TYPE_HEADER = {"Content-Type": "application/json"}


def get_params():
    parser = argparse.ArgumentParser(usage="usage: Pythagoras [options]",
                                     description="Import dashboards and set metadashboard, projectname and config")

    parser.add_argument('kibiter_url', help='Kibana URL')
    parser.add_argument('archimedes_root_path', help='Archimedes folder')
    parser.add_argument('top_menu_path', help='Top menu yaml file')
    parser.add_argument('--kibiter-index', dest='kibiter_index', help='Kibiter index', default='.kibiter')
    parser.add_argument('--kibiter-time-from', dest='kibiter_time_from', help='Kibiter time from', default='now-90d')
    parser.add_argument('--kibiter-index-pattern', dest='kibiter_index_pattern', help='Kibiter index pattern', default='git')
    parser.add_argument('--kibiter-version', dest='kibiter_version', help='Kibiter version', default='6.8.6')
    parser.add_argument('--elasticsearch-url', dest='elasticsearch_url', help='ElasticSearch URL', default=None)
    parser.add_argument('--import-dashboards', dest='import_dashboards', action='store_true', help='Import dashboards')
    parser.add_argument('--set-top-menu', dest='set_top_menu', action='store_true', help='Set top menu')
    parser.add_argument('--set-project-name', dest='set_project_name', action='store_true', help='Set project name')
    parser.add_argument('--set-config', dest='set_config', action='store_true', help='Set the Kibiter conf')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='Overwrite existing Kibana obj')

    args = parser.parse_args()

    if args.set_top_menu and not args.elasticsearch_url:
        logger.error("ElasticSearch URL not declared")
        return

    return args


def load_yaml(file_path):
    """Load the YAML file containing the top menu and returns its content

    :param file_path: path of the YAML file
    """
    with open(file_path, 'r') as f:
        try:
            menu = yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.YAMLError as ex:
            logger.error(ex)
            return

    logger.info("%s loaded" % file_path)
    return menu


def set_kibiter_config(kibiter_url, kibiter_time_from='now-90d', kibiter_index_pattern='git', kibiter_version='6.8.6',
                       overwrite=True):
    """Set the configuration of the Kibiter instance via the Kibana API

    :param kibiter_url: Kibiter URL
    :param kibiter_time_from: The value of the time picker
    :param kibiter_index_pattern: The value of the default index pattern
    :param kibiter_version: The value of the Kibiter version
    :param overwrite: If True, force the overwrite of existing dashboards
    """
    attributes = {}
    time_picker = {"from": kibiter_time_from, "to": "now", "mode": "quick"}
    attributes["timepicker:timeDefaults"] = json.dumps(time_picker)
    attributes["defaultIndex"] = kibiter_index_pattern

    saved_objects = SavedObjects(kibiter_url)
    saved_objects.create_object('config', kibiter_version, attributes, overwrite=overwrite)


def set_kibiter_endpoint(elasticsearch_url, kibiter_index, endpoint, data):
    """Set a target Kibiter endpoint

    :param elasticsearch_url: URL of elasticsearch DB
    :param kibiter_index: name of the target index
    :param endpoint: the Kibiter-related endpoint (`metadashbord` or `projectname`)
    :param data: the content to be uploaded
    """
    endpoint_url = urijoin(elasticsearch_url, kibiter_index, 'doc', endpoint)
    response = requests.put(endpoint_url, data=json.dumps(data), headers=CONTENT_TYPE_HEADER, verify=False)
    try:
        response.raise_for_status()
        logger.info("%s successfully set" % endpoint)
    except Exception as ex:
        logger.error("%s not set: %s" % (endpoint, ex))


def import_dashboard(archimedes, dash_id, dash_title, overwrite):
    """Import a dashboard by its ID or title

    :param archimedes: Archimedes object
    :param dash_id: Dashboard ID
    :param dash_title: Dashboard title
    :param overwrite: If True, force the overwrite of an existing dashboard
    """
    if dash_id:
        logger.info("Importing dashboard %s" % dash_id)
        archimedes.import_from_disk(obj_type=DASHBOARD, obj_id=dash_id, find=True, force=overwrite)
    elif dash_title:
        logger.info("Importing dashboard %s" % dash_title)
        archimedes.import_from_disk(obj_type=DASHBOARD, obj_title=dash_title, find=True, force=overwrite)


def find_dashboard(archimedes, dash_id, dash_title):
    """Find a dashboard by its ID or title and return the Kibana object

    :param archimedes: Archimedes object
    :param dash_id: Dashboard ID
    :param dash_title: Dashboard title

    :return the Kibana dashboard obj
    """
    obj = None
    if dash_id:
        obj = archimedes.kibana.find_by_id(obj_type=DASHBOARD, obj_id=dash_id)
    elif dash_title:
        obj = archimedes.kibana.find_by_title(obj_type=DASHBOARD, obj_title=dash_title)

    return obj


def create_metadashboard_entry(panel_id, entry_title, menu_attr, descr):
    """Create an entry for the Kibiter metadashboard

    :param panel_id: panel id (it can be a URL or a dashboard ID
    :param entry_title: entry title
    :param menu_attr: attribute defined in the YAML file to be set as the name of the entry
    :param descr: description for the entry

    :return: a dict representing the entry in the metadashboard
    """
    entry = {
        'title': entry_title,
        'name': menu_attr,
        'description': descr,
        'type': 'entry',
        'panel_id': panel_id
    }

    return entry


def upload_dashboards(kibiter_url, archimedes_path, menu_yaml, import_dashboards=False, overwrite=False):
    """Upload the dashboards to a target Kibana instance.

    :param kibiter_url: Kibiter URL
    :param archimedes_path: Root path of the Archimedes folder
    :param menu_yaml: YAML containing the structure of the top menu
    :param import_dashboards: If True, import the dashboards defined in `menu_yaml`
    :param overwrite: If True, force the overwrite of existing dashboards

    :returns a dict including the project name and the metadashboard info (the list of dashboards in the menu_yaml)
    """
    menu = load_yaml(menu_yaml)
    archimedes = Archimedes(kibiter_url, archimedes_path)

    project_name = menu['project']
    top_menu = []
    for tab in menu['tabs']:
        dashboard_title = tab.get('dashboard-title', None)
        dashboard_id = tab.get('dashboard-id', None)
        descr = tab.get('description', '')
        if dashboard_title or dashboard_id:
            if import_dashboards:
                import_dashboard(archimedes, dashboard_id, dashboard_title, overwrite)
            obj = find_dashboard(archimedes, dashboard_id, dashboard_title)
            entry_title = obj['attributes'].get('title', '')
            panel_id = obj['id']
            entry = create_metadashboard_entry(panel_id, entry_title, tab['tab'], descr)
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
                dashboard_title = sect.get('dashboard-title', None)
                dashboard_id = sect.get('dashboard-id', None)
                descr = sect.get('description', '')

                if sect['name'] == 'Contact' and 'https' in dashboard_id:
                    entry = create_metadashboard_entry(dashboard_id, '', sect['name'], descr)
                    dashboards.append(entry)
                else:
                    if dashboard_title or dashboard_id:
                        if import_dashboards:
                            import_dashboard(archimedes, dashboard_id, dashboard_title, overwrite)
                        obj = find_dashboard(archimedes, dashboard_id, dashboard_title)
                        entry_title = obj['attributes'].get('title', '')
                        dashboard_id = obj['id']
                        entry = create_metadashboard_entry(dashboard_id, entry_title, sect['name'], descr)
                        dashboards.append(entry)
            sub_menu['dashboards'] = dashboards
            top_menu.append(sub_menu)

    return {
        'projectname': project_name,
        'metadashboard': top_menu
    }


def main():
    """Pythagoras helps Archimedes to import dashboards (overwriting the existing ones if
    needed) based on the top menu passed as input. Furthermore, it also helps to set the
    top menu, project name and config settings in Kibiter.

    Example:
    pythagoras http://admin:admin@localhost:7890 /tmp/archimedes_folder ./menu.yaml
    --elasticsearch-url https://admin:admin@localhost:6789
    --set-project-name
    --set-top-menu
    --set-config
    --import-dashboards
    --kibiter-index .kibana_1
    --overwrite
    --kibiter-index-pattern mbox

    menu.yaml
    ```
    project: Bitergia
    tabs:
    - tab: Overview
        dashboard-title: Overview
        description: "Summary of basic metrics on all analyzed sources."
    - tab: Git
      sections:
        - name: Overview
          dashboard-id: Git
        - name: Attraction/Retention
          dashboard-title: Git Demographics
        - name: Areas of Code
          dashboard-title: Git Areas of Code
        - name: Lifecycle
          dashboard-title: Lifecycle
    - tab: About
      sections:
      - name: About the dashboard
        dashboard-id: About
        description: Panel with information about the usage of the interface, an information
          about the panel itself and acknowledgments
      - name: Contact
        dashboard-id: https://gitlab.com/Bitergia/c/CHAOSS/support
        description: Direct link to the support repository
    ```
    """
    args = get_params()
    menu_json = upload_dashboards(args.kibiter_url, args.archimedes_root_path, args.top_menu_path,
                                  args.import_dashboards, args.overwrite)

    if args.set_top_menu:
        metadashboard = menu_json['metadashboard']
        set_kibiter_endpoint(args.elasticsearch_url, args.kibiter_index,
                             METADASHBOARD, {"metadashboard": metadashboard})

    if args.set_project_name:
        projectname = menu_json['projectname']
        set_kibiter_endpoint(args.elasticsearch_url, args.kibiter_index, PROJECTNAME, {"projectname": projectname})

    if args.set_config:
        set_kibiter_config(args.kibiter_url, args.kibiter_time_from, args.kibiter_index_pattern, args.kibiter_version,
                           args.overwrite)


if __name__ == "__main__":
    main()
