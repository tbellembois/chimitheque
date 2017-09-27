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
from chimitheque_logger import chimitheque_logger
from gluon import current

my_logger = chimitheque_logger()


class MESSAGE_MAPPER(object):
    """Database message table mapper.

    Request the database for messages.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_child_message(message_id, depth):

        child_messages = current.db(current.db.message.parent==message_id).select(orderby=current.db.message.id)

        return [ [depth + 1, child_message.id, get_child_message(child_message.id, depth + 1)] for child_message in child_messages ]


    @staticmethod
    def get_message_hierarchy():

        root_messages_pin = current.db((current.db.message.parent==None) & 
                                   (current.db.message.pin==True) & 
                                   (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.creation_datetime)
        root_messages_not_pin = current.db((current.db.message.parent==None) & 
                                   (current.db.message.pin==False) &
                                   (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.creation_datetime)

        message_pin_id_hierarchy = flatten([[0, message.id, get_child_message(message.id, 0)] for message in root_messages_pin ])
        message_not_pin_id_hierarchy = flatten([[0, message.id, get_child_message(message.id, 0)] for message in root_messages_not_pin ])

        message_hierarchy = []
        for depth, message_id in chunks(message_pin_id_hierarchy + message_not_pin_id_hierarchy, 2):
            message_hierarchy.append((depth, current.db(current.db.message.id==message_id).select().first()))

        return message_hierarchy


    @staticmethod
    def get_pin_message():

        messages = current.db((current.db.message.pin==True) & (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.id)

        return messages

