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
# $Id: c_store_location.py 196 2015-02-26 15:32:18Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class STORE_LOCATION:
    """Define an store location.

    A store location belongs to one entity.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__name = kwargs.get('name')
        self.__full_path = kwargs.get('full_path')
        self.__can_store = kwargs.get('can_store')
        self.__color = kwargs.get('color')
        self.__entity = kwargs.get('entity')  # lambda - returns an ENTITY
        self.__parent = kwargs.get('parent')  # lambda - returns a STORE_LOCATION

        self.__compute_nb_storage_card = kwargs.get('compute_nb_storage_card')  # lambda - returns a int
        self.__compute_nb_archived_storage_card = kwargs.get('compute_nb_archived_storage_card')  # lambda - returns a int
        self.__compute_nb_children = kwargs.get('compute_nb_children')  # lambda - returns a int
        self.__retrieve_parents = kwargs.get('retrieve_parents')  # lambda - returns a [ STORE_LOCATION ]
        self.__retrieve_children = kwargs.get('retrieve_children')  # lambda - returns a [ STORE_LOCATION ]
        self.__has_parent = kwargs.get('has_parent')  # lambda - returns a boolean
        self.__has_storage = kwargs.get('has_storage')  # lambda - returns a boolean

    def __repr__(self):
        return '<STORE_LOCATION:%s:%s-parent_id:%s>' % (self.id, self.name, self.parent.id)

    def __eq__(self, other):
        my_logger.debug(message='type(self):%s' % type(self))
        my_logger.debug(message='type(other):%s' % type(other))
        if self is None or other is None:
            return False
        else:
            return self.name == other.name

    #
    # attributes
    #
    @property
    def id(self):
        """Return the store location id."""
        return self.__id

    @property
    def name(self):
        """Return the store location name."""
        return self.__name

    @property
    def full_path(self):
        """Return the store location full path."""
        return self.__full_path

    @property
    def can_store(self):
        """Return True if the store location can have storages."""
        return self.__can_store

    @property
    def color(self):
        """Return the store location color."""
        return self.__color

    @property
    def entity(self):
        """Return the store location entity."""
        return self.__entity()

    @property
    def parent(self):
        """Return the store location first parent."""
        return self.__parent()

    #
    # methods
    #
    def compute_and_set_full_path(self):
        """Compute and set the full_path property of the store location."""
        my_logger.debug(message='compute_and_set_full_path')

        _full_path = ''

        if self.has_parent():

            my_logger.debug(message='has_parent')
 
            for _parent in self.retrieve_parents():
                my_logger.debug(message='_parent:%s' % _parent)
                _full_path = _full_path + _parent.name + ' / ' \
                             if _parent is not None \
                             else _full_path

        _full_path = _full_path + self.name
        my_logger.debug(message='_full_path:%s' % _full_path)

        self.full_path = _full_path

    def compute_nb_storage_card(self):
        """Return the number of storage cards of the store location."""
        return self.__compute_nb_storage_card()

    def compute_nb_archived_storage_card(self):
        """Return the number of archived storage cards of the store location."""
        return self.__compute_nb_archived_storage_card()

    def compute_nb_children(self):
        """Return the number children of the store location."""
        return self.__compute_nb_children()

    def retrieve_parents(self):
        """Return the store locations parents.

        returns: a list of STORE_LOCATION
        """
        # the mapper lambda funtion returns the current store location
        # we have to remove it
        return reversed(self.__retrieve_parents()[1:])

    def retrieve_children(self):
        """Return the store locations children.

        returns: a list of STORE_LOCATION
        """
        return self.__retrieve_children()

    def has_parent(self):
        """Return True if the store location has a parent."""
        return self.__has_parent() if self.__has_parent is not None else False

    def has_storage(self, product_id=None, archive=False):
        """Return True if the store location has storages."""
        return self.__has_storage(product_id=product_id, archive=archive) if self.__has_storage is not None else False


