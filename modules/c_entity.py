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
# $Id: c_entity.py 196 2015-02-26 15:32:18Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class ENTITY:
    """Define an entity.

    A user belongs to one or several entities.
    An entity has one or several store_locations.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__name = kwargs.get('name')
        self.__description = kwargs.get('description')
        self.__manager = kwargs.get('manager')  # lambda that returns a [ PERSON ]

        self.__compute_nb_store_location = kwargs.get('compute_nb_store_location')  # lambda that returns a int
        self.__compute_nb_storage_card = kwargs.get('compute_nb_storage_card')  # lambda that returns a int
        self.__compute_nb_archived_storage_card = kwargs.get('compute_nb_archived_storage_card')  # lambda that returns a int
        self.__compute_nb_user = kwargs.get('compute_nb_user')  # lambda that returns a int
        self.__retrieve_users = kwargs.get('retrieve_users')  # lambda that returns a [ PERSON ]
        self.__retrieve_store_locations = kwargs.get('retrieve_store_locations')  # lambda that returns a [ STORE_LOCATION ]
        self.__count_all = kwargs.get('count_all')

    def __repr__(self):
        return '<ENTITY:%s:%s>' % (self.id, self.name)

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return self.name == other.name

    #
    # attributes
    #
    @property
    def id(self):
        """Return the entity id."""
        return self.__id

    # alias for role
    @property
    def name(self):
        """Alias that return the entity role."""
        return self.__name

    @property
    def role(self):
        """Return the entity role."""
        return self.__name

    @property
    def description(self):
        """Return the entity description."""
        return self.__description

    @property
    def manager(self):
        """Return the entity manager(s).

        returns: a list of PERSON
        """
        return self.__manager()

    #
    # methods
    #
    def compute_nb_storage_card(self):
        """Return the number of storage cards of the entity."""
        return self.__compute_nb_storage_card()

    def compute_nb_archived_storage_card(self):
        """Return the number of archived storage cards of the entity."""
        return self.__compute_nb_archived_storage_card()

    def compute_nb_store_location(self):
        """Return the number of store locations of the entity."""
        return self.__compute_nb_store_location()

    def compute_nb_user(self):
        """Return the number of users of the entity."""
        return self.__compute_nb_user()

    def retrieve_store_locations(self):
        """Return the store locations of the entity as a list.

        returns: a list of STORE_LOCATION
        """
        return self.__retrieve_store_locations()

    def retrieve_users(self):
        """Return the users of the entity as a list.

        returns: a list of PERSON
        """
        return self.__retrieve_users()

    def count_all(self):
        """Return the number of entities."""
        return self.__count_all()
