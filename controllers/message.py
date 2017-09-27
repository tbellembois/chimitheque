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
# $Id: message.py 194 2015-02-23 16:27:16Z tbellemb $
#
from datetime import datetime

from chimitheque_ide_autocomplete import *
from c_message_mapper import MESSAGE_MAPPER
import chimitheque_commons as cc


def can_delete_update(message_id):
    if message_id:
        message = db(db.message.id == int(message_id)).select(db.message.person).first()
        if message:
            return message.person == auth.user.id
        else:
            return True
    else:
        return True


@auth.requires_login()
@auth.requires(auth.has_permission('create_message') or
               auth.has_permission('admin'))
def answer():
    message_id = request.args[0]
    message = db(db.message.id == message_id).select().first()
    # we can not answer pin messages...
    if message.pin:
        return None

    # and answers are not pinnable
    db.message.pin.writable = False
    db.message.pin.readable = False
    db.message.parent.default = message_id
    db.message.topic.default = 'RE: %s' % message.topic
    return create()


@auth.requires_login()
@auth.requires(auth.has_permission('create_message') or
               auth.has_permission('admin'))
def create():
    # only admins can pin messages
    if not auth.has_permission('admin'):
        db.message.pin.writable = False
        db.message.pin.readable = False

    form = crud.create(db.message,
                       next=URL(request.application, 'message', 'close_modal', vars={"action": "create"}))
    return dict(form=form)


@auth.requires_login()
@auth.requires((auth.has_permission('create_message') and
                (can_delete_update(request.args[0]) if len(request.args) > 0 else False)) or
               auth.has_permission('admin'))
def update():
    message_id = request.args[0]
    message = db(db.message.id == message_id).select().first()
    if not message.pin:
        db.message.pin.writable = False
        db.message.pin.readable = False

    form = crud.update(db.message,
                        message_id,
                        deletable=False,
                        next=URL(request.application, 'message', 'close_modal', args=[message_id], vars={"action": "update"}))
    return dict(form=form, message_id=message_id)


@auth.requires_login()
@auth.requires((auth.has_permission('create_message') and
                (can_delete_update(request.args[0]) if len(request.args) > 0 else False)) or
               auth.has_permission('admin'))
def delete():
    message_id = request.args[0]
    form = crud.delete(db.message,
                       message_id,
                       next=URL(request.application, 'message', 'index'))
    return dict(form=form, message_id=message_id)


@auth.requires_login()
def index():
    messages = MESSAGE_MAPPER.get_message_hierarchy()
    return dict(messages=messages)


def close_modal():
    action = request.vars["action"]
    return dict(id=request.args[0] if len(request.args) > 0 else None,
                action=action)
