# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
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
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosenntino <valcos@bitergia.com>
#


class BaseError(Exception):
    """Base class for Archimedes exceptions.

    Derived classes can overwrite the error message declaring ``message``
    property.
    """
    message = 'Archimedes base error'

    def __init__(self, **kwargs):
        super().__init__()
        self.msg = self.message % kwargs

    def __str__(self):
        return self.msg


class ImportError(BaseError):
    """Error for handling import errors"""

    message = "%(cause)s"


class FileTypeError(BaseError):
    """Error for handling unknown file types"""

    message = "%(cause)s"


class ExportError(BaseError):
    """Error for handling export errors"""

    message = "%(cause)s"


class NotFoundError(BaseError):
    """Error for handling not found errors"""

    message = "%(cause)s"


class ObjectTypeError(BaseError):
    """Error for handling unknown object types"""

    message = "%(cause)s"


class RegistryError(BaseError):
    """Error for handling registry errors"""

    message = "%(cause)s"
