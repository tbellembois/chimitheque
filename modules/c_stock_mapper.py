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
# $Id: c_stock_mapper.py 196 2015-02-26 15:32:18Z tbellemb $
#
from gluon import current

from chimitheque_logger import chimitheque_logger
from c_stock import STOCK
from c_product_mapper import PRODUCT_MAPPER
from c_entity_mapper import ENTITY_MAPPER
from c_unit_mapper import UNIT_MAPPER
from types import ListType


my_logger = chimitheque_logger()


class STOCK_MAPPER(object):

    def __init__(self):

        self.__product_mapper = PRODUCT_MAPPER()
        self.__entity_mapper = ENTITY_MAPPER()
        self.__unit_mapper = UNIT_MAPPER()

    def __stock_from_row(self, stock_row):

        my_logger.debug(message='%s' % stock_row)
        return STOCK(id=stock_row['stock']['id'],
                                    product=lambda: self.__product_mapper.find(stock_row['stock']['product'])[0],
                                    entity=lambda: self.__entity_mapper.find(stock_row['stock']['entity'])[0],
                                    maximum=stock_row['stock']['maximum'],
                                    maximum_unit=self.__unit_mapper.find(stock_row['stock']['maximum_unit']) if stock_row['stock']['maximum_unit'] is not None else None,
                                    minimum=stock_row['stock']['minimum'],
                                    minimum_unit=self.__unit_mapper.find(stock_row['stock']['minimum_unit']) if stock_row['stock']['minimum_unit'] is not None else None)

    def find(self, product_id, entity_id):

        if type(entity_id) is ListType:
            _stock_rows = current.db((current.db.stock.entity.belongs(tuple(entity_id))) &
                         (current.db.stock.product == product_id) &
                         (current.db.entity.id == current.db.stock.entity)).select()
        else:
            _stock_rows = current.db((current.db.stock.entity == entity_id) &
                         (current.db.stock.product == product_id) &
                         (current.db.entity.id == current.db.stock.entity)).select()

        return [self.__stock_from_row(_stock_row) for _stock_row in _stock_rows]
