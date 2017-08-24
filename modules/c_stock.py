# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class STOCK(object):

    def __init__(self, *args, **kwargs):

        self.__id = kwargs.get('id')
        self.__product = kwargs.get('product')  # lambda that returns a product type
        self.__entity = kwargs.get('entity')  # lambda that returns a entity type

        self.__maximum = kwargs.get('maximum')
        self.__maximum_unit = kwargs.get('maximum_unit')  # unit type
        self.__minimum = kwargs.get('minimum')
        self.__minimum_unit = kwargs.get('minimum_unit')  # unit type

    def __repr__(self):
        return '<STOCK:%s:%s:maximum=%s:%sminimum=%s:%s>' % (self.product,
                                                             self.entity,
                                                             self.maximum,
                                                             self.maximum_unit,
                                                             self.minimum,
                                                             self.minimum_unit)

    @property
    def id(self):
        return self.__id

    @property
    def product(self):
        return self.__product()

    @property
    def entity(self):
        return self.__entity()

    @property
    def maximum(self):
        return self.__maximum

    @property
    def maximum_unit(self):
        return self.__maximum_unit

    @property
    def minimum(self):
        return self.__minimum

    @property
    def minimum_unit(self):
        return self.__minimum_unit
