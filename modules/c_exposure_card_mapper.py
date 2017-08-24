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
from c_exposure_card import EXPOSURE_CARD
from c_exposure_item_mapper import EXPOSURE_ITEM_MAPPER
from gluon import current
from types import ListType


my_logger = chimitheque_logger()


class EXPOSURE_CARD_MAPPER(object):
    """Database exposure card table mapper.

    Request the database to create EXPOSURE_CARD instances.
    """
    def __init__(self):
        self.__exposure_item_mapper = EXPOSURE_ITEM_MAPPER()

    def _exposure_card_from_row(self, _exposure_card_row):
        """Return an EXPOSURE_CARD instance from a row.
        """
        return EXPOSURE_CARD(id=_exposure_card_row['id'],
                             title=_exposure_card_row['title'],
                             accidental_exposure_type=_exposure_card_row['accidental_exposure_type'],
                             accidental_exposure_datetime=_exposure_card_row['accidental_exposure_datetime'],
                             accidental_exposure_duration_and_extent=_exposure_card_row['accidental_exposure_duration_and_extent'],
                             creation_datetime=_exposure_card_row['creation_datetime'],
                             modification_datetime=_exposure_card_row['modification_datetime'],
                             archive=_exposure_card_row['archive'],
                             exposure_items=lambda: self.__exposure_item_mapper.find(_exposure_card_row['exposure_item'], orderby=current.db.name.label_nost))

    def find(self, exposure_card_id=None, orderby=None):
        """Select exposure cards in the database.

        exposure_card_id -- search by exposure_card_id or list of ids
        """
        my_logger.debug(message='exposure_card_id:%s' % exposure_card_id)
        query_list = []

        if exposure_card_id is not None:
            if type(exposure_card_id) is ListType:
                query_list.append(current.db.exposure_card.id.belongs(exposure_card_id))
            else:
                query_list.append(current.db.exposure_card.id == exposure_card_id)

        final_query = (current.db.exposure_card.id > 0)

        # building the final query
        for query in query_list:
            my_logger.debug(message='query:%s' % str(query))
            final_query = final_query.__and__(query)

        # getting the exposure_card in the db
        _exposure_card_rows = current.db(final_query).select(current.db.exposure_card.ALL, orderby=orderby)
        my_logger.debug(message='_exposure_card_rows:%s' % str(_exposure_card_rows))

        if len(_exposure_card_rows) == 0:
            return []
        else:
            return [self._exposure_card_from_row(_exposure_card_row) for _exposure_card_row in _exposure_card_rows]

    def delete(self, exposure_card):
        """Delete an exposure_card.

        exposure_card -- an EXPOSURE_ITEM instance
        return: the last row id
        """
        # deleting exposure items references
        current.db(current.db.exposure_item.id.belongs(exposure_card.exposure_items)).delete()

        # deleting person references
        exposure_card_owner = current.db(current.db.person.exposure_card.contains(exposure_card.id)).select().first()
        _new_exposure_cards = [ec_id for ec_id in exposure_card_owner.exposure_card if ec_id != exposure_card.id]
        exposure_card_owner.update_record(exposure_card=_new_exposure_cards)

        _id = current.db(current.db.exposure_card.id == exposure_card.id).delete()
        current.db.commit()

        return _id

    def update(self, exposure_card): # EXPOSURE_CARD type

        if isinstance(exposure_card.id, (int, long)):
            _is_new = False
        else:
            _is_new = True
        my_logger.debug(message='exposure_card:%s' % str(exposure_card))
        my_logger.debug(message='_is_new:%s' % _is_new)

        # updating the exposure_items first
        # we could only update the changed items...
        ei_ids = []
        for ei in exposure_card.exposure_items:
            ei_ids.append(self.__exposure_item_mapper.update(ei))
        my_logger.debug(message='ei_ids:%s' % str(ei_ids))

        if _is_new:
            _id = current.db.exposure_card.insert(title=exposure_card.title,
                                            archive=exposure_card.archive,
                                            accidental_exposure_type=exposure_card.accidental_exposure_type,
                                            accidental_exposure_datetime=exposure_card.accidental_exposure_datetime,
                                            accidental_exposure_duration_and_extent=exposure_card.accidental_exposure_duration_and_extent,
                                            exposure_item=ei_ids)

        else:
            row = current.db(current.db.exposure_card.id == exposure_card.id).select().first()

            row.update_record(title=exposure_card.title,
                              archive=exposure_card.archive,
                              accidental_exposure_type=exposure_card.accidental_exposure_type,
                              accidental_exposure_datetime=exposure_card.accidental_exposure_datetime,
                              accidental_exposure_duration_and_extent=exposure_card.accidental_exposure_duration_and_extent,
                              exposure_item=ei_ids)

            _id = exposure_card.id

        current.db.commit()

        return _id
