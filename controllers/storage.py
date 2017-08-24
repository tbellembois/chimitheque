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
# $Id: storage.py 205 2015-04-08 13:40:27Z tbellemb $
#
from datetime import date, datetime
import json
import re

from c_entity_mapper import ENTITY_MAPPER
from c_product_mapper import PRODUCT_MAPPER
from c_storage_mapper import STORAGE_MAPPER
from c_store_location_mapper import STORE_LOCATION_MAPPER
from chimitheque_logger import chimitheque_logger
import chimitheque_commons as cc

from fake import *

my_logger = chimitheque_logger()

crud.messages.record_created = cc.get_string("STORAGE_CREATED")
crud.messages.record_updated = cc.get_string("STORAGE_UPDATED")
crud.messages.record_deleted = cc.get_string("STORAGE_DELETED")

@auth.requires(auth.has_permission('create_sup') or
               auth.has_permission('admin'))
@auth.requires_login()
def ajax_add_vendor():
    my_logger.debug(message='request.vars:%s' % request.vars)
    label = request.vars['text']
    if len(label) == 0:
        return '1;' + cc.get_string("ENTER_A_LABEL")

    # check that the coc does NOT already exists
    count = db(db.supplier.label == label).count()
    if count != 0:
        return '1;' + cc.get_string("SUPPLIER_ALREADY_EXIST")
    else:
        _id = db.supplier.insert(label=label)
        return '0;' + str(_id)


def clean_unit(form):

    my_logger.debug(message='clean_unit')
    if form.vars['volume_weight'] is None:
        form.vars['unit'] = None


def generate_barecode(form):

    my_logger.debug(message='generate_barecode')
    product_id = form.element('[name=product]').attributes['_value']
    form.vars.barecode = cc.create_barecode(product_id)


def duplicate_storage(form):

    my_logger.debug(message='duplicate_storage')
    my_logger.debug(message='form.vars:%s' % form.vars)
    del form.vars['id']
    for key in form.vars.keys():
        m = re.match("(?P<uid>.+):search", key)
        if m:
            uid = m.group('uid')
            del form.vars['%s:search' % uid]

    barecode = form.vars['barecode']
    barecode_begin = barecode[0:-1]
    barecode_number = int(barecode[-1:])

    nb_items = form.vars['nb_items'] if form.vars['nb_items'] else 1
    for i in range(1, nb_items):
        barecode_number = barecode_number + 1
        form.vars['barecode'] = barecode_begin + str(barecode_number)
        db.storage.insert(**dict(form.vars))

    db.commit()


def create_stock(form):

    _product = PRODUCT_MAPPER().find(form.vars['product'])[0]
    _store_location = STORE_LOCATION_MAPPER().find(form.vars['store_location'])[0]
    _entity_id = _store_location.entity.id
    if db((db.stock.product == _product.id) &
          (db.stock.entity == _entity_id)).count() == 0:
        db.stock.insert(product=_product.id, entity=_entity_id)
        db.commit()


@auth.requires(auth.has_permission('read_sc') or auth.has_permission('admin'))
@auth.requires_login()
def detail():

    history = 'history' in request.vars
    archive = 'archive' in request.vars and request.vars['archive']
    my_logger.debug(message='history:%s' % history)
    my_logger.debug(message='archive:%s' % archive)

    _id = request.args(0)

    if history:
        storage = STORAGE_MAPPER().find(storage_history_id=_id, history=history)[0]
    else:
        storage = STORAGE_MAPPER().find(storage_id=_id, archive=archive)[0]

    return dict(storage=storage,
                is_history=history,
                is_archive=archive)

@auth.requires(auth.has_permission('read_sc') or auth.has_permission('admin'))
@auth.requires_login()
def label():

    storage_id = request.args(0)

    storage = STORAGE_MAPPER().find(storage_id=storage_id, archive=None)[0]

    return dict(storage=storage)

@auth.requires(auth.has_permission('read_sc') or auth.has_permission('admin'))
@auth.requires_login()
def list_history():

    storage_id = request.args(0)

    storages = STORAGE_MAPPER().find(storage_id=storage_id, history=True)

    return dict(storages=storages)

