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
# $Id: c_product_mapper.py 210 2015-05-11 08:46:57Z tbellemb $
#
from types import ListType
from c_name_mapper import NAME_MAPPER
from c_person_mapper import PERSON_MAPPER
from c_product import PRODUCT
from chimitheque_logger import chimitheque_logger
from gluon import current

my_logger = chimitheque_logger()


class PRODUCT_MAPPER(object):
    """Database entity product mapper.

    Request the database to create PRODUCT instances.
    """
    def __init__(self):
        self.__name_mapper = NAME_MAPPER()
        self.__person_mapper = PERSON_MAPPER()

    def __product_from_row(self, product_row):
        """Return a PRODUCT instance from a Row"""
        my_logger.debug(message='product_row:%s' % product_row)

        _broken_reference_list = []
        for table in ['physical_state',
                      'class_of_compounds',
                      'hazard_code',
                      'symbol',
                      'signal_word',
                      'risk_phrase',
                      'safety_phrase',
                      'hazard_statement',
                      'precautionary_statement']:

            my_logger.debug(message='table:%s' % table)
            _reference_value = product_row[table]

            if not type(_reference_value) is ListType:
                _reference_value = [_reference_value]

            for _ref in _reference_value:
                if _ref is not None:
                    _count = current.db(current.db[table]['id'] == _ref).count()
                    my_logger.debug(message='_ref:%s _count:%s' % (_ref, _count))
                    if _count == 0:
                        _broken_reference_list.append(table)
                        break

        return PRODUCT(id=product_row['id'],
                       cas_number=product_row['cas_number'],
                       ce_number=product_row['ce_number'],
                       creation_datetime=product_row['creation_datetime'],
                       person=lambda: self.__person_mapper.find(person_id=product_row['person'])[0]
                       if product_row['person'] is not None
                       else None,
                       name=self.__name_mapper.find(name_id=product_row['name'])
                       if product_row['name'] is not None
                       else None,
                       synonym=[self.__name_mapper.find(name_id=n_id) for n_id in product_row['synonym']]
                       if product_row['synonym'] is not None
                       else None,
                       restricted_access=product_row['restricted_access'],
                       specificity=product_row['specificity'],
                       td_formula=product_row['tdformula'],
                       empirical_formula=product_row['empirical_formula'],
                       linear_formula=product_row['linear_formula'],
                       msds=product_row['msds'],
                       physical_state=product_row['physical_state'],
                       class_of_compounds=product_row['class_of_compounds'],
                       hazard_code=product_row['hazard_code'],
                       symbol=product_row['symbol'],
                       signal_word=product_row['signal_word'],
                       risk_phrase=product_row['risk_phrase'],
                       safety_phrase=product_row['safety_phrase'],
                       hazard_statement=product_row['hazard_statement'],
                       precautionary_statement=product_row['precautionary_statement'],
                       disposal_comment=product_row['disposal_comment'],
                       remark=product_row['remark'],
                       is_cmr=product_row['is_cmr'],
                       is_radio=product_row['is_radio'],
                       cmr_cat=product_row['cmr_cat'],

                       is_in_entity_of=lambda user_id: self.is_in_entity_of(product_id=product_row['id'], user_id=user_id),
                       is_in_entity_except_of=lambda user_id: self.is_in_entity_except_of(product_id=product_row['id'], user_id=user_id),
                       has_storage_archived=lambda product_id, user_id: self.has_storage_archived(product_id=product_row['id'], user_id=user_id),
                       has_bookmark=lambda user_id: self.has_bookmark(product_id=product_row['id'], user_id=user_id),
                       has_history=self.has_history(product_id=product_row['id']),
                       is_orphan=self.is_orphan(product_id=product_row['id']),
                       bookmark=lambda user_id: self.bookmark(product_id=product_row['id'], user_id=user_id),
                       unbookmark=lambda user_id: self.unbookmark(product_id=product_row['id'], user_id=user_id),
                       has_broken_reference=len(_broken_reference_list)>0,
                       broken_reference_list=_broken_reference_list)

    def find(self, product_id=None, history=False, limitby=None, orderby=None):
        """Select products in the database.

           product_id -- search by product id or list of ids
           limitby -- query limit as defined by Web2py
           orderby -- query order as defined by Web2py
           returns: a list of PRODUCT
        """
        my_logger.debug(message='product_id:%s' % str(product_id))
        my_logger.debug(message='limitby:%s' % str(limitby))

        if history:
            product_table = 'product_history'
        else:
            product_table = 'product'

        # join with the name table to order by name.label
        # TODO: detect dynamically from the order by parameter the tables to join
        query_list = [current.db[product_table]['name'] == current.db.name.id]

        if product_id is not None:
            if type(product_id) is ListType:
                query_list.append(current.db[product_table]['id'].belongs(tuple(product_id)))
            else:
                query_list.append(current.db[product_table]['id'] == product_id)

        final_query = (current.db[product_table]['id'] > 0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)
        my_logger.debug(message='final_query:%s' % final_query)

        # getting the ENTITY in the db
        _product_rows = current.db(final_query).select(current.db[product_table]['ALL'], limitby=limitby, orderby=orderby)

        if len(_product_rows) == 0:
            return []
        else:
            return [self.__product_from_row(_product_row) for _product_row in _product_rows]

    def has_storage_archived(self, product_id, user_id):
        """Return True if the product has archived storage for the given product in one of the
        entities of the given user.

        product_id -- the product id
        user_id -- the user id
        """
        if current.auth.has_permission(user_id=user_id, name='admin'):
            _has_storage_archives = current.db((current.db.storage.product == product_id) &
                                               (current.db.storage.archive == True) &
                                               (current.db.storage.store_location == current.db.store_location.id) &
                                               (current.db.store_location.entity == current.db.entity.id)).count() != 0
        else:
            _has_storage_archives = current.db((current.db.storage.product == product_id) &
                                               (current.db.storage.archive == True) &
                                               (current.db.storage.store_location == current.db.store_location.id) &
                                               (current.db.store_location.entity == current.db.entity.id) &
                                               (current.db.membership.user_id == user_id) &
                                               (current.db.entity.id == current.db.membership.group_id)).count() != 0

        return _has_storage_archives

    def is_in_entity_of(self, product_id, user_id):
        """Return True if the product is stored in one of the entities of the given user.

        product_id -- the product id
        user_id -- the user id
        """
        if current.auth.has_membership(user_id=user_id, role='all_entity'):
            _product_entities_count = current.db((current.db.product.id == product_id) &
                                                 (current.db.storage.product == current.db.product.id) &
                                                 (current.db.storage.archive == False)).count()
        else:
            _product_entities_count = current.db((current.db.product.id == product_id) &
                                                 (current.db.storage.product == current.db.product.id) &
                                                 (current.db.storage.archive == False) &
                                                 (current.db.storage.store_location == current.db.store_location.id) &
                                                 (current.db.store_location.entity == current.db.entity.id) &
                                                 (current.db.membership.user_id == user_id) &
                                                 (current.db.entity.id == current.db.membership.group_id)).count()

        return _product_entities_count > 0

    def is_in_entity_except_of(self, product_id, user_id):
        """Return True if the product is stored but not in one of the entities of the given user.

        product_id -- the product id
        user_id -- the user id
        """
	# Use a subrequest to avoid joining with membership which cause a problem when no user belongs to the other entity
	own_entity = [ row.id for row in current.db((current.db.membership.user_id == user_id) & (current.db.entity.id == current.db.membership.group_id)).select(current.db.entity.id) ]
        _product_entities_count = current.db((current.db.product.id == product_id) &
                                             (current.db.storage.product == current.db.product.id) &
                                             (current.db.storage.archive == False) &
                                             (current.db.storage.store_location == current.db.store_location.id) &
                                             ~(current.db.store_location.entity.belongs(own_entity))).count()

        my_logger.debug(message='_product_entities_count:%s' % _product_entities_count)

        return _product_entities_count > 0

    def has_bookmark(self, product_id, user_id):
        """Return True if the product has been bookmarked by the given user.

        product_id -- the product id
        user_id -- the user id
        """
        return current.db((current.db.bookmark.product == product_id) &
                          (current.db.bookmark.person == user_id)).count() > 0

    def has_history(self, product_id):
        """Return True if the product has been modified."""
        return current.db(current.db.product_history.current_record == product_id).count() != 0

    def is_orphan(self, product_id):
        """Return True if the product as no associated storage cards."""
        return current.db(current.db.storage.product == product_id).count() == 0

    def bookmark(self, product_id, user_id):
        """Bookmark a product for the given user.

        product_id -- the product id
        user_id -- the user id
        """
        if not self.has_bookmark(product_id, user_id):
            current.db.bookmark.insert(product=product_id, person=user_id)

    def unbookmark(self, product_id, user_id):
        """Remove product bookmark for the given user.

        product_id -- the product id
        user_id -- the user id
        """
        current.db((current.db.bookmark.product == product_id) &
                   (current.db.bookmark.person == user_id)).delete()

    @staticmethod
    def count_all():
        """Returns the total number of product cards.
        """
        return current.db(current.db.product.archive == False).count()
