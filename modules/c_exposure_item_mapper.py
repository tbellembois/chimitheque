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
from c_exposure_item import EXPOSURE_ITEM
from gluon import current
from types import ListType

my_logger = chimitheque_logger()


class EXPOSURE_ITEM_MAPPER(object):
    """Database exposure item table mapper.

    Request the database to create EXPOSURE_ITEM instances.
    """
    def __init__(self):
        pass

    def _exposure_item_from_row(self, _exposure_item_row):
        """Return an EXPOSURE_ITEM instance from a row.
        """
        from c_product_mapper import PRODUCT_MAPPER
        self.__product_mapper = PRODUCT_MAPPER()

        return EXPOSURE_ITEM(id=_exposure_item_row['id'],
                             creation_datetime=_exposure_item_row['creation_datetime'],
                             product=lambda: self.__product_mapper.find(product_id=_exposure_item_row['product'])[0],
                             kind_of_work=_exposure_item_row['kind_of_work'],
                             cpe=_exposure_item_row['cpe'],
                             ppe=_exposure_item_row['ppe'],
                             nb_exposure=_exposure_item_row['nb_exposure'],
                             exposure_time=_exposure_item_row['exposure_time'],
                             simultaneous_risk=_exposure_item_row['simultaneous_risk'])

    def find(self, exposure_item_id=None, orderby=None):
        """Select exposure items in the database.

        exposure_item_id -- search by exposure_item_id or list of ids
        """
        my_logger.debug(message='exposure_item_id:%s' % exposure_item_id)
        query_list = []

        if exposure_item_id is not None:
            if type(exposure_item_id) is ListType:
                query_list.append(current.db.exposure_item.id.belongs(exposure_item_id))
            else:
                query_list.append(current.db.exposure_item.id == exposure_item_id)

        # joining with the product an name table for the orderby parameter
        final_query = (current.db.exposure_item.product == current.db.product.id) & (current.db.product.name == current.db.name.id)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        # getting the EXPOSURE_ITEM in the db
        _exposure_item_rows = current.db(final_query).select(current.db.exposure_item.ALL, orderby=orderby)
        my_logger.debug(message='_exposure_item_rows:%s' % str(_exposure_item_rows))

        if len(_exposure_item_rows) == 0:
            return []
        else:
            return [self._exposure_item_from_row(_exposure_item_row) for _exposure_item_row in _exposure_item_rows]

    def delete(self, exposure_item):
        """Delete an exposure_item.

        exposure_item -- an EXPOSURE_ITEM instance
        return: the last row id
        """
        # deleting exposure cards references
        linked_exposure_cards = current.db(current.db.exposure_card.exposure_item.contains(exposure_item.id)).select()
        for linked_exposure_card in linked_exposure_cards:
            exposure_items = linked_exposure_card.exposure_item
            exposure_items.remove(exposure_item.id)
            linked_exposure_card.update_record(exposure_items=exposure_items)

        _id = current.db(current.db.exposure_item.id == exposure_item.id).delete()
        current.db.commit()

        return _id

    def update(self, exposure_item): # EXPOSURE_ITEM type

        my_logger.debug(message='exposure_item:%s' % str(exposure_item))

        if isinstance(exposure_item.id, (int, long)):
            _is_new = False
        else:
            _is_new = True
        my_logger.debug(message='_is_new:%s' % _is_new)

        if _is_new:
            _ret = current.db.exposure_item.insert(product=exposure_item.product.id,
                                            kind_of_work=exposure_item.kind_of_work,
                                            cpe=exposure_item.cpe,
                                            ppe=exposure_item.ppe,
                                            nb_exposure=exposure_item.nb_exposure,
                                            exposure_time=exposure_item.exposure_time,
                                            simultaneous_risk=exposure_item.simultaneous_risk)

        else:
            row = current.db(current.db.exposure_item.id == exposure_item.id).select().first()

            row.update_record(product=exposure_item.product.id,
                              kind_of_work=exposure_item.kind_of_work,
                              cpe=exposure_item.cpe,
                              ppe=exposure_item.ppe,
                              nb_exposure=exposure_item.nb_exposure,
                              exposure_time=exposure_item.exposure_time,
                              simultaneous_risk=exposure_item.simultaneous_risk)
            
            _ret = row.id

        current.db.commit()

        return _ret
