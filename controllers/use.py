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
# $Id: use.py 194 2015-02-23 16:27:16Z tbellemb $
#
from c_storage_mapper import STORAGE_MAPPER
from chimitheque_logger import chimitheque_logger
import chimitheque_commons as cc

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("BORROWING_CREATED")
crud.messages.record_updated = cc.get_string("BORROWING_UPDATED")
crud.messages.record_deleted = cc.get_string("BORROWING_DELETED")
crud.messages.delete_label = cc.get_string("CHECK_TO_GIVE_BACK")


@auth.requires(auth.has_permission('admin') or auth.has_permission('read_sc'))
@auth.requires_login()
def create_update():
    storage_id = request.args[0]
    if db(db.borrow.storage == storage_id).count() > 0:
        return update()
    else:
        return create()


@auth.requires(auth.has_permission('admin') or auth.has_permission('read_sc'))
@auth.requires_login()
def create():
    storage_id = request.args[0]

    db.borrow.storage.default = storage_id
    db.borrow.borrower.default = auth.user.id

    _storage = STORAGE_MAPPER().find(storage_id=storage_id)[0]

    form = crud.create(db.borrow,
                       next=URL(request.application,
                                'product',
                                'details_reload',
                                args=_storage.product.id,
                                vars={'load_storage_list': True}))

    cache.ram.clear(regex='.*/storage/list')

    return dict(storage_id=storage_id,
                form=form)


@auth.requires(auth.has_permission('admin') or auth.has_permission('read_sc'))
@auth.requires_login()
def update():
    storage_id = request.args[0]

    use_id = db(db.borrow.storage == storage_id).select(db.borrow.id).first().id

    db.borrow.borrower.default = auth.user.id

    _storage = STORAGE_MAPPER().find(storage_id=storage_id)[0]

    form = crud.update(db.borrow, use_id,
                                next=URL(request.application,
                                'product',
                                'details_reload',
                                args=_storage.product.id,
                                vars={'load_storage_list': True}))

    cache.ram.clear(regex='.*/storage/list')

    return dict(storage_id=storage_id,
                form=form)
