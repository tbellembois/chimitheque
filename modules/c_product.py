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
# $Id: c_product.py 210 2015-05-11 08:46:57Z tbellemb $
#
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class PRODUCT(object):
    """Define a product."""
    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__cas_number = kwargs.get('cas_number')
        self.__ce_number = kwargs.get('ce_number')
        self.__creation_datetime = kwargs.get('creation_datetime')
        self.__person = kwargs.get('person')
        self.__name = kwargs.get('name')
        self.__synonym = kwargs.get('synonym')
        self.__restricted_access = kwargs.get('restricted_access')
        self.__specificity = kwargs.get('specificity')
        self.__td_formula = kwargs.get('td_formula')
        self.__empirical_formula = kwargs.get('empirical_formula')
        self.__linear_formula = kwargs.get('linear_formula')
        self.__msds = kwargs.get('msds')
        self.__physical_state = kwargs.get('physical_state')
        self.__class_of_compounds = kwargs.get('class_of_compounds')
        self.__hazard_code = kwargs.get('hazard_code')
        self.__symbol = kwargs.get('symbol')
        self.__signal_word = kwargs.get('signal_word')
        self.__risk_phrase = kwargs.get('risk_phrase')
        self.__safety_phrase = kwargs.get('safety_phrase')
        self.__hazard_statement = kwargs.get('hazard_statement')
        self.__precautionary_statement = kwargs.get('precautionary_statement')
        self.__disposal_comment = kwargs.get('disposal_comment')
        self.__remark = kwargs.get('remark')
        self.__is_cmr = kwargs.get('is_cmr')
        self.__is_radio = kwargs.get('is_radio')
        self.__cmr_cat = kwargs.get('cmr_cat')
        self.__has_broken_reference = kwargs.get('has_broken_reference')
        self.__broken_reference_list = kwargs.get('broken_reference_list')

        self.__is_in_entity_of = kwargs.get('is_in_entity_of')
        self.__is_in_entity_except_of = kwargs.get('is_in_entity_except_of')
        self.__has_storage_archived = kwargs.get('has_storage_archived')
        self.__has_bookmark = kwargs.get('has_bookmark')
        self.__has_history = kwargs.get('has_history')
        self.__is_orphan = kwargs.get('is_orphan')
        self.__bookmark = kwargs.get('bookmark')
        self.__unbookmark = kwargs.get('unbookmark')

    def __repr__(self):
        return '<product:%s:%s>' % (self.id, self.name)

    def __eq__(self, other):
        my_logger.debug(message='self:%s' % self)
        my_logger.debug(message='other:%s' % other)
        if self is None or other is None:
            return False
        else:
            return self.id == other.id

    @property
    def id(self):
        """Return the product id."""
        return self.__id

    @property
    def cas_number(self):
        """Return the product cas number."""
        return self.__cas_number

    @property
    def ce_number(self):
        """Return the product ce number."""
        return self.__ce_number

    @property
    def creation_datetime(self):
        """Return the product creation datetime."""
        return self.__creation_datetime

    @property
    def person(self):
        """Return the product creator as a PERSON instance."""
        return self.__person()

    @property
    def name(self):
        """Return the product name as a NAME instance."""
        return self.__name

    @property
    def synonym(self):
        """Return the product synonym(s) as a list of NAME instances."""
        return self.__synonym

    @property
    def restricted_access(self):
        """Return True if the product is restricted."""
        return self.__restricted_access

    @property
    def specificity(self):
        """Return the product specificity."""
        return self.__specificity

    @property
    def td_formula(self):
        """Return the product 3D formula."""
        return self.__td_formula

    @property
    def empirical_formula(self):
        """Return the product empirical formula."""
        return self.__empirical_formula

    @property
    def linear_formula(self):
        """Return the product linear formula."""
        return self.__linear_formula

    @property
    def msds(self):
        """Return the product MSDS."""
        return self.__msds

    @property
    def physical_state(self):
        """Return the product physical state."""
        return self.__physical_state

    @physical_state.setter
    def physical_state(self, value):
        """Set the product physical state."""
        self.__physical_state = value

    @physical_state.deleter
    def physical_state(self):
        """Delete the product physical state."""
        del self.__physical_state

    @property
    def class_of_compounds(self):
        """Return the product class of compounds."""
        return self.__class_of_compounds

    @class_of_compounds.setter
    def class_of_compounds(self, value):
        """Set the product class of compounds."""
        self.__class_of_compounds = value

    @class_of_compounds.deleter
    def class_of_compounds(self):
        """Delete the product class of compounds."""
        del self.__class_of_compounds

    @property
    def hazard_code(self):
        """Return the product hazard code."""
        return self.__hazard_code

    @hazard_code.setter
    def hazard_code(self, value):
        """Set the product hazard code."""
        self.__hazard_code = value

    @hazard_code.deleter
    def hazard_code(self):
        """Delete the product hazard code."""
        del self.__hazard_code

    @property
    def symbol(self):
        """Return the product symbol."""
        return self.__symbol

    @symbol.deleter
    def symbol(self):
        """Delete the product symbol."""
        del self.__symbol

    @symbol.setter
    def symbol(self, value):
        """Set the product symbol."""
        self.__symbol = value

    @property
    def signal_word(self):
        """Return the signal word."""
        return self.__signal_word

    @signal_word.deleter
    def signal_word(self):
        """Delete the signal word."""
        del self.__signal_word

    @signal_word.setter
    def signal_word(self, value):
        """Set the product signal word."""
        self.__signal_word = value

    @property
    def risk_phrase(self):
        """Return the risk phrase."""
        return self.__risk_phrase

    @risk_phrase.deleter
    def risk_phrase(self):
        """Delete the signal risk phrase."""
        del self.__risk_phrase

    @risk_phrase.setter
    def risk_phrase(self, value):
        """Set the product risk phrase."""
        self.__risk_phrase = value

    @property
    def safety_phrase(self):
        """Return the safety phrase."""
        return self.__safety_phrase

    @safety_phrase.deleter
    def safety_phrase(self):
        """Delete the signal safety phrase."""
        del self.__safety_phrase

    @safety_phrase.setter
    def safety_phrase(self, value):
        """Set the product safety phrase."""
        self.__safety_phrase = value

    @property
    def hazard_statement(self):
        """Return the hazard statement."""
        return self.__hazard_statement

    @hazard_statement.deleter
    def hazard_statement(self):
        """Delete the signal hazard statement."""
        del self.__hazard_statement

    @hazard_statement.setter
    def hazard_statement(self, value):
        """Set the product hazard statement."""
        self.__hazard_statement = value

    @property
    def precautionary_statement(self):
        """Return the precautionary statement."""
        return self.__precautionary_statement

    @precautionary_statement.deleter
    def precautionary_statement(self):
        """Delete the signal precautionary statement."""
        del self.__precautionary_statement

    @precautionary_statement.setter
    def precautionary_statement(self, value):
        """Set the product precautionary statement."""
        self.__precautionary_statement = value

    @property
    def disposal_comment(self):
        """Return the disposal comment."""
        return self.__disposal_comment

    @property
    def remark(self):
        """Return the remark."""
        return self.__remark

    @property
    def is_cmr(self):
        """Return True if the product is a CMR."""
        return self.__is_cmr

    @property
    def is_radio(self):
        """Return True if the product is a radioactive."""
        return self.__is_radio

    @property
    def cmr_cat(self):
        """Return True if the product CMR category."""
        return self.__cmr_cat

    @property
    def is_radio(self):
        """Return True if the product is radioactive."""
        return self.__is_radio

    @property
    def has_broken_reference(self):
        """Return True if the product has broken attributes references."""
        return self.__has_broken_reference

    @property
    def broken_reference_list(self):
        """Return the list of broken broken attributes references."""
        return self.__broken_reference_list

    #
    # methods
    #
    def is_in_entity_of(self, user_id):
        """Return True if the product is stored in one of the entities of the given user.

        user_id -- the user id
        """
        return self.__is_in_entity_of(user_id)

    def is_in_entity_except_of(self, user_id):
        """Return True if the product is stored but not in one of the entities of the given user.

        user_id -- the user id
        """
        return self.__is_in_entity_except_of(user_id)

    # TODO remove product_id parameter
    def has_storage_archived(self, product_id, user_id):
        """Return True if the product has archived storage for the given product in one of the
        entities of the given user.

        product_id -- the product id
        user_id -- the user id
        """
        return self.__has_storage_archived(product_id, user_id)

    def has_bookmark(self, user_id):
        """Return True if the product has been bookmarked by the given user.

        user_id -- the user id
        """
        return self.__has_bookmark(user_id)

    def has_history(self):
        """Return True if the product has been modified."""
        return self.__has_history

    def is_orphan(self):
        """Return True if the product as no associated storage cards."""
        return self.__is_orphan

    def bookmark(self, user_id):
        """Bookmark a product for the given user.

        user_id -- the user id
        """
        return self.__bookmark(user_id)

    def unbookmark(self, user_id):
        """Remove product bookmark for the given user.

        user_id -- the user id
        """
        return self.__unbookmark(user_id)

    def add_to_active_exposure_card(self, user):
        """Add the product to the auth user active exposure card.

        user -- the PERSON instance
        """
        return user.add_to_active_exposure_card(self)
