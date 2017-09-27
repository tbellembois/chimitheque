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
# $Id: command.py
#
from chimitheque_ide_autocomplete import *

from chimitheque_logger import chimitheque_logger
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
import chimitheque_commons as cc
from datetime import datetime

from c_entity_mapper import ENTITY_MAPPER

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("COMMAND_CREATED")
crud.messages.record_updated = cc.get_string("COMMAND_UPDATED")
crud.messages.record_deleted = cc.get_string("COMMAND_DELETED")
crud.messages.submit_button = cc.get_string("SUBMIT")

@auth.requires_login()
@auth.requires(auth.has_permission('read_com') or
               auth.has_permission('admin'))
def list():
    """List all commands."""

    # querying the database
    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    if 'request' in request.vars and request.vars['request'] == 'all':
        _query = db.command.entity.belongs(current_user_entities)
    elif 'request' in request.vars and request.vars['request'] == 'mine':
        _query = db.command.submitter==auth.user.id
    elif 'request' in request.vars and request.vars['request'] == 'new':
        status_id = db(db.command_status.label == 'New').select(db.command_status.id)
        _query = db.command.status.belongs(status_id) & db.command.entity.belongs(current_user_entities)
    elif 'request' in request.vars and request.vars['request'] == 'accepted':
        status_id = db(db.command_status.label == 'Accepted').select(db.command_status.id)
        _query = db.command.status.belongs(status_id) & db.command.entity.belongs(current_user_entities)
    else:
        status_id = db(db.command_status.state == 0).select(db.command_status.id)
        _query = db.command.status.belongs(status_id) & db.command.entity.belongs(current_user_entities)

    # pagination stuff
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v': 1},
                          anchor='main',
                          renderstyle=False)
    paginator.records = db(_query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    # querying the database
    _orderby = ~db.command.modification_datetime
    rows = db(_query).select(limitby=paginator.limitby(), orderby=_orderby)

    return dict(commands=rows, paginator=paginator, paginate_selector=paginate_selector, paginate_info=paginate_info)

@auth.requires_login()
@auth.requires(auth.has_permission('create_com') or
               auth.has_permission('admin'))
def create():
    """Create or clone a command."""

    # Clone
    if 'command_clone_id' in request.vars:
        command_clone_id = request.vars['command_clone_id']
        command_clone = db(db.command.id == command_clone_id).select().first()
        product_id = command_clone.product.id

        db.command.volume_weight.default = command_clone.volume_weight
        db.command.unit.default = command_clone.unit
        db.command.nb_items.default = command_clone.nb_items
        db.command.funds.default = command_clone.funds
        db.command.entity.default = command_clone.entity
        db.command.subteam.default = command_clone.subteam
        db.command.supplier.default = command_clone.supplier
        db.command.retailer.default = command_clone.retailer
        db.command.store_location.default = command_clone.store_location
        db.command.unit_price.default = command_clone.unit_price
        db.command.reference.default = command_clone.reference
        db.command.product_reference.default = command_clone.product_reference
        db.command.comment.default = command_clone.comment
    else:
        product_id = request.args(0)

    product = db(db.product.id == product_id).select().first()

    db.command.product.default = product_id
    status = db(db.command_status.label == 'New').select().first()
    db.command.status.default = status.id
    db.command.submitter.default = db.person[auth.user.id]
    # default to uniq entity
    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    if len(current_user_entities) == 1:
        db.command.entity.default = current_user_entities[0]

    form = SQLFORM(db.command, submit_button=cc.get_string("SUBMIT"),
                   fields=['volume_weight', 'unit', 'nb_items', 'funds', 'entity', 'subteam', 'store_location', 'supplier', 'retailer', 'unit_price', 'reference', 'product_reference', 'comment'])

    if form.accepts(request.vars, session):
        redirect(URL(a=request.application,
                     c=request.controller,
                     f='list'))
    elif form.errors:
        session.flash = DIV(cc.get_string("MISSING_FIELDS"), _class="flasherror")

    return dict(form=form, product=product, is_edit=False)

@auth.requires_login()
@auth.requires(auth.has_permission('delete_com') or
               auth.has_permission('admin'))
def delete():
    """Delete a command."""

    command_id = request.args(0)
    db(db.command.id == command_id).delete()
    session.flash = cc.get_string("COMMAND_DELETED")

    return redirect(URL(request.application, request.controller, 'list'))

@auth.requires_login()
@auth.requires(auth.has_permission('update_com') or
               auth.has_permission('admin'))
def update():
    """Update a command."""

    command_id = request.args(0)

    command = db(db.command.id == command_id).select().first()

    # Don't update a command with a final state
    if command['status'].state != 0:
        redirect(URL(a=request.application,
                     c=request.controller,
                     f='list'))

    form = SQLFORM(db.command, command, submit_button=cc.get_string("SUBMIT"),
                   fields=['status', 'volume_weight', 'unit', 'nb_items', 'funds', 'entity', 'subteam', 'store_location', 'supplier', 'retailer', 'unit_price', 'reference', 'product_reference', 'comment'])

    old_status = command.status

    if form.accepts(request.vars, session):
        # Get modified fields
        command = db(db.command.id == command_id).select().first()
        new_status = command.status

        # Integration
        if new_status.state == 1:
            barecode = STORAGE_MAPPER.create_barecode(command.product.id)
            barecode_begin = barecode[0:-1]
            barecode_number = int(barecode[-1:])

            for _ in range(command.nb_items):
                this_barecode = barecode_begin + str(barecode_number)
                db.storage.insert(product=command.product, store_location=command.store_location, volume_weight=command.volume_weight, unit=command.unit, nb_items=1,
                                  reference=command.product_reference, supplier=command.supplier, comment='', batch_number='', barecode=this_barecode)
                barecode_number = barecode_number + 1

        if old_status != new_status:
            db.command_log.insert(command=command, before_status=old_status, after_status=new_status)

            # Notify the submitter
            message = cc.get_string("COMMAND_UPDATE_MESSAGE_BODY") %(command.submitter.first_name + ' ' + command.submitter.last_name, \
                                                                     '%d X %.1f%s' % (command.nb_items, command.volume_weight, command.unit.label), \
                                                                     '%s / %s' % (command.product.cas_number, command.product.name.label), \
                                                                     T(old_status.label), T(new_status.label))

            mail_sent = mail.send(command.submitter.email, subject= cc.get_string("COMMAND_UPDATE_MESSAGE_SUBJECT"), message=message)

            if mail_sent:
                session.flash=cc.get_string("EMAIL_SENT")
            else:
                session.flash=cc.get_string("ERROR") + mail.error

        redirect(URL(a=request.application,
                     c=request.controller,
                     f='list'))
    elif form.errors:
        session.flash = DIV(cc.get_string("MISSING_FIELDS"), _class="flasherror")

    return dict(form=form, product=command.product, is_edit=True)

@auth.requires_login()
@auth.requires(auth.has_permission('read_com') or
               auth.has_permission('admin'))
def details():
    """Details on a command."""

    command_id = request.args(0)
    command = db(db.command.id == command_id).select().first()

    _orderby = ~db.command_log.log_datetime
    command_logs = db(db.command_log.command == command).select(orderby=_orderby)

    d = dict(command=command, command_logs=command_logs)

    return response.render(d)

@auth.requires_login()
def export_to_csv():

    export_list = []

    response.view = 'command/export_chimitheque.csv'

    export_header = [
                     cc.get_string('DB_PRODUCT_NAME_LABEL'),
                     cc.get_string('DB_PRODUCT_CAS_NUMBER_LABEL'),
                     cc.get_string('DB_COMMAND_SUBMITTER_LABEL'),
                     cc.get_string('DB_COMMAND_NB_ITEMS_LABEL'),
                     cc.get_string('DB_COMMAND_VOLUME_WEIGHT_LABEL'),
                     cc.get_string('DB_COMMAND_UNIT_LABEL'),
                     cc.get_string('DB_COMMAND_FUNDS_LABEL'),
                     cc.get_string('DB_COMMAND_ENTITY_LABEL'),
                     cc.get_string('DB_COMMAND_SUBTEAM_LABEL'),
                     cc.get_string('DB_COMMAND_SUPPLIER_LABEL'),
                     cc.get_string('DB_COMMAND_RETAILER_LABEL'),
                     cc.get_string('DB_COMMAND_UNIT_PRICE_LABEL'),
                     cc.get_string('DB_COMMAND_REFERENCE_LABEL'),
                     cc.get_string('DB_COMMAND_PRODUCT_REFERENCE_LABEL'),
                     cc.get_string('DB_COMMAND_COMMENT_LABEL'),
                    ]

    # querying the database
    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    if 'request' in request.vars and request.vars['request'] == 'all':
        _query = db.command.entity.belongs(current_user_entities)
    elif 'request' in request.vars and request.vars['request'] == 'mine':
        _query = db.command.submitter==auth.user.id
    elif 'request' in request.vars and request.vars['request'] == 'new':
        status_id = db(db.command_status.label == 'New').select(db.command_status.id)
        _query = db.command.status.belongs(status_id) & db.command.entity.belongs(current_user_entities)
    else:
        status_id = db(db.command_status.state == 0).select(db.command_status.id)
        _query = db.command.status.belongs(status_id) & db.command.entity.belongs(current_user_entities)

    # querying the database
    _orderby = ~db.command.modification_datetime
    rows = db(_query).select(orderby=_orderby)

    for row in rows:
	if not row.supplier:
            sup = ''
	else:
            sup = row.supplier.label
        values = (row.product.name.label, row.product.cas_number, row.submitter.last_name, row.nb_items, row.volume_weight, row.unit.label, \
                  row.funds, row.entity.role, row.subteam, sup, row.retailer, row.unit_price, row.reference, row.product_reference, row.comment)
        export_list.append(values)

    return dict(filename='command_chimitheque.csv',
                csvdata=export_list,
                field_names=export_header)


