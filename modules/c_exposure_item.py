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

my_logger = chimitheque_logger()


class EXPOSURE_ITEM(object):
    """Define an exposure item.

    An exposure item is an element defining the exposure to a specific product.
    """
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id') if 'id' in kwargs else web2py_uuid()  # uid to debug instance creation - not commited in DB
        self.__creation_datetime = kwargs.get('creation_datetime')
        self.__product = kwargs.get('product')
        self.__kind_of_work = kwargs.get('kind_of_work')
        self.__cpe = kwargs.get('cpe')
        self.__ppe = kwargs.get('ppe')
        self.__nb_exposure = kwargs.get('nb_exposure')
        self.__exposure_time = kwargs.get('exposure_time')
        self.__simultaneous_risk = kwargs.get('simultaneous_risk')


    def __repr__(self):
        return '<exposure_item:%s:%s>' % (self.id, self.product)

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return self.product == other.product

    @property
    def id(self):
        """Return the exposure item id."""
        return self.__id

    @property
    def creation_datetime(self):
        """Return the exposure item creation datetime."""
        return self.__creation_datetime

    @property
    def product(self):
        """Return the exposure item product."""
        try:
            return self.__product()
        except TypeError:
            return self.__product

    @property
    def kind_of_work(self):
        """Return the exposure item kind of work."""
        return self.__kind_of_work

    @kind_of_work.setter
    def kind_of_work(self, value):
        """Set the exposure item kind of work."""
        self.__kind_of_work = value

    @property
    def cpe(self):
        """Return the exposure item cpe."""
        return self.__cpe

    @cpe.setter
    def cpe(self, value):
        """Set the exposure item cpe."""
        self.__cpe = value

    @property
    def ppe(self):
        """Return the exposure item ppe."""
        return self.__ppe

    @ppe.setter
    def ppe(self, value):
        """Set the exposure item ppe."""
        self.__ppe = value

    @property
    def nb_exposure(self):
        """Return the exposure item number of exposure."""
        return self.__nb_exposure

    @nb_exposure.setter
    def nb_exposure(self, value):
        """Set the exposure item nb exposure."""
        self.__nb_exposure = value

    @property
    def exposure_time(self):
        """Return the exposure item exposure time."""
        return self.__exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        """Set the exposure item exposure time."""
        self.__exposure_time = value

    @property
    def simultaneous_risk(self):
        """Return the exposure item simultaneous risk."""
        return self.__simultaneous_risk

    @simultaneous_risk.setter
    def simultaneous_risk(self, value):
        """Set the exposure item simultaneous risk."""
        self.__simultaneous_risk = value


