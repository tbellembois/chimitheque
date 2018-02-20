# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
from gluon import current

from c_storage import STORAGE
from chimitheque_logger import chimitheque_logger
from c_person_mapper import PERSON_MAPPER
from c_product_mapper import PRODUCT_MAPPER
from c_store_location_mapper import STORE_LOCATION_MAPPER
from c_supplier_mapper import SUPPLIER_MAPPER
from c_unit_mapper import UNIT_MAPPER
from types import ListType
import datetime

my_logger = chimitheque_logger()


class STORAGE_MAPPER(object):

    def __init__(self):
        self.__product_mapper = PRODUCT_MAPPER()
        self.__person_mapper = PERSON_MAPPER()
        self.__store_location_mapper = STORE_LOCATION_MAPPER()
        self.__supplier_mapper = SUPPLIER_MAPPER()
        self.__unit_mapper = UNIT_MAPPER()

    def __storage_from_row(self, storage_row):
        return STORAGE(id=storage_row['id'],
                       volume_weight=storage_row['volume_weight'],
                       unit=lambda: self.__unit_mapper.find(unit_id=storage_row['unit']) \
                                       if storage_row['unit'] is not None \
                                       else None,
                       nb_items=storage_row['nb_items'],
                       creation_datetime=storage_row['creation_datetime'],
                       entry_datetime=storage_row['entry_datetime'],
                       exit_datetime=storage_row['exit_datetime'],
                       expiration_datetime=storage_row['expiration_datetime'],
                       opening_datetime=storage_row['opening_datetime'],
                       comment=storage_row['comment'],
                       barecode=storage_row['barecode'],
                       reference=storage_row['reference'],
                       batch_number=storage_row['batch_number'],
                       archive=storage_row['archive'],
                       to_destroy=storage_row['to_destroy'],
                       product=lambda: self.__product_mapper.find(product_id=storage_row['product'])[0],
                       person=lambda: self.__person_mapper.find(person_id=storage_row['person'])[0],
                       store_location=lambda: self.__store_location_mapper.find(store_location_id=storage_row['store_location'])[0],
                       supplier=lambda: self.__supplier_mapper.find(supplier_id=storage_row['supplier'])[0],
                       # storage history
                       modification_datetime=storage_row['modification_datetime'] if 'modification_datetime' in storage_row else None,

                       has_borrowing=lambda: self.has_borrowing(storage_row['id']),
                       retrieve_borrower=lambda: self.retrieve_borrower(storage_row['id']),
                       retrieve_borrow_datetime=lambda: self.retrieve_borrow_datetime(storage_row['id']),
                       retrieve_borrow_comment=lambda: self.retrieve_borrow_comment(storage_row['id']),
                       has_history=lambda: self.has_history(storage_row['id']))

    def find(self, storage_id=None, storage_history_id=None, entity_id=None, negate_entity_search=False, store_location_id=None, product_id=None, unit_reference_id=None, archive=False, history=False, limitby=None, orderby=None):

        my_logger.debug(message='storage_id:%s' % storage_id)

        assert (storage_history_id is not None and history) or (storage_history_id is None), "history must be True with a storage_history_id!"

        if history:
            table = 'storage_history'
        else:
            table = 'storage'

        query_list = []
        if storage_id is not None or storage_history_id is not None:
            if history:
                if storage_history_id is not None:
                    query_list.append(current.db.storage_history.id == storage_history_id)
                else:
                    query_list.append(current.db.storage_history.current_record == storage_id)
            else:
                if type(storage_id) is ListType:
                    query_list.append(current.db[table]['id'].belongs(storage_id))
                else:
                    query_list.append(current.db[table]['id'] == storage_id)
        if entity_id is not None:
            if type(entity_id) is ListType:
                if negate_entity_search:
                    query_list.append((current.db[table]['store_location']==current.db.store_location.id) &
                                      (~current.db.store_location.entity.belongs(tuple(entity_id))))
                else:
                    query_list.append((current.db[table]['store_location']==current.db.store_location.id) &
                                      (current.db.store_location.entity.belongs(tuple(entity_id))))
            else:
                if negate_entity_search:
                    query_list.append((current.db[table]['store_location']==current.db.store_location.id) &
                                      (~current.db.store_location.entity==entity_id))
                else:
                    query_list.append((current.db[table]['store_location']==current.db.store_location.id) &
                                      (current.db.store_location.entity==entity_id))
        if store_location_id is not None:
            query_list.append(current.db[table]['store_location'] == store_location_id)
        if product_id is not None:
            if type(product_id) is ListType:
                query_list.append(current.db[table]['product'].belongs(product_id))
            else:
                query_list.append(current.db[table]['product'] == product_id)
        if unit_reference_id is not None:
            query_list.append((current.db.storage.unit == current.db.unit.id) &
                              (current.db.unit.reference == unit_reference_id))

        if archive is not None:
            final_query = (current.db[table]['archive']==archive)
        else:
            final_query = (current.db[table]['id']>0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)
        my_logger.debug(message='final_query:%s' % str(final_query))

        _storage_rows = current.db(final_query).select(current.db[table]['ALL'],
                left=(current.db.borrow.on(current.db[table]['id'] == current.db.borrow.storage)),
                limitby=limitby,
                orderby=orderby)

        my_logger.debug(message='len(_storage_rows):%s' % str(len(_storage_rows)))
        my_logger.debug(message='_storage_rows:%s' % str(_storage_rows))
        if len(_storage_rows) == 0:
            return []
        else:
            return [self.__storage_from_row(_storage_row) for _storage_row in _storage_rows]

    def has_history(self, storage_id):
        return current.db(current.db.storage_history.current_record==storage_id).count() > 0

    def has_borrowing(self, storage_id):
        return current.db(current.db.borrow.storage==storage_id).count() > 0

    def retrieve_borrower(self, storage_id):

        borrower = current.db((current.db.borrow.storage==storage_id) &
                              (current.db.borrow.borrower==current.db.person.id)).select(current.db.person.id).first()

        if borrower is not None:
            return PERSON_MAPPER().find(person_id=borrower.id)[0]
        else:
            return None

    def retrieve_borrow_comment(self, storage_id):

        borrow = current.db((current.db.borrow.storage==storage_id)).select(current.db.borrow.comment).first()

        if borrow is not None:
            return borrow.comment
        else:
            return None

    def retrieve_borrow_datetime(self, storage_id):

        borrow = current.db((current.db.borrow.storage==storage_id)).select(current.db.borrow.creation_datetime).first()

        if borrow is not None:
            return borrow.creation_datetime
        else:
            return None

    def delete(self, storage): # STORAGE type

        current.db(current.db.storage.id==storage.id).delete()
        current.db.commit()

    def update(self, storage): # STORAGE type

        row = current.db(current.db.storage.id==storage.id).select().first()

        row.update_record(product=storage.product.id,
                          store_location=storage.store_location.id,
                          volume_weight=storage.volume_weight,
                          unit=storage.unit.id if storage.unit is not None else None,
                          nb_items=storage.nb_items,
                          entry_datetime=storage.entry_datetime,
                          exit_datetime=storage.exit_datetime,
                          expiration_datetime=storage.expiration_datetime,
                          opening_datetime=storage.opening_datetime,
                          comment=storage.comment,
                          barecode=storage.barecode,
                          reference=storage.reference,
                          batch_number=storage.batch_number,
                          supplier=storage.supplier.id,
                          archive=storage.archive,
                          to_destroy=storage.to_destroy)

        current.db.commit()

    @staticmethod
    def create_barecode(product_id):
        """Return the generated barecode from a product
        """
        my_logger.debug(message='create_barecode')
        product_cas_number = current.db(current.db.product.id == product_id).select(current.db.product.cas_number).first().cas_number

        my_logger.debug(message='product_id:%s' % product_id)
        my_logger.debug(message='product_cas_number:%s' % product_cas_number)

        last_storage_id = current.db(current.db.storage).count()
        my_logger.debug(message='last_storage_id:%s' % last_storage_id)

        today = datetime.date.today()
        today = today.strftime('%Y%m%d')

        barecode = '%s_%s_%s.1' % (product_cas_number, today, last_storage_id)
        my_logger.debug(message='barecode:%s' % barecode)

        return barecode

    @staticmethod
    def compute_stock_total(product, store_location):
        """Return the stock total of the given product in the store location
        and its sub store locations.
        
        A product can be stored several times in different units.
        
        product -- a PRODUCT instance
        return: a dictionary { unit: volume_weight } with
                unit -- the reference unit id
                volume_weight -- the volume or weight
        """
        _stock = {}
        _stock_current = STORAGE_MAPPER().compute_stock_current(product, store_location)
        
        for _child in store_location.retrieve_children():
            _child_stock_current = STORAGE_MAPPER().compute_stock_current(product, _child)
        
            for _reference in _child_stock_current.keys():
                if _reference in _stock.keys():
                    _stock[_reference] = _stock[_reference]  + _child_stock_current[_reference]
                else:
                    _stock[_reference] = _child_stock_current[_reference]
        
        # adding the stock_current
        for _reference in _stock_current.keys():
            if _reference in _stock.keys():
                _stock[_reference] = _stock[_reference]  + _stock_current[_reference]
            else:
                _stock[_reference] = _stock_current[_reference]
        
        return _stock


    @staticmethod
    def compute_stock_current(product, store_location):
        """Return the stock of the product in the given store location.
        
        A product can be stored several times in different units.
        
        store_location -- a STORE_LOCATION instance
        return: a dictionary { unit: volume_weight } with
                unit -- the reference unit id
                volume_weight -- the volume or weight
        """
        _stock = {}
        
        for _storage in STORAGE_MAPPER().find(store_location_id=store_location.id, product_id=product.id):
        
            my_logger.debug(message='_storage:%s' % _storage)
        
            # using the number 99 (random choice) as a dictionary key if the storage has no unit
            _reference = _storage.unit.reference.id if _storage.unit is not None else 99
            _multiplier = _storage.unit.multiplier_for_reference if _storage.unit is not None else 1
            _volume_weight = _storage.volume_weight if _storage.volume_weight is not None else 1
        
            if _reference in _stock.keys():
                _stock[_reference] = _stock[_reference] + (_volume_weight * _multiplier)
            else:
                _stock[_reference] = _volume_weight * _multiplier
        
        return _stock

