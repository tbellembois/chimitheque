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
# $Id: shout.py 194 2015-02-23 16:27:16Z tbellemb $
#
import chimitheque_commons as cc

crud = Crud(globals(), db)
crud.messages.record_created = cc.get_string("SHOUT_CREATED")

@auth.requires_login()
def ajax_check_shout():
    session.forget()
    if auth.user:
        nb_shout = db(db.shout.receiver==auth.user.id).count()
        return str(nb_shout)
    else:
        return 0

@auth.requires_login()
def load():
    session.forget()
    shouts = db(db.shout.receiver==auth.user.id).select(orderby=db.shout.sender|db.shout.creation_datetime)
    return dict(shouts=shouts)

@auth.requires_login()
def forget():
    db((db.shout.receiver==auth.user.id) & (db.shout.sender==request.args[0])).delete()
    db.commit()
    return redirect(URL(request.application, request.controller, 'close_modal'))

@auth.requires_login()
def create():
    db.shout.receiver.default = request.args[0]
    form = crud.create(db.shout,
        next=URL(request.application, request.controller, 'close_modal'))
    db((db.shout.receiver==auth.user.id) & (db.shout.sender==request.args[0])).delete()
    db.commit()
    return dict(form=form)

def close_modal():
    return dict()
