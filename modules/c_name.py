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
# $Id: c_name.py 195 2015-02-25 09:51:08Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

mylogger = chimitheque_logger()


class NAME(object):
    """Define an product name or synonym.

    A product has one name and can have several synonyms.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__label = kwargs.get('label')

    def __repr__(self):
        return '<name:%s:%s>' % (self.id, self.label)

    #
    # attributes
    #
    @property
    def id(self):
        """Return the name id."""
        return self.__id

    @property
    def label(self):
        """Return the name label."""
        return self.__label
