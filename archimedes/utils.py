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
import logging
import os


def load_json(file_path):
    """Load JSON content from file.

    :param file_path: the path of a JSON file

    :returns: JSON content
    """
    with open(file_path, 'r') as f:
        content = f.read()

    json_content = json.loads(content)
    return json_content


def save_to_file(json_content, dest_path, force=False):
    """Save JSON content to a `dest_path`.

    :param json_content: the JSON content to be saved
    :param dest_path: the destination path
    :param force: overwrite an existing file on file name conflict
    """
    content = json.dumps(json_content, sort_keys=True, indent=4)

    if os.path.exists(dest_path) and not force:
        logging.warning("File %s already exists, it won't be overwritten", dest_path)
        return

    with open(dest_path, "w+") as f:
        f.write(content)
        logging.info("File %s saved", dest_path)


def find_file(folder_path, target_name):
    """Find a file with `target_name` in a `folder_path`. The method
    raises a `FileNotFoundError` in case the file is not found.

    :param folder_path: the folder where to look for the file
    :param target_name: the name of the target file

    :returns: the file path of the file
    """
    files = os.listdir(folder_path)
    found = None
    for name in files:
        if target_name == name:
            found = os.path.join(folder_path, target_name)
            break

    if not found:
        logging.error("File %s not found in %s", target_name, folder_path)
        raise FileNotFoundError

    return found
