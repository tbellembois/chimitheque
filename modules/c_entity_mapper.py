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
# $Id: c_entity_mapper.py 196 2015-02-26 15:32:18Z tbellemb $
#
from gluon import current

from c_entity import ENTITY
from chimitheque_logger import chimitheque_logger
from types import ListType
import c_person_mapper
import chimitheque_commons as cc
import c_store_location_mapper

my_logger = chimitheque_logger()


class ENTITY_MAPPER:
    """Database entity table mapper.

    Request the database to create ENTITY instances.
    """
    def _entity_from_row(self, _entity_row):
        """Return an ENTITY instance from a Row"""
        my_logger.debug(message='_entity_row:%s' % str(_entity_row))

        return ENTITY(id=_entity_row['id'],
                      name=_entity_row['role'],
                      description=_entity_row['description'],
                      manager=lambda: c_person_mapper.PERSON_MAPPER().find(person_id=_entity_row['manager']) if _entity_row['manager'] is not None else None,
                      compute_nb_store_location=lambda: self.compute_nb_store_location(_entity_row['id']),
                      compute_nb_storage_card=lambda: self.compute_nb_storage_card(_entity_row['id']),
                      compute_nb_archived_storage_card=lambda: self.compute_nb_archived_storage_card(_entity_row['id']),
                      compute_nb_user=lambda: self.compute_nb_user(_entity_row['id']),
                      count_all=lambda: self.count_all(),
                      retrieve_users=lambda: c_person_mapper.PERSON_MAPPER().find(entity_id=_entity_row['id']),
                      retrieve_store_locations=lambda: c_store_location_mapper.STORE_LOCATION_MAPPER().find(entity_id=_entity_row['id']))

    def find(self,
             entity_id=None,
             role=None,
             negate_id_search=False,
             negate_role_search=False,
             person_id=None,
             product_id=None,
             limitby=None,
             orderby=None):
        """Select entities in the database.

           The query parameters can be combined.
           example: search entities with id in [1, 2, 3] that contains the product with id 35.

           entity_id -- search by entity id or list of ids
           role -- search by entity role
           negate_id_search -- if True search entity with id not in entity_id
           negate_role_search -- if True search entity with role != role
           person_id -- search entities that have the person person_id member of
           product_id -- search entities that contains the product with id product_id
           limitby -- query limit as defined by Web2py
           orderby -- query order as defined by Web2py
           returns: a list of ENTITY
        """
        query_list = []
        groupby = None

        if entity_id is not None:
            if type(entity_id) is ListType:
                if negate_id_search:
                    query_list.append(~current.db.entity.id.belongs(entity_id))
                else:
                    query_list.append(current.db.entity.id.belongs(entity_id))
            else:
                if negate_id_search:
                    query_list.append(~current.db.entity.id == entity_id)
                else:
                    query_list.append(current.db.entity.id == entity_id)
        if role is not None:
            if negate_role_search:
                query_list.append(~(current.db.entity.role == role))
            else:
                query_list.append(current.db.entity.role == role)
        if person_id is not None:
            # if the PERSON belongs to the "all_entity" ENTITY
            # then returning all the entities
            _all_entity_id = current.db(current.db.entity.role == 'all_entity').select(current.db.entity.id).first().id
            if not current.auth.has_membership(group_id=_all_entity_id, user_id=person_id):
                query_list.append((current.db.membership.user_id == person_id) &
                                  (current.db.entity.id == current.db.membership.group_id))
        if product_id is not None:
            query_list.append((current.db.store_location.entity == current.db.entity.id) &
                              (current.db.storage.store_location == current.db.store_location.id) &
                              (current.db.storage.product == product_id))
            groupby = current.db.entity.id
        if orderby is None:
            orderby = current.db.entity.role

        # do not retrieve users personal groups, either the root_entity entity
        final_query = ((~current.db.entity.role.like('user_%%')) &
                       (~current.db.entity.role.like('root_entity')))

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        # getting the ENTITY in the db
        _entity_rows = current.db(final_query).select(current.db.entity.ALL,
                                                      groupby=groupby,
                                                      limitby=limitby,
                                                      orderby=orderby)
        my_logger.debug(message='_entity_rows:%s' % str(_entity_rows))

        if len(_entity_rows) == 0:
            return []
        else:
            return [self._entity_from_row(_entity_row) for _entity_row in _entity_rows]

    def delete(self, entity):
        """Delete an entity.

        entity -- an ENTITY instance
        return: the last row id
        """
        _id = current.db(current.db.entity.id == entity.id).delete()
        current.db.commit()

        return _id

    def count_all(self):
        """Count the number"""
        # count the entities in the db
        _count = current.db((~current.db.entity.role.like('user_%%')) &
                            (current.db.entity.id > 0)).count()

        return _count

    def compute_nb_storage_card(self, entity_id):
        """Get the number of storage cards for the given entity.

        entity_id -- the id of the entity
        """
        sl_id = [_sl.id for _sl in current.db(current.db.store_location.entity == entity_id).select(current.db.store_location.id)]
        ret = 0
        for _sl_id in sl_id:
            ret = ret + c_store_location_mapper.STORE_LOCATION_MAPPER().get_nb_storage_card(_sl_id)
        return ret

    def compute_nb_archived_storage_card(self, entity_id):
        """Get the number of archived storage cards for the given entity.

        entity_id -- the id of the entity
        """
        sl_id = [_sl.id for _sl in current.db(current.db.store_location.entity == entity_id).select(current.db.store_location.id)]
        ret = 0
        for _sl_id in sl_id:
            ret = ret + c_store_location_mapper.STORE_LOCATION_MAPPER().get_nb_archived_storage_card(_sl_id)
        return ret

    def compute_nb_user(self, entity_id):
        """Get the number of users for the given entity.

        entity_id -- the id of the entity
        """
        admin_id = [a.id for a in cc.get_admins()]
        return current.db((current.auth.settings.table_membership.group_id == entity_id) &
                          (~current.auth.settings.table_membership.user_id.belongs(tuple(admin_id)))).count()

    def compute_nb_store_location(self, entity_id):
        """Returns the number of store_locations of the given entity.

        entity_id -- the id of the entity
        """
        _count = current.db(current.db.store_location.entity == entity_id).count()

        my_logger.debug(message='_count:%s' % _count)
        return _count
