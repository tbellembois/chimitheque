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
# $Id:
#
from chimitheque_logger import chimitheque_logger
from gluon.utils import web2py_uuid
from c_exposure_item import EXPOSURE_ITEM

my_logger = chimitheque_logger()


class EXPOSURE_CARD(object):
    """Define an exposure card.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id') if 'id' in kwargs else web2py_uuid()  # uid to debug instance creation - not commited in DB
        self.__title = kwargs.get('title')
        self.__accidental_exposure_type = kwargs.get('accidental_exposure_type')
        self.__accidental_exposure_datetime = kwargs.get('accidental_exposure_datetime')
        self.__accidental_exposure_duration_and_extent = kwargs.get('accidental_exposure_duration_and_extent')
        self.__creation_datetime = kwargs.get('creation_datetime')
        self.__modification_datetime = kwargs.get('modification_datetime')
        self.__archive = kwargs.get('archive') if 'archive' in kwargs else False  # boolean
        self.__exposure_items = kwargs.get('exposure_items') if 'exposure_items' in kwargs else []  # [EXPOSURE_ITEM] type

    def __repr__(self):
        return '<EXPOSURE_CARD:%s:%s archive:%s>' % (self.title, self.id, self.archive) + str(self.exposure_items)

    @property
    def title(self):
        """Return the exposure card title."""
        return self.__title

    @title.setter
    def title(self, value):
        """Set the exposure card title."""
        self.__title = value

    @property
    def id(self):
        """Return the exposure card id."""
        return self.__id

    @property
    def creation_datetime(self):
        """Return the exposure card creation datetime."""
        return self.__creation_datetime

    @property
    def modification_datetime(self):
        """Return the exposure card modification datetime."""
        return self.__modification_datetime

    @property
    def archive(self):
        """Return True if the exposure card is archived."""
        return self.__archive

    @archive.setter
    def archive(self, value):
        """Set the exposure card archive."""
        self.__archive = value

    @property
    def accidental_exposure_type(self):
        """Return the exposure card accidental exposure type"""
        return self.__accidental_exposure_type

    @accidental_exposure_type.setter
    def accidental_exposure_type(self, value):
        """Set the exposure card accidental exposure type"""
        self.__accidental_exposure_type = value

    @property
    def accidental_exposure_datetime(self):
        """Return the exposure card accidental exposure datetime"""
        return self.__accidental_exposure_datetime

    @accidental_exposure_datetime.setter
    def accidental_exposure_datetime(self, value):
        """Set the exposure card accidental exposure datetime"""
        self.__accidental_exposure_datetime = value

    @property
    def accidental_exposure_duration_and_extent(self):
        """Return the exposure card accidental exposure duration and extent"""
        return self.__accidental_exposure_duration_and_extent

    @accidental_exposure_duration_and_extent.setter
    def accidental_exposure_duration_and_extent(self, value):
        """Set the exposure card accidental exposure duration_and_extent"""
        self.__accidental_exposure_duration_and_extent = value

    @property
    def exposure_items(self):
        """Return the exposure card exposure item list."""
        try:
            return self.__exposure_items()
        except TypeError:
            return self.__exposure_items

    @exposure_items.setter
    def exposure_items(self, value):
        """Set the exposure_items"""
        self.__exposure_items = value

    #
    # methods
    #
    def has_product(self, product):
        """Wrapper for the get_exposure_item_for_product method.
        """
        return self.get_exposure_item_for_product(product) is not None

    def get_exposure_item_for_product(self, product):
        """Return the exposure item for the given product or None
        if no product are found.

        product -- the product to search
        """
        for item in self.exposure_items:
            if item.product == product:
                return item

        return None

    def add_exposure_item_for_product(self, product):
        """Add an exposure item to the card for a given product.
        The others EXPOSURE_ITEM fields are set to default.

        product -- the PRODUCT to add
        """
        my_logger.debug(message='product:%s' % str(product))
        assert not self.has_product(product), "exposure item already present for product %s" % product
        self.exposure_items = self.exposure_items + [EXPOSURE_ITEM(product=product)]

        return self.exposure_items[-1]

    def delete_exposure_item_for_product(self, product):
        """Delete the exposure item from the card for a given product.

        product -- the PRODUCT to delete
        """
        assert self.has_product(product), "exposure item not present for product %s" % product
        self.exposure_items = filter(lambda e: not (e.product == product), self.exposure_items)


