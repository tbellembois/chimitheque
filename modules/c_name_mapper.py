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
# $Id: c_name_mapper.py 195 2015-02-25 09:51:08Z tbellemb $
#
from chimitheque_logger import chimitheque_logger
from c_name import NAME
from gluon import current

my_logger = chimitheque_logger()


class NAME_MAPPER(object):
    """Database name table mapper.

    Request the database to create ENTITY instances.
    """
    def __init__(self):
        pass

    def __name_from_row(self, name_row):
        """Return a NAME instance from a Row"""
        return NAME(id=name_row['id'],
                    label=name_row['label'])

    def find(self, name_id):
        """Select a name in the database.

        name_id -- the name id to select
        returns: a NAME
        """
        my_logger.debug(message='name_id:%s' % name_id)

        _name_row = current.db(current.db.name.id == name_id).select().first()
        my_logger.debug(message='_name_row:%s' % _name_row)

        if _name_row is not None:
            return self.__name_from_row(_name_row)
        else:
            return None
