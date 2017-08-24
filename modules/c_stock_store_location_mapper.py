# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
from gluon import current

from chimitheque_logger import chimitheque_logger
from c_stock_store_location import STOCK_STORE_LOCATION
from c_product_mapper import PRODUCT_MAPPER
from c_storage_mapper import STORAGE_MAPPER
from c_store_location_mapper import STORE_LOCATION_MAPPER
from c_unit_mapper import UNIT_MAPPER


my_logger = chimitheque_logger()


class STOCK_STORE_LOCATION_MAPPER(object):

    def __init__(self):
        self.__product_mapper = PRODUCT_MAPPER()
        self.__store_location_mapper = STORE_LOCATION_MAPPER()
        self.__storage_mapper = STORAGE_MAPPER()
        self.__unit_mapper = UNIT_MAPPER()

    def __stock_store_location_from_row(self, stock_store_location_row):
        return STOCK_STORE_LOCATION(id=stock_store_location_row['id'],
                                    product=lambda: self.__product_mapper.find(stock_store_location_row['product'])[0],
                                    store_location=lambda: self.__store_location_mapper.find(stock_store_location_row['store_location'])[0],
                                    unit_reference=lambda: self.__unit_mapper.find(stock_store_location_row['unit_reference']) \
                                                           if stock_store_location_row['unit_reference'] is not None \
                                                           else None,
                                    volume_weight_actual=stock_store_location_row['volume_weight_actual'],
                                    volume_weight_total=stock_store_location_row['volume_weight_total'],
                                    storages=lambda: self.find(store_location_id=stock_store_location_row['store_location'],
                                                               product_id=stock_store_location_row['product'],
                                                               unit_reference_id=stock_store_location_row['unit_reference']))

    # development/test function - not to be used in the code
    def new_for_store_location_and_product_and_unit(self, store_location_id, product_id, unit_reference_id):
        _stock_store_location_row = {}
        _stock_store_location_row['id'] = -1  # not used
        _stock_store_location_row['store_location'] = store_location_id
        _stock_store_location_row['product'] = product_id
        _stock_store_location_row['unit_reference'] = unit_reference_id
        _stock_store_location_row['volume_weight_actual'] = 0
        _stock_store_location_row['volume_weight_total'] = 0

        return self.__stock_store_location_from_row(_stock_store_location_row)

    def find(self, store_location_id, product_id=None, unit_reference_id=None, no_unit_reference=False):
        assert ((no_unit_reference and (unit_reference_id is None)) or
                ((not no_unit_reference) and (unit_reference_id is not None)),
            "unit_reference_id and no_unit_reference parameters incoherence!")

        query_list = []

        if product_id is not None:
            query_list.append(current.db.stock_store_location.product == product_id)
        if no_unit_reference:
            query_list.append(current.db.stock_store_location.unit_reference == None)
        elif unit_reference_id is not None:
            query_list.append(current.db.stock_store_location.unit_reference == unit_reference_id)
        else:
            query_list.append(current.db.stock_store_location.id>0)

        #query_list.append(current.db.stock_store_location.unit_reference == unit_reference_id)

        final_query = (current.db.stock_store_location.store_location == store_location_id)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        _stock_store_location_rows = current.db(final_query).select()

        if len(_stock_store_location_rows) == 0:
            return []
        else:
            return [self.__stock_store_location_from_row(_stock_store_location_row) for _stock_store_location_row in _stock_store_location_rows]

    def exists(self, store_location_id, product_id, unit_reference_id=None, no_unit_reference=False):
        assert ((no_unit_reference and (unit_reference_id is None)) or
                ((not no_unit_reference) and (unit_reference_id is not None)),
                "unit_reference_id and no_unit_reference parameters incoherence!")

        query_list = []

        if no_unit_reference:
            query_list.append(current.db.stock_store_location.unit_reference == None)
        elif unit_reference_id is not None:
            query_list.append(current.db.stock_store_location.unit_reference == unit_reference_id)
        else:
            query_list.append(current.db.stock_store_location.id>0)

        final_query = ((current.db.stock_store_location.store_location == store_location_id) &
                       (current.db.stock_store_location.product == product_id))

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        return current.db(final_query).count() > 0

    def save(self, stock_store_location):
        _unit_reference_id = stock_store_location.unit_reference.id \
                            if stock_store_location.unit_reference is not None \
                            else None
        current.db.stock_store_location.insert(volume_weight_total=stock_store_location.volume_weight_total,
                                               volume_weight_actual=stock_store_location.volume_weight_actual,
                                               unit_reference=_unit_reference_id,
                                               store_location=stock_store_location.store_location.id,
                                               product=stock_store_location.product.id)

        current.db.commit()

    def update(self, stock_store_location):
        _unit_reference_id = stock_store_location.unit_reference.id \
                            if stock_store_location.unit_reference is not None \
                            else None
        current.db(current.db.stock_store_location.id == stock_store_location.id).update(volume_weight_total=stock_store_location.volume_weight_total,
                                                                                           volume_weight_actual=stock_store_location.volume_weight_actual,
                                                                                           unit_reference=_unit_reference_id,
                                                                                           store_location=stock_store_location.store_location.id,
                                                                                           product=stock_store_location.product.id)

        current.db.commit()
