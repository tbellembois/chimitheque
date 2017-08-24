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
# $Id: c_person.py 224 2015-07-23 13:53:22Z tbellemb2 $
#
from time import time, strftime
from chimitheque_logger import chimitheque_logger
from gluon.utils import web2py_uuid
from datetime import datetime
from c_permission import PERMISSION
from c_entity import ENTITY
from c_exposure_card import EXPOSURE_CARD

my_logger = chimitheque_logger()


class PERSON(object):
    """Define a person.

    A user belongs to one or several entities.
    """
    def __init__(self, id=None, new_person=True, **kwargs):

        self.__uuid = web2py_uuid()  # uid to debug instance creation - not present in DB
        self.__new_person = new_person  # flag to help user creation/update - not present in DB
        self.__id = id  # id not inserted in DB in the commit method
        self.__first_name = kwargs.get('first_name')
        self.__last_name = kwargs.get('last_name')
        self.__email = kwargs.get('email')
        self.__contact = kwargs.get('contact')
        self.__password = str(int(time())) + '-' + web2py_uuid()  # generating a random password
        self.__password_key = str(int(time())) + '-' + web2py_uuid()  # generating a random password key
        self.__registration_key = kwargs.get('registration_key') if 'registration_key' in kwargs else ''
        self.__creation_date = datetime.now()
        self.__virtual = kwargs.get('virtual') if 'virtual' in kwargs else False
        self.__archive = False  # a user is never deleted but archived
        self.__creator = kwargs.get('creator')  # lambda that returns a PERSON instance - see the get_creator method
        self.__permissions = kwargs.get('permissions') if 'permissions' in kwargs else []  # lambda that returns a [ PERMISSIONS ]
        self.__entities = kwargs.get('entities') if 'entities' in kwargs else []  # lambda that returns a [ ENTITIES ]
        self.__exposure_cards = kwargs.get('exposure_cards') if 'exposure_cards' in kwargs else []  # lambda that returns a [ EXPOSURE_CARD ]
        self.__has_product_in_active_exposure_card = kwargs.get('has_product_in_active_exposure_card')

        self.__compute_nb_storage_card = kwargs.get('compute_nb_storage_card')  # lambda that returns a int
        self.__compute_nb_archived_storage_card = kwargs.get('compute_nb_archived_storage_card')  # lambda that returns a int

    def __repr__(self):
        return '<PERSON:%s (uuid=%s) (id=%s) (registration_key=%s) exposure_cards:%s>' % (self.email,
                                                                   self.__uuid,
                                                                   self.id,
                                                                   self.__registration_key,
                                                                   self.exposure_cards)

    def __eq__(self, other):
        try:
            assert isinstance(other, PERSON), "%s is not a Person" % other
            if self is None or other is None:
                return False
            else:
                return self.email == other.email
        except AssertionError:
            pass

    #
    # attributes
    #
    @property
    def id(self):
        """Return the person id."""
        return self.__id

    @id.setter
    def id(self, value):
        """Set the person id."""
        self.__id = value

    @property
    def creator(self):
        """Return the person creator.

        returns: a PERSON
        """
        return self.__creator()

    @creator.setter
    def creator(self, value):
        """Set the person creator."""
        self.__creator = value

    @property
    def password(self):
        """Return the person password."""
        return self.__password

    @property
    def password_key(self):
        """Return the person password key."""
        return self.__password_key

    @property
    def registration_key(self):
        """Return the person registration key."""
        return self.__registration_key

    @registration_key.setter
    def registration_key(self, value):
        """Set the person registration key."""
        self.__registration_key = value

    @property
    def first_name(self):
        """Return the person first name."""
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        """Set the person first name."""
        self.__first_name = value

    @property
    def last_name(self):
        """Return the person last_name."""
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        """Set the person last name."""
        self.__last_name = value

    @property
    def email(self):
        """Return the person email."""
        return self.__email

    @email.setter
    def email(self, value):
        """Set the person email."""
        self.__email = value

    @property
    def contact(self):
        """Return the person contact."""
        return self.__contact

    @contact.setter
    def contact(self, value):
        """Set the person contact."""
        self.__contact = value

    @property
    def creation_date(self):
        """Return the person creation date."""
        return self.__creation_date

    @property
    def virtual(self):
        """Return True if the person is virtual.

        A virtual person is a generic account can may
        be used by several users.
        """
        return self.__virtual

    @virtual.setter
    def virtual(self, value):
        """Set the person virtual attribute."""
        self.__virtual = value

    @property
    def archive(self):
        """Return True if the person is archived."""
        return self.__archive

    @property
    def permissions(self):
        """Return the person permissions.

        returns: a list of PERMISSION
        """
        try:
            return self.__permissions()
        except TypeError:
            return self.__permissions

    @permissions.setter
    def permissions(self, permissions=[]):
        """Set the person permissions.

        permissions -- a list of PERMISSION
        """
        # admins can impersonate (web2py feature)
        if PERMISSION(name='admin') in permissions:
            permissions.append(PERMISSION(name='impersonate'))

        self.__permissions = permissions

    @property
    def new_person(self):
        """Return True if the person is new.

        A new person is not yet present in the database.
        """
        return self.__new_person

    @property
    def entities(self):
        """Return the person entities.

        returns: a list of ENTITY
        """
        try:
            return self.__entities()
        except TypeError:
            return self.__entities

    @entities.setter
    def entities(self, entities=[]):
        """Set the person entities.

        entities -- a list of ENTITY
        """

        self.__entities = entities

    @property
    def exposure_cards(self):
        """Return the person exposure cards.

        returns: a list of EXPOSURE_CARD
        """
        try:
            return self.__exposure_cards()
        except TypeError:
            return self.__exposure_cards

    @exposure_cards.setter
    def exposure_cards(self, value):
         self.__exposure_cards = value

    #
    # methods
    #
    def compute_nb_storage_card(self):
        """Return the number of storage cards of the person."""
        return self.__compute_nb_storage_card()

    def compute_nb_archived_storage_card(self):
        """Return the number of archived storage cards of the person."""
        return self.__compute_nb_archived_storage_card()

    def compute_nb_entities(self):
        """Return the number of entities the person belongs to."""
        return len(self.entities)

    def is_disabled(self):
        """Return True if the person has been disabled by an administrator."""
        return self.registration_key == 'blocked' or self.registration_key == 'disabled'

    def is_admin(self):
        """Return True if the person is an administrator."""
        return PERMISSION(name='admin') in self.permissions

    def is_all_entity(self):
        """Return True if the person belongs to all entities.

        An administrator automatically belongs to all entities.
        """
        _entities = self.entities
        my_logger.debug(message='_entities:%s' % _entities)
        return _entities is not None and \
               (ENTITY(name='all_entity') in _entities)

    def is_deletable(self):
        """Return True if the person can be deleted.

        A person is deletable if she has no storage cards and no archived storage cards.
        """
        return self.compute_nb_storage_card() == 0 and self.compute_nb_archived_storage_card() == 0

    def disable(self):
        """Disable the person."""
        self.registration_key = 'disabled'

    def enable(self):
        """Enable the person."""
        self.registration_key = ''

    def has_permission(self, permission):
        """Return True if the person is the person has the given permission.

        permission -- the PERMISSION to check
        """
        return permission in self.permissions

    def create_exposure_card(self, **kwargs):
        """Create a new exposure card and add it to the person exposure cards.
        Make it active if no active card is present.

        returns: the new created EXPOSURE_CARD
        """
        if self.exposure_cards is None or len(self.exposure_cards) == 0:
            self.exposure_cards = [EXPOSURE_CARD(**kwargs)]
        else:
            if self.get_active_exposure_card() is None:
                # append method does not work
                self.exposure_cards = self.exposure_cards + [EXPOSURE_CARD(**kwargs)]
            else:
                self.exposure_cards = self.exposure_cards + [EXPOSURE_CARD(archive=True, **kwargs)]

        return self.exposure_cards[-1]

    def get_active_exposure_card(self):
        """Return the current active exposure card (ie. not archived).

        Only one exposure card per user is active. This must be ensured outside this class.

        returns: an EXPOSURE_CARD
        """
        my_logger.debug(message='self.exposure_cards:%s' % self.exposure_cards)
        if self.exposure_cards is None or len(self.exposure_cards) == 0:
            _title = strftime("%c")
            self.create_exposure_card(title=_title)

        card_list = filter(lambda card: card.archive == False, self.exposure_cards)
        my_logger.debug(message='card_list:%s' % card_list)

        return card_list[0] if len(card_list) > 0 else None

    def has_product_in_active_exposure_card(self, product):
        """Return True if the given product is in the user active exposure card.

        product -- a PRODUCT instance to search
        """
        return self.__has_product_in_active_exposure_card(product)
        #active_exposure_card = self.get_active_exposure_card()

        #if active_exposure_card is None:
        #    return False
        #else:
        #    return active_exposure_card.has_product(product)

    def add_to_active_exposure_card(self, product):
        """Add the given product to the user active exposure card.

        product -- the PRODUCT to add
        """
        active_exposure_card = self.get_active_exposure_card()
        my_logger.debug(message='active_exposure_card:%s' % active_exposure_card)

        if active_exposure_card is None:
            my_logger.debug(message='no active exposure card, creating a new one')
            self.create_exposure_card()
            active_exposure_card = self.get_active_exposure_card()
            #TODO: to be improved

        return active_exposure_card.add_exposure_item_for_product(product)
