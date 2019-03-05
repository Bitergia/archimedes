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
import os
import unittest

from archimedes.utils import load_json


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestUtils(unittest.TestCase):

    def test_load_json(self):
        """Test whether the content of JSON is correctly loaded"""

        target_file = 'data/object_visualization'
        obj_file = read_file(target_file)

        expected = json.loads(obj_file)
        self.assertDictEqual(load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), target_file)),
                             expected)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