@auth.requires(auth.has_permission('read_archive') or auth.has_permission('admin'))
@auth.requires_login()
def list_archive():

    product_id = request.args(0)

    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    my_logger.debug(message='user_entities:%s' % current_user_entities)

    storages = STORAGE_MAPPER().find(entity_id=current_user_entities, product_id=product_id, archive=True)

    request.vars['archive'] = True

    return dict(storages=storages,
                product_id=product_id)

# No cache because the output depend the user
#@cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
@auth.requires(auth.has_permission('read_sc') or auth.has_permission('admin'))
@auth.requires_login()
def list():

    my_logger.debug(message='request.vars:%s' %request.vars)

    product_id = request.args[0] if len(request.args)>0 else request.vars['product_id']
    my_logger.debug(message='product_id:%s' %product_id)

    if product_id is None:
        return 'foo'

    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    my_logger.debug(message='user_entities:%s' % current_user_entities)

    storages = STORAGE_MAPPER().find(product_id=product_id, entity_id=current_user_entities)

    d = dict(storages=storages,
             product_id=product_id)

    return response.render(d)

@auth.requires(auth.has_permission('select_sc') or auth.has_permission('admin'))
@auth.requires_login()
def list_other_entity():

    product_id = request.args(0)

    current_user_entities = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]
    my_logger.debug(message='user_entities:%s' % current_user_entities)

    entities = ENTITY_MAPPER().find(entity_id=current_user_entities,
                                    negate_id_search=True,
                                    product_id=product_id)

    return dict(entities=entities,
                product_id=product_id)

@auth.requires(auth.has_permission('delete_sc') or auth.has_permission('admin'))
@auth.requires_login()
def delete():

    storage_id = request.args[0]

    my_logger.debug(message='storage_id:%s' %storage_id)

    storage_mapper = STORAGE_MAPPER()
    _storage = storage_mapper.find(storage_id=storage_id, archive=None)[0]

    if _storage.archive:
        my_logger.debug(message='storage is archive')
        storage_mapper.delete(_storage)
    else:
        my_logger.debug(message='storage is NOT archive')
        _storage.archive=True
        _storage.to_destroy=False
        _storage.exit_datetime=datetime.now()
        storage_mapper.update(_storage)

        # un-borrow the storage if needed
        db(db.borrow.storage==storage_id).delete()

        # updating the STOCK
        # if there's no more active storage for this product and this entity, delete the stock
        product_id = _storage.product.id
        entity_id = _storage.store_location.entity.id
        nb_remain_storage = db((db.product.id == product_id) & (db.storage.product == db.product.id) & (db.storage.archive == False) &
                               (db.storage.store_location == db.store_location.id) & (db.store_location.entity == entity_id)).count()
        if nb_remain_storage == 0:
            db((db.stock.product == product_id) & (db.stock.entity == entity_id)).delete()
        #update_stock(None, storage=_storage, delete=True)

    request.vars['storage']=storage_id

    cache.ram.clear(regex='.*/storage/list')
    cache.ram.clear(regex='.*/product/details')

    return storage_id

@auth.requires(auth.has_permission('update_sc') or auth.has_permission('admin'))
@auth.requires_login()
def destroy():

    storage_id = request.args[0]

    my_logger.debug(message='storage_id:%s' %storage_id)

    storage_mapper = STORAGE_MAPPER()
    _storage = storage_mapper.find(storage_id=storage_id)[0]

    _storage.to_destroy=True
    _storage.exit_datetime=datetime.now()

    STORAGE_MAPPER().update(_storage)

    cache.ram.clear(regex='.*/storage/list')

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True})

@auth.requires(auth.has_permission('update_sc') or auth.has_permission('admin'))
@auth.requires_login()
def undestroy():

    storage_id = request.args[0]

    my_logger.debug(message='storage_id:%s' %storage_id)

    storage_mapper = STORAGE_MAPPER()
    _storage = storage_mapper.find(storage_id=storage_id)[0]

    _storage.to_destroy=False
    _storage.exit_datetime=None

    STORAGE_MAPPER().update(_storage)

    cache.ram.clear(regex='.*/storage/list')

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True})

