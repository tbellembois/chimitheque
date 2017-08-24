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
# $Id: supplier.py 194 2015-02-23 16:27:16Z tbellemb $
#
from chimitheque_logger import chimitheque_logger
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
import chimitheque_commons as cc

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("SUPPLIER_CREATED")
crud.messages.record_updated = cc.get_string("SUPPLIER_UPDATED")
crud.messages.record_deleted = cc.get_string("SUPPLIER_DELETED")
crud.messages.submit_button = cc.get_string("SUBMIT")

@auth.requires(auth.has_permission('admin') or 
               auth.has_permission('read_sup'))
@auth.requires_login()
def list():

    # building the query
    _query = db.supplier
    _orderby = db.supplier.label

    # pagination stuff
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v': 1},
                          anchor='main',
                          renderstyle=False)
    paginator.records = db(_query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    # querying the database
    rows = db(_query).select(limitby=paginator.limitby(),
                             orderby=_orderby) 

    return dict(rows=rows, paginator=paginator, paginate_selector=paginate_selector, paginate_info=paginate_info)

@auth.requires(auth.has_permission('admin') or 
               auth.has_permission('create_sup'))
@auth.requires_login()
def create():
    db.supplier.label.default=''
    form=crud.create(db.supplier, next=URL(request.application, 'supplier', 'list'))
    return dict(form=form)

@auth.requires(auth.has_permission('admin') or auth.has_permission('update_sup'))
@auth.requires_login()
def update():
    form=crud.update(db.supplier,
                     request.args(0),
                     next=URL(request.application,
                              request.controller,
                              'list',
                              vars=request.vars,
                              args=request.args))
    return dict(form=form)

@auth.requires(auth.has_permission('admin') or auth.has_permission('read_sup'))
@auth.requires_login()
def read():
    form=crud.read(db.supplier, request.args(0))
    return dict(form=form)

@auth.requires(auth.has_permission('admin') or auth.has_permission('delete_sup'))
@auth.requires_login()
def delete():
    form = crud.delete(db.supplier,
                       request.args[0],
                       next=URL(request.application,
                                request.controller,
                                'list',
                                vars=request.vars,
                                args=request.args))

    return dict(form=form)
