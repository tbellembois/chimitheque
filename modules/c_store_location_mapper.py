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
# $Id: c_store_location_mapper.py 196 2015-02-26 15:32:18Z tbellemb $
#
from gluon import current

from c_store_location import STORE_LOCATION
from chimitheque_logger import chimitheque_logger
import c_entity_mapper


my_logger = chimitheque_logger()


class STORE_LOCATION_MAPPER:
    """Database store_location table mapper.

    Request the database to create STORE_LOCATION instances.
    """
    def _store_location_from_row(self, _store_location_row):

        return STORE_LOCATION(id=_store_location_row['id'],
                              name=_store_location_row['label'],
                              can_store=_store_location_row['can_store'],
                              color=_store_location_row['color'],
                              full_path=_store_location_row['label_full_path'],
                              parent=lambda: self.find(store_location_id=_store_location_row['parent'])[0],
                              entity=lambda: c_entity_mapper.ENTITY_MAPPER().find(entity_id=_store_location_row['entity'])[0],

                              has_parent=lambda: self.has_parent(store_location_id=_store_location_row['id']),
                              has_storage=lambda product_id, archive: self.has_storage(store_location_id=_store_location_row['id'], product_id=product_id, archive=archive),
                              compute_nb_storage_card=lambda: self.get_nb_storage_card(_store_location_row['id']),
                              compute_nb_archived_storage_card=lambda: self.get_nb_archived_storage_card(_store_location_row['id']),
                              compute_nb_children=lambda: self.get_nb_children(_store_location_row['id']),
                              retrieve_parents=lambda: self.find_parents(store_location_id=_store_location_row['id']),
                              retrieve_children=lambda: self.find_children(store_location_id=_store_location_row['id']))


    def find(self, store_location_id=None, label=None, entity_id=None, root=False, limitby=None, orderby=None):
        """Select store locations in the database.

           The query parameters can be combined.
           example: search store locations with id in [1, 2, 3] that belongs to entity with id 35.

           store_location_id -- search by store location id
           label -- search by store location label (name)
           entity_id -- search store locations that belongs to entity with id entity_id
           root -- if True returns only root store locations (with no parent)
           limitby -- query limit as defined by Web2py
           orderby -- query order as defined by Web2py

           returns: a list of STORE_LOCATION
        """
        query_list = []

        if store_location_id is not None:
            query_list.append(current.db.store_location.id == store_location_id)
        if label is not None:
            query_list.append(current.db.store_location.label == label)
        if entity_id is not None:
            query_list.append(current.db.store_location.entity == entity_id)
        if root:
            query_list.append(current.db.store_location.parent == None)

        final_query = (current.db.store_location.id > 0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        # getting the STORE_LOCATION in the db
        _store_location_rows = current.db(final_query).select(limitby=limitby, orderby=orderby)

        if len(_store_location_rows) == 0:
            return []
        else:
            return [self._store_location_from_row(_store_location_row) for _store_location_row in _store_location_rows]


    def find_parents(self, store_location_id):
        """Find the parents of the given store location.
        A store location has only one direct parent.
        Search recursively up to the root. 

        store_location_id -- the store location id
        return: a list of STORE_LOCATION
        """
        # getting the STORE_LOCATION in the db
        _store_location_row = current.db(current.db.store_location.id == store_location_id).select().first()

        #if  _store_location_row is None or _store_location_row['parent'] == 0:
        if store_location_id is None:
            return [None]
        else:
            return [self._store_location_from_row(_store_location_row)] + self.find_parents(_store_location_row['parent'])


    def find_children(self, store_location_id):
        """Find the children of the given store location.

        store_location_id -- the store location id
        return: a list of STORE_LOCATION
        """
        my_logger.debug(message='store_location_id=%s' % store_location_id)

        # getting the children in the db
        _store_location_children_rows = current.db(current.db.store_location.parent == store_location_id).select()
        _ret = []

        for _store_location_row in _store_location_children_rows:
            my_logger.debug(message='_store_location_row[\'id\']=%s' % _store_location_row['id'])
            if (self.get_nb_children(store_location_id=_store_location_row['id'])) == 0:
                my_logger.debug(message='has NO children:%s' % _store_location_row['id'])
                _ret.append(self._store_location_from_row(_store_location_row))
            else:
                my_logger.debug(message='has children:%s' % _store_location_row['id'])
                _ret = _ret + [self._store_location_from_row(_store_location_row)] + self.find_children(store_location_id=_store_location_row['id'])

        return _ret


    def has_parent(self, store_location_id):
        """Return True is the given store location has a parent.

        store_location_id -- the store location id
        """
        my_logger.debug(message='store_location_id=%s' % store_location_id)
        _has_parent = current.db(current.db.store_location.id == store_location_id).select().first().parent is not None
        my_logger.debug(message='_has_parent=%s' % _has_parent)

        return _has_parent


    def has_storage(self, store_location_id, product_id=None, archive=False):
        """Return True is the given store location has storages for the given product.

        store_location_id -- the store location id
        product_id -- the product id
        archive -- if True search for archived storages
        """
        my_logger.debug(message='store_location_id=%s' % store_location_id)
        my_logger.debug(message='product_id=%s' % product_id)

        if product_id is not None:
            _has_storage = current.db((current.db.storage.store_location == store_location_id) &
                                      (current.db.storage.product == product_id) &
                                      (current.db.storage.archive  == archive)).count() > 0
        else:
            _has_storage = current.db((current.db.storage.store_location == store_location_id) &
                                      (current.db.storage.archive == archive)).count() > 0

        my_logger.debug(message='_has_storage=%s' % _has_storage)

        return _has_storage


    def get_nb_children(self, store_location_id):
        """Return the number of children of the given store_location.

        store_location_id -- the store location id
        """
        my_logger.debug(message='store_location_id=%s' % store_location_id)
        _count = current.db(current.db.store_location.parent == store_location_id).count()
        my_logger.debug(message='_count=%s' % _count)

        return _count


    def get_nb_storage_card(self, store_location_id):
        """Return the number of storage cards of the given store_location.

        store_location_id -- the store location id
        """
        return current.db((current.db.storage.store_location == store_location_id) &
                          (current.db.storage.archive == False)).count()


    def get_nb_archived_storage_card(self, store_location_id):
        """Return the number of archived storage cards of the given store_location.

        store_location_id -- the store location id
        """
        return current.db((current.db.storage.store_location == store_location_id) &
                          (current.db.storage.archive == True)).count()


    def save(self, store_location):  # STORE_LOCATION type
        """Save the store location into the database.

        store_location: a STORE_LOCATION instance
        """
        # inserting the user in the DB
        store_location.id = current.db.store_location.insert(label=store_location.name,
                                                             label_full_path=store_location.full_path,
                                                             entity=store_location.entity.id,
                                                             parent=store_location.parent.id,
                                                             can_store=store_location.can_store,
                                                             color=store_location.color)

        # not sure that it is necessary...
        current.db.commit()


    def update(self, store_location):  # STORE_LOCATION type
        """Update the store location into the database.

        store_location: a STORE_LOCATION instance
        """
        my_logger.debug(message='store_location=%s' % store_location)

        # we pass the registration_key for the disable/enable feature
        current.db(current.db.store_location.id == store_location.id).update(label=store_location.name,
                                                                             label_full_path=store_location.full_path,
                                                                             entity=store_location.entity.id,
                                                                             parent=store_location.parent.id,
                                                                             can_store=store_location.can_store,
                                                                             color=store_location.color)
        # not sure that it is necessary...
        current.db.commit()


