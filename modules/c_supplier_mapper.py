# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from c_supplier import SUPPLIER
from chimitheque_logger import chimitheque_logger
from gluon import current

my_logger = chimitheque_logger()


class SUPPLIER_MAPPER(object):

    def __init__(self):
        pass

    def __supplier_from_row(self, supplier_row):
        return SUPPLIER(id=supplier_row['id'],
                        label=supplier_row['label'])

    def find(self, supplier_id):

        query_list = []

        if supplier_id is not None:
            query_list.append(current.db.supplier.id == supplier_id)

        final_query = (current.db.supplier.id>0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        _supplier_rows = current.db(final_query).select(current.db.supplier.ALL)

        if len(_supplier_rows) == 0:
            return []
        else:
            return [self.__supplier_from_row(_supplier_row) for _supplier_row in _supplier_rows]

