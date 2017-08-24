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
# $Id: c_person_mapper.py 224 2015-07-23 13:53:22Z tbellemb2 $
#
from gluon import current

from gluon.validators import CRYPT
from types import ListType
from chimitheque_logger import chimitheque_logger
from c_person import PERSON
from c_permission import PERMISSION
from c_exposure_card_mapper import EXPOSURE_CARD_MAPPER
import c_entity_mapper


my_logger = chimitheque_logger()


class PERSON_MAPPER(object):
    """Database person table mapper.

    Request the database to create PERSON instances.
    """
    def __init__(self):
        self.entity_mapper = c_entity_mapper.ENTITY_MAPPER()
        self.exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    def _person_from_row(self, _person_row):
        """Return a PERSON instance from a Row.
        """
        return PERSON(id=_person_row['id'],
                      new_person=False,
                      first_name=_person_row['first_name'],
                      last_name=_person_row['last_name'],
                      # creator = id if an admin modifies himself
                      creator=lambda: self.find(person_id=_person_row['creator'])[0]
                      if (_person_row['creator'] is not None) and (_person_row['creator'] != _person_row['id']) \
                      else None,
                      email=_person_row['email'],
                      contact=_person_row['contact'],
                      creation_date=_person_row['creation_date'],
                      archive=_person_row['archive'],
                      virtual=_person_row['virtual'],
                      registration_key=_person_row['registration_key'],
                      permissions=lambda: self.find_permissions(_person_row['id']),
                      exposure_cards=lambda: self.exposure_card_mapper.find(exposure_card_id=_person_row['exposure_card'])
                      if _person_row['exposure_card'] is not None \
                      else [],
                      entities=lambda: self.entity_mapper.find(person_id=_person_row['id']),
                      has_product_in_active_exposure_card=lambda product: self.has_product_in_active_exposure_card(product, _person_row['id']),
                      compute_nb_storage_card=lambda: self.compute_nb_storage_card(_person_row['id']),
                      compute_nb_archived_storage_card=lambda: self.compute_nb_archived_storage_card(_person_row['id']))

    def find(self, person_id=None, entity_id=None, creator_id=None, permission_name=None, orderby=None):
        """Select persons in the database.

           The query parameters can be combined.
           example: search person with id in [1, 2, 3] that belongs to entity with with id 35.

           person_id -- search by person_id or list of ids
           entity_id -- search by entity id or list of ids
           creator_id -- search by creator id
           permission_name -- search by permission name such as 'delete_sc'
           returns: a list of PERSON
        """
        my_logger.debug(message='person_id:%s' % person_id)
        query_list = []

        if person_id is not None:
            if type(person_id) is ListType:
                query_list.append(current.db.person.id.belongs(person_id))
            else:
                query_list.append(current.db.person.id == person_id)
        if entity_id is not None:
            if type(entity_id) is ListType:
                query_list.append((current.db.membership.group_id.belongs(entity_id)) &
                                  (current.db.person.id == current.db.membership.user_id))
            else:
                query_list.append((current.db.membership.group_id == entity_id) &
                                  (current.db.person.id == current.db.membership.user_id))
        if creator_id is not None:
            query_list.append(current.db.person.creator == creator_id)

        if permission_name is not None:
            query_list.append((current.auth.settings.table_permission.name == permission_name) &
                              (current.auth.settings.table_membership.group_id == current.auth.settings.table_permission.group_id) &
                              (current.auth.settings.table_user.id == current.auth.settings.table_membership.user_id))

        final_query = (current.db.person.id > 0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        # getting the PERSON in the db
        _person_rows = current.db(final_query).select(current.db.person.ALL, orderby=orderby)
        my_logger.debug(message='_person_rows:%s' % str(_person_rows))

        if len(_person_rows) == 0:
            return []
        else:
            return [self._person_from_row(_person_row) for _person_row in _person_rows]


    def delete(self, person):
        """Delete a person.

        person -- an PERSON instance
        return: the last row id
        """
        _id = current.db(current.db.person.id == person.id).delete()
        current.db.commit()

        return _id


    def create(self):
        """Create a person.

        return: a PERSON instance
        """
        return PERSON(id=None,
                      new_person=True,
                      creator=lambda: self.find(person_id=current.auth.user.id)[0] if current.auth.user else None)


    def count_in_same_entity(self, person_id):
        """Return the number of users that belongs to the same
        ENTITY(ies) as the given person.

        person_id -- the id of the person
        """
        _all_entity_id = current.db(current.db.entity.role == 'all_entity').select(current.db.entity.id).first().id
        _person_id_entity = current.db(current.db.membership.user_id == person_id).select(current.db.membership.group_id)

        if _all_entity_id in ((_g.group_id) for _g in _person_id_entity):
            _count = current.db(current.db.person).count()
        else:
            _count = current.db((current.db.membership.group_id.belongs((_g.group_id) for _g in _person_id_entity)) &
                                (current.db.person.id == current.db.membership.user_id)).count()

        return _count


    def find_in_same_entity(self, person_id, limitby=None):
        """Return the users that belongs to the same
        ENTITY(ies) as the given person.

        person_id -- the id of the person
        return: a list of PERSON
        """
        _all_entity_id = current.db(current.db.entity.role == 'all_entity').select(current.db.entity.id).first().id
        _person_id_entity = current.db(current.db.membership.user_id == person_id).select(current.db.membership.group_id)

        if _all_entity_id in ((_g.group_id) for _g in _person_id_entity):
            _person_rows = current.db(current.db.person).select(current.db.person.ALL,
                                                                orderby=current.db.person.last_name,
                                                                limitby=limitby)
        else:
            _person_rows = current.db((current.db.membership.group_id.belongs((_g.group_id) for _g in _person_id_entity)) &
                                      (current.db.person.id == current.db.membership.user_id)).select(current.db.person.ALL,
                                                                                                      distinct=True,
                                                                                                      orderby=current.db.person.last_name,
                                                                                                      limitby=limitby)

        return [self._person_from_row(_person_row) for _person_row in _person_rows] \
               if _person_rows is not None \
               else None


    def find_permissions(self, person_id):
        """Return the permissions of the given person.

        person_id -- the id of the person
        return: a list of PERMISSION
        """
        _person_personnal_group = current.auth.user_group(person_id)
        return [PERMISSION(name=_permission_row['name']) \
                            for _permission_row in \
                            current.db(current.auth.settings.table_permission.group_id == _person_personnal_group).select(current.auth.settings.table_permission.name)]


    def save_or_update(self, person):  # PERSON type
        """Save or update the person into the database.

        person: a PERSON instance
        """
        if not person.new_person:

            my_logger.debug(message='not person.is_new')
            # we pass the registration_key for the disable/enable feature
            _ret = current.db(current.auth.settings.table_user.id == person.id).update(first_name=person.first_name,
                                                                              last_name=person.last_name,
                                                                              email=person.email,
                                                                              contact=person.contact,
                                                                              registration_key=person.registration_key)
        else:
            my_logger.debug(message='person.is_new')
            # inserting the user in the DB
            _user_table = current.auth.settings.table_user
            person.id = current.db['%s' % _user_table].insert(
                                                            creator=person.creator.id,
                                                            first_name=person.first_name,
                                                            last_name=person.last_name,
                                                            email=person.email,
                                                            contact=person.contact,
                                                            virtual=person.virtual,
                                                            password=CRYPT(key=current.auth.settings.hmac_key,
                                                                           min_length=current.auth.settings.password_min_length)(person.password)[0],
                                                            registration_key=person.registration_key,
                                                            reset_password_key=person.password_key)

            _ret = person.id

            # inserting his personal group
            _personal_group_id = current.auth.add_group(current.auth.settings.create_user_groups % person.id)

            # making him belonging to his personal group
            _membership_table = current.auth.settings.table_membership
            current.db['%s' % _membership_table].insert(user_id=person.id, group_id=_personal_group_id)

        # updating the user membership
        self.update_membership(person)
        # updating the user permission
        self.update_permission(person)

        # not sure that it is necessary...
        current.db.commit()

        return _ret


    def compute_nb_storage_card(self, user_id):
        """Returns the number of storage cards of the given user.

        user_id -- the id of the user
        """
        count = current.db((current.db.storage.person == user_id) &
                        (current.db.storage.archive == False)).count()

        my_logger.debug(message='count:%s' % count)
        return count


    def compute_nb_archived_storage_card(self, user_id):
        """Returns the number of storage cards of the given user.

        user_id -- the id of the user
        """
        count = current.db((current.db.storage.person == user_id) &
                        (current.db.storage.archive == True)).count()

        my_logger.debug(message='count:%s' % count)
        return count

    def has_product_in_active_exposure_card(self, product, user_id):
        """Return True if the given product is in the user active exposure card.

        product -- a PRODUCT instance to search
        """
        return current.db((current.db.exposure_item.product==product.id) &
                  (current.db.exposure_card.exposure_item.contains(current.db.exposure_item.id)) &
                  (current.db.person.exposure_card.contains(current.db.exposure_card.id)) &
                  (current.db.person.id==user_id)).count() != 0

    def update_exposure_card(self, person):
        """
        Update the database exposure cards of the given user.

        person -- a PERSON instance
        """
        my_logger.debug(message='person:%s' % person)
        user_id = person.id

        ec_ids = []
        my_logger.debug(message='ec_ids:%s' % ec_ids)
        for ec in person.exposure_cards:
            ec_ids.append(self.exposure_card_mapper.update(ec))

        current.db(current.auth.settings.table_user.id==person.id).update(exposure_card=ec_ids)

        current.db.commit()

    def update_permission(self, person):
        """
        Update the database permissions of the given user.

        person -- a PERSON instance
        """
        user_id = person.id
        permissions = person.permissions

        # getting the current permissions
        current_permissions = self.find_permissions(user_id)
        my_logger.debug(message='permissions:%s' % permissions)
        my_logger.debug(message='current_permissions:%s' % current_permissions)
        user_personal_group = current.auth.user_group(user_id)
        my_logger.debug(message='user_personal_group:%s' % user_personal_group)

        # deleting permissions if needed
        for current_permission in current_permissions:
            if not current_permission in permissions:
                my_logger.debug(message='deleting permission %s for user_personal_group %s' % (current_permission, user_personal_group))
                current.auth.del_permission(group_id=user_personal_group, name=current_permission.name)

        # adding permissions if needed
        for permission in permissions:
            my_logger.debug(message='current.auth.has_permission(name=%s, user_id=%s):%s' % (permission, user_id, current.auth.has_permission(name=permission.name, user_id=user_id)))
            if permission.name != 'custom_permission_hidden' and (not current.auth.has_permission(name=permission.name, user_id=user_id)) and (current.auth.has_permission(permission.name) or current.auth.has_permission('admin')):
                my_logger.debug(message='adding permission %s for user_personal_group %s' % (permission, user_id))
                my_logger.debug(message='current.auth.settings.table_user_name: %s' % current.auth.settings.table_user_name)
                if permission.name != 'impersonate':
                    current.auth.add_permission(group_id=user_personal_group, name=permission.name)
                else:
                    current.auth.add_permission(group_id=user_personal_group, name=permission.name, table_name=current.auth.settings.table_user_name)


    def update_membership(self, person):
        """Update the database membership of the given user.

        person: a PERSON instance
        """
        user_id = person.id
        entity_ids = [_entity.id for _entity in person.entities]
        # getting the current membership
        current_memberships = current.db(current.auth.settings.table_membership.user_id == user_id).select(current.auth.settings.table_membership.group_id)
        current_group_ids = [current_membership.group_id for current_membership in current_memberships]
        user_personal_group = current.auth.user_group(user_id)
        my_logger.debug(message='current_group_ids:%s' % current_group_ids)

        # deleting the membership if needed - except personal membership
        for current_group_id in current_group_ids:
            if (not (str(current_group_id) in entity_ids)) and (current_group_id != user_personal_group):
                my_logger.debug(message='deleting group_id %s for user %s' % (current_group_id, user_id))
                current.auth.del_membership(group_id=current_group_id, user_id=user_id)

        # adding the membership if needed
        for group_id in entity_ids:
            if not current.auth.has_membership(group_id=group_id, user_id=user_id):
                my_logger.debug(message='adding group_id %s for user %s' % (group_id, user_id))
                current.auth.add_membership(group_id=group_id, user_id=user_id)
