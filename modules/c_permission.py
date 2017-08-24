# -*- coding: utf-8; -*-
#
# (c) 2011-2015 Thomas Bellembois thomas.bellembois@ens-lyon.fr
#
# This file is part of Chimithèque.
#
# Chimithèque is free software; you can redistribute it and/or modify
# it under the terms of the Cecill as published by the CEA, CNRS and INRIA
# either version 2 of the License, or (at your option) any later version.
#
# Chimithèque is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Cecill along with Chimithèque.
# If not, see <http://www.cecill.info/licences/>.
#
# SVN Revision:
# -------------
# $Id: c_permission.py 195 2015-02-25 09:51:08Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class PERMISSION:
    """Define a permission.

    Permissions are given per user.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__name = kwargs.get('name')

    def __repr__(self):
        return '<PERMISSION:%s>' % self.name

    def __eq__(self, other):
        my_logger.debug(message='self:%s' % self)
        my_logger.debug(message='other:%s' % other)
        if self is None or other is None:
            return False
        else:
            return self.name == other.name

    #
    # attributes
    #
    @property
    def id(self):
        """Return the permission id."""
        return self.__id

    @property
    def name(self):
        """Return the permission name."""
        return self.__name