@auth.requires(auth.has_permission('create_sc') or auth.has_permission('admin'))
@auth.requires_login()
def clone():
    my_logger.debug(message='request.vars:%s' %request.vars)
    storage_id = request.args(0)
    user_entity = [_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)]

    storage_to_update = db(db.storage.id == storage_id).select().first()
    product_id = storage_to_update.product
    db.storage.product.default = storage_to_update.product
    db.storage.volume_weight.default = storage_to_update.volume_weight
    db.storage.unit.default = storage_to_update.unit
    db.storage.comment.default = storage_to_update.comment
    db.storage.reference.default = storage_to_update.reference
    db.storage.batch_number.default = storage_to_update.batch_number
    db.storage.supplier.default = storage_to_update.supplier

    # getting the user store locations ids
    my_logger.debug(message='user_entity:%s' %user_entity)
    rows = db(db.store_location.entity.belongs(tuple(user_entity))).select(db.store_location.id) or None
    user_store_location_ids = [ row.id for row in rows ] if rows else None
    my_logger.debug(message='user_store_location_ids:%s' %user_store_location_ids)

    # the user as no store locations - leaving...
    if not user_store_location_ids:
        # TODO return an error
        pass

    # creating the form
    db.storage.product.widget.attributes['_disabled']='disabled'
    form=crud.create(db.storage,
                     next=URL(request.application,
                                     'product',
                                     'details_reload',
                                     args=product_id,
                                     vars={'load_storage_list': True}),
#                     onvalidation=lambda theform: (generate_barecode(theform)),
                     onaccept=lambda form: (duplicate_storage(form),
                                            #update_stock(form)
                                            ))

    if form.errors:
        session.flash=DIV(cc.get_string("MISSING_FIELDS"), _class="flasherror")

    cache.ram.clear(regex='.*/storage/list')
    cache.ram.clear(regex='.*/product/details')

    return dict(product_id = product_id,
                form=form)

@auth.requires(auth.has_permission('create_sc') or auth.has_permission('admin'))
@auth.requires_login()
def create():
    my_logger.debug(message='request.vars:%s' % request.vars)
    product_id = request.args(0)
    db.storage.product.default = product_id
    db.storage.barecode.default = cc.create_barecode(product_id)

    # creating the form
    db.storage.product.widget.attributes['_disabled'] = 'disabled'
    form = crud.create(db.storage,
                            next=URL(request.application,
                                     'product',
                                     'details_reload',
                                     args=product_id,
                                     vars={'load_storage_list': True}),
                             onvalidation=lambda form: clean_unit(form),
#                             onvalidation=lambda form: (clean_unit(form),
#                                                        generate_barecode(form)),
                             onaccept=lambda form: (duplicate_storage(form),
                                                    create_stock(form)))

    if form.errors:
        session.flash=DIV(cc.get_string("MISSING_FIELDS"), _class="flasherror")

    cache.ram.clear(regex='.*/storage/list')
    cache.ram.clear(regex='.*/product/details')

    return dict(product_id = product_id,
                form=form)


def update_storage_person(form):
    form.vars['person'] = auth.user.id


def save_storage_store_location(form):
    form.vars['old_store_location_id'] = db(db.storage.id==request.args[0]).select(db.storage.store_location).first().store_location


@auth.requires(auth.has_permission('update_sc') or auth.has_permission('admin'))
@auth.requires_login()
def update():
    storage_id = request.args[0]

    _storage = STORAGE_MAPPER().find(storage_id)[0]

    # creating the form
    db.storage.product.widget.attributes['_disabled']='disabled'
    form=crud.update(db.storage,
                     storage_id,
                     next=URL(request.application,
                             'product',
                             'details_reload',
                             args=_storage.product.id,
                             vars={'load_storage_list': True}),
                     onvalidation=lambda theform: (update_storage_person(theform), save_storage_store_location(theform)),
                     onaccept=lambda theform: (auth.archive(theform,
                                                            archive_table=db.storage_history,
                                                            archive_current=False),
                                               ),
                     ondelete=lambda theform: (auth.archive(theform, archive_table=db.storage_history, archive_current=False)))

    if form.errors:
        session.flash=DIV(cc.get_string("MISSING_FIELDS"), _class="flasherror")

    cache.ram.clear(regex='.*/storage/list')
    cache.ram.clear(regex='.*/product/details')

    return dict(storage_id = storage_id,
                product_id = _storage.product.id,
                form=form)
