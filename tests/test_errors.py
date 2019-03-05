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

import unittest

import archimedes.errors as errors


# Mock classes to test BaseError class
class MockErrorNoArgs(errors.BaseError):
    message = "Mock error without args"


class MockErrorArgs(errors.BaseError):
    message = "Mock error with args. Error: %(code)s %(msg)s"


class TestBaseError(unittest.TestCase):

    def test_subclass_with_no_args(self):
        """Check subclasses that do not require arguments.

        Arguments passed to the constructor should be ignored.
        """
        e = MockErrorNoArgs(code=1, msg='Fatal error')

        self.assertEqual("Mock error without args", str(e))

    def test_subclass_args(self):
        """Check subclasses that require arguments"""

        e = MockErrorArgs(code=1, msg='Fatal error')

        self.assertEqual("Mock error with args. Error: 1 Fatal error",
                         str(e))

    def test_subclass_invalid_args(self):
        """Check when required arguments are not given.

        When this happens, it raises a KeyError exception.
        """
        kwargs = {'code': 1, 'error': 'Fatal error'}
        self.assertRaises(KeyError, MockErrorArgs, **kwargs)


class TestImportError(unittest.TestCase):

    def test_message(self):
        """Test ImportError message"""

        e = errors.ImportError(cause='something went wrong during Import')
        self.assertEqual('something went wrong during Import', str(e))


class TestExportError(unittest.TestCase):

    def test_message(self):
        """Test ExportError message"""

        e = errors.ExportError(cause='something went wrong during Export')
        self.assertEqual('something went wrong during Export', str(e))


class TestFileTypeError(unittest.TestCase):

    def test_message(self):
        """Test FileTypeError message"""

        e = errors.FileTypeError(cause='file type not recognized')
        self.assertEqual('file type not recognized', str(e))


class TestObjectTypeError(unittest.TestCase):

    def test_message(self):
        """Test ObjectTypeError message"""

        e = errors.ObjectTypeError(cause='object type not recognized')
        self.assertEqual('object type not recognized', str(e))


class TestNotFoundError(unittest.TestCase):

    def test_message(self):
        """Test NotFoundError message"""

        e = errors.NotFoundError(cause='object not found')
        self.assertEqual('object not found', str(e))


class TestRegistryError(unittest.TestCase):

    def test_message(self):
        """Test RegistryError message"""

        e = errors.RegistryError(cause='error on registry')
        self.assertEqual('error on registry', str(e))


if __name__ == "__main__":
    unittest.main(warnings='ignore')
