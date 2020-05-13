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

from archimedes.archimedes import Archimedes, logger


DASHBOARD_TITLE2ID = {
    "About": "About",
    "Affiliations": "Affiliations",
    "Apache": "Apache",
    "Askbot": "Askbot",
    "Bugzilla": "Bugzilla",
    "Bugzilla Backlog": "Bugzilla-Backlog",
    "Bugzilla Timing": "Bugzilla-Timing",
    "Code Complexity": "9a00bc60-9900-11e9-82c4-37956b0c932a",
    "Code License": "07dadc50-9c19-11e9-82c4-37956b0c932a",
    "Community Structure by Organization": "Community-Structure-by-Organization",
    "Community Structure by Project": "Community-Structure-by-Project",
    "Confluence": "Confluence",
    "Contributors Growth": "4434c9a0-18dd-11e9-ba47-d5cbef43f8d3",
    "Data Status": "Data-Status",
    "Demographics": "15e4b020-d075-11e8-8aac-ef7fd4d8cbad",
    "Discourse": "Discourse",
    "Docker": "1fe57070-4f11-11ea-ac47-d59b2800ffe6",
    "DockerHub": "DockerHub",
    "Efficiency: Timing overview": "69208f40-18cb-11e9-ba47-d5cbef43f8d3",
    "Emerging Tech Adoption": "EmTech-Adoption",
    "Emerging Tech Dev": "EmTech-Dev",
    "Emerging Tech Social": "EmTech-Social",
    "EmTech Community Structure": "EmTech-Community-Structure",
    "Engagement": "b7b169e0-14e3-11e9-8aac-ef7fd4d8cbad",
    "Functest": "Functest",
    "Gerrit": "Gerrit",
    "Gerrit Approvals": "95487340-6762-11e9-a198-67126215b112",
    "Gerrit Backlog": "Gerrit-Backlog",
    "Gerrit Efficiency": "8c515590-e1de-11e8-8aac-ef7fd4d8cbad",
    "Gerrit Timing": "Gerrit-Timing",
    "Git": "Git",
    "Git Areas of Code": "Git-Areas-of-Code",
    "Git Demographics": "Git-Demographics",
    "Git Pair Programming": "Git-Pair-Programming",
    "GitHub Development Activity Overview": "3f4bf390-b29a-11e8-bbe5-d99a6d067cbc",
    "GitHub Events - ClosedEvent": "b702de50-83b1-11ea-b68b-31a1aa44b23a",
    "GitHub External Contributions": "2f1be220-dbb9-11e9-8bb5-a754934c91d5",
    "GitHub Issues": "GitHub-Issues",
    "GitHub Issues Backlog": "GitHub-Issues-Backlog",
    "GitHub Issues Comments and Collaboration": "4b6cdf80-33cd-11ea-b68b-31a1aa44b23a",
    "GitHub Issues Comments and Collaboration (with feelings)": "a3aa38c0-4f19-11ea-ac47-d59b2800ffe6",
    "GitHub Issues Efficiency": "c3da5c20-e1c3-11e8-8aac-ef7fd4d8cbad",
    "GitHub Issues Timing": "GitHub-Issues-Timing",
    "GitHub Pull Requests": "GitHub-Pull-Requests",
    "GitHub Pull Requests Backlog": "GitHub-Pull-Requests-Backlog",
    "GitHub Pull Requests Comments and Collaboration": "bcb51ca0-3870-11ea-b68b-31a1aa44b23a",
    "GitHub Pull Requests Efficiency": "9663d5a0-e1dc-11e8-8aac-ef7fd4d8cbad",
    "GitHub Pull Requests Timing": "GitHub-Pull-Requests-Timing",
    "GitHub Repositories": "8035e0c0-45e6-11e9-b68b-31a1aa44b23a",
    "GitLab Issues": "2e968fe0-b1bb-11e8-8aac-ef7fd4d8cbad",
    "Gitlab Issues Backlog": "5e03cfb0-b4f7-11e8-8aac-ef7fd4d8cbad",
    "GitLab Issues Efficiency": "38fe7980-f6f2-11e8-8aac-ef7fd4d8cbad",
    "GitLab Issues Timing": "5a542570-b508-11e8-8aac-ef7fd4d8cbad",
    "GitLab Merge Requests": "b2218fd0-bc11-11e8-8aac-ef7fd4d8cbad",
    "GitLab Merge Requests Backlog": "078d8780-bcad-11e8-8aac-ef7fd4d8cbad",
    "GitLab Merge Requests Efficiency": "bff9e0c0-fe16-11e8-8aac-ef7fd4d8cbad",
    "GitLab Merge Requests Timing": "3eae8110-bc1c-11e8-8aac-ef7fd4d8cbad",
    "Gitter": "Gitter",
    "Google Hits": "Google-Hits",
    "IRC": "IRC",
    "Jenkins": "Jenkins",
    "Jenkins Export (Slow)": "Jenkins-Export-(Slow)",
    "Jenkins Job Categories": "5c707260-2a0f-11e9-b1b8-f3720d7eacea",
    "Jenkins Jobs": "00862e30-bbf7-11e8-8aac-ef7fd4d8cbad",
    "Jenkins Nodes": "a41a9940-bcb1-11e8-8aac-ef7fd4d8cbad",
    "Jira": "Jira",
    "Jira Backlog": "Jira-Backlog",
    "Jira Effort": "Jira-Effort",
    "Jira Timing": "Jira-Timing",
    "KIP": "KIP",
    "Lifecycle": "999ea330-f7b2-11e8-865a-85ff6467a442",
    "Lines of Code Changed": "f13af0e0-18e5-11e9-ba47-d5cbef43f8d3",
    "Mailing Lists": "MailingLists",
    "Maintainer Response to Merge Request Duration": "206c9180-1d86-11e9-ba47-d5cbef43f8d3",
    "Maniphest": "Maniphest",
    "Maniphest Backlog": "Maniphest-Backlog",
    "Maniphest Timing": "Maniphest-Timing",
    "Mattermost": "Mattermost",
    "Mediawiki": "Mediawiki",
    "Meetup": "Meetup",
    "Meetup Locations": "Meetup-Locations",
    "Mozilla Club": "Mozilla-Club",
    "Organization Tracking Overview": "2b7c68b0-472f-11ea-97d2-0103fac622e1",
    "Organizational Diversity": "ab68fe20-17f2-11e9-872f-e17019e68d6d",
    "Organizational Diversity by Domains": "6e0e2900-18c0-11e9-872f-e17019e68d6d",
    "Overall Community Structure": "Overall-Community-Structure",
    "Overview": "Overview",
    "Pull Request Merge Duration": "00fa7e30-1b0a-11e9-ba47-d5cbef43f8d3",
    "Pull Requests Merged": "a7b3fd70-ef16-11e8-9be6-c962f0cee9ae",
    "Redmine": "Redmine",
    "Redmine Backlog": "Redmine-Backlog",
    "Redmine Timing": "Redmine-Timing",
    "Reps Activities": "Reps-Activities",
    "Reps Events": "Reps-Events",
    "RSS": "RSS",
    "Slack": "Slack",
    "StackOverflow": "Stackoverflow",
    "Telegram": "Telegram",
    "Testing": "Testing",
    "Twitter": "Twitter"
}


