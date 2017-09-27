# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class STOCK_STORE_LOCATION(object):

    def __init__(self, *args, **kwargs):

        self.__id = kwargs.get('id')
        self.__product = kwargs.get('product')  # lambda that returns a product type
        self.__store_location = kwargs.get('store_location')  # lambda that returns a STORE_LOCATION type
        self.__unit_reference = kwargs.get('unit_reference')  # lambda that returns a unit type
        self.__volume_weight_actual = kwargs.get('volume_weight_actual')
        self.__volume_weight_total = kwargs.get('volume_weight_total')

        self.__storages = kwargs.get('storages')  # lambda function that returns a [ storage ]

    def __repr__(self):
        return '<STOCK_STORE_LOCATION:%s:%s:actual=%s:total=%s:%s>' % (self.store_location,
                                                    self.product,
                                                    self.volume_weight_actual,
                                                    self.volume_weight_total,
                                                    self.unit_reference)

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return (self.product == other.product) and\
                   (self.unit_reference == other.unit_reference) and\
                   (self.store_location == other.store_location)

    @property
    def id(self):
        return self.__id

    @property
    def product(self):
        return self.__product()

    @property
    def store_location(self):
        return self.__store_location()

    @property
    def unit_reference(self):
        return self.__unit_reference()

    @property
    def storages(self):
        return self.__storages()

    @property
    def volume_weight_actual(self):
        return self.__volume_weight_actual

    @volume_weight_actual.setter
    def volume_weight_actual(self, value):
        self.__volume_weight_actual = value

    @property
    def volume_weight_total(self):
        return self.__volume_weight_total

    @volume_weight_total.setter
    def volume_weight_total(self, value):
        self.__volume_weight_total = value
 
    def update_stock_actual(self, storage):
        assert (((storage.unit is None) and (self.unit_reference is None)) or \
                (storage.unit.reference == self.unit_reference)), "STOCK store location update with a different reference unit!"

        _volume_weight = storage.volume_weight
        if storage.unit is not None:
            _multiplier_for_reference = storage.unit.multiplier_for_reference
            self.volume_weight_actual = self.volume_weight_actual + (_volume_weight * _multiplier_for_reference)
        else:
            self.volume_weight_actual = self.volume_weight_actual + 1

    def update_stock_total(self, storage):
        my_logger.debug(message='storage:%s' % storage)
        my_logger.debug(message='self:%s' % self)
        assert (((storage.unit is None) and (self.unit_reference is None)) or \
                (storage.unit.reference == self.unit_reference)), "STOCK store location update with a different reference unit!"

        _volume_weight = storage.volume_weight
        if storage.unit is not None:
            my_logger.debug(message='storage.unit:%s' % storage.unit)
            my_logger.debug(message='storage.unit.multiplier_for_reference:%s' % storage.unit.multiplier_for_reference)
            _multiplier_for_reference = storage.unit.multiplier_for_reference
            self.volume_weight_total = self.volume_weight_total + (_volume_weight * _multiplier_for_reference)
        else:
            self.volume_weight_total = self.volume_weight_total + 1