def import_batch(archimedes, dashboards, by='id', force=False, find=False):
    for title in dashboards:
        dashboard_id = dashboards[title]
        logger.info("Importing dashboard %s" % title)
        try:
            if by == 'id':
                archimedes.import_from_disk(obj_type="dashboard", obj_id=dashboard_id, force=force, find=find)
            else:
                archimedes.import_from_disk(obj_type="dashboard", obj_title=title, force=force, find=find)
        except Exception as ex:
            logger.error("Impossible to import dashboard %s, skipping it. %s" % (dashboard_id, ex))
            continue


def export_batch(archimedes, dashboards, by='id', force=False):
    for title in dashboards:
        dashboard_id = dashboards[title]
        logger.info("Exporting dashboard %s" % title)
        try:
            if by == 'id':
                archimedes.export_to_disk(obj_type="dashboard", obj_id=dashboard_id, force=force)
            else:
                archimedes.export_to_disk(obj_type="dashboard", obj_title=title, force=force)
        except Exception as ex:
            logger.error("Impossible to import dashboard %s, skipping it. %s" % (dashboard_id, ex))
            continue


def get_params():
    parser = argparse.ArgumentParser(usage="usage: Euclid [options]", description="Import/Export Kibana dashboards")

    parser.add_argument('url', help='Kibana URL')
    parser.add_argument('root_path', help='Archimedes folder')
    parser.add_argument('--search-by', dest='search_by',
                        help='Search dashboards by title or ID', choices=['id', 'title'], default='id')
    parser.add_argument('--dashboards', dest='dashboards',
                        help='A dict with a set of dashboards title and id to import', default=None)
    parser.add_argument('--import-all', action='store_true')
    parser.add_argument('--export-all', action='store_true')

    args = parser.parse_args()

    return args


def main():
    """Euclid helps Archimedes to import/export a set of dashboards. They can be passed as a
    JSON file with the following format `{"dashbord_title-1": "dashboard_id-1", "dashbord_title-2": "dashboard_id-2"}`.
    If the file isn't defined the dashboards are initialized with the value of DASHBOARD_TITLE2ID.

    A common execution consists of running the export, and the export.

    Examples:
    - Import all dashbaords from a local Archimedes repo to a Kibana instance
        ./bin/utils http://admin:admin@localhost:5601 /home/dashboards --import-all --search-by title
    - Export all dashboards from a Kibana instance to a local Archimedes repo
        ./bin/utils http://admin:admin@localhost:5601 /home/dashboards --export-all --dashboards dashboards.json
    """
    args = get_params()

    if (args.import_all and args.export_all) or (not args.import_all and not args.export_all):
        print("One action is needed: select --import-all or --export-all")
        return

    archimedes = Archimedes(args.url, args.root_path)
    search_by = args.search_by
    if args.dashboards:
        with open(args.dashboards, 'r') as f:
            dashboards = json.loads(f.read())
    else:
        dashboards = DASHBOARD_TITLE2ID

    if args.import_all:
        import_batch(archimedes, dashboards, by=search_by, force=True, find=True)

    if args.export_all:
        export_batch(archimedes, dashboards, by=search_by, force=True)


if __name__ == "__main__":
    main()
