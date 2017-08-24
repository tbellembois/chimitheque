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
# $Id: store_location.py 201 2015-03-04 13:08:14Z tbellemb $
#
from c_store_location_mapper import STORE_LOCATION_MAPPER
from chimitheque_decorators import is_auth_user_member_of_store_location
from chimitheque_decorators import is_store_location_deletable
from chimitheque_logger import chimitheque_logger
import chimitheque_commons as cc
from gluon.html import XML

from fake import *

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("STORE_LOCATION_CREATED")
crud.messages.record_updated = cc.get_string("STORE_LOCATION_UPDATED")
crud.messages.record_deleted = cc.get_string("STORE_LOCATION_DELETED")
crud.messages.submit_button = cc.get_string("SUBMIT")


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('read_sl'))
@auth.requires((auth.has_membership('all_entity') or
                auth.has_membership(request.vars['entity']))
                if len(request.vars) != 0 and request.vars['entity'] != '' else True)
@auth.requires_login()
def ajax_get_entity_store_location_options():
    '''
    returns store locations of the ENTITY given in parameters
    as HTML select options
    '''
    mylogger.debug(message='request.vars:%s' % request.vars)

    _entity_id = request.vars['entity']

    store_location_mapper = STORE_LOCATION_MAPPER()
    _store_locations = store_location_mapper.find(entity_id=_entity_id)
    mylogger.debug(message='_store_locations:%s' % _store_locations)

    # hum... not sure this is a very clean way to unblock the UI and set the style...
    _result = "<script>$('select#store_location_parent').css('border', '4px solid yellow');</script><option value=''></option>"
    if _store_locations is not None:
        for _store_location in _store_locations:
            # str(_store_location.full_path) if full_path is None (should never happen) to concatenate strings
            _result += "<option value='" + str(_store_location.id) + "'>" + str(_store_location.full_path) + "</option>"

    return XML(_result)


def list_reload():

    return dict()


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('read_sl'))
@auth.requires((auth.has_membership('all_entity') or
                auth.has_membership(request.args[0])) \
               if len(request.args) != 0 else False)
@auth.requires_login()
def list_entity():
    '''
    lists store locations of the given ENTITY
    '''
    mylogger.debug(message='request.vars:%s' % request.vars)

    store_location_mapper = STORE_LOCATION_MAPPER()

    _entity_id = request.args[0]

    _store_locations = store_location_mapper.find(entity_id=_entity_id, orderby=db.store_location.label_full_path)

    return dict(store_locations=_store_locations)


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('create_sl'))
@auth.requires_login()
def create():

    form = crud.create(db.store_location,
                       onaccept=lambda form: cc.clear_menu_cache(),
                       next=URL(request.application, request.controller, 'page_reload', vars=request.vars))

    return dict(form=form)


def page_reload():

    return dict()


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('update_sl'))
@auth.requires_login()
@is_auth_user_member_of_store_location
def update():

    mylogger.debug(message='request.vars:%s' % request.vars)

    _store_location_id = request.args[0]

    form = crud.update(db.store_location,
                       _store_location_id,
                       onaccept=lambda form: cc.clear_menu_cache(),
                       next=URL(request.application,
                                request.controller,
                                'update_childrens_full_path',
                                args=request.args[0]))

    return dict(form=form)


def update_childrens_full_path():

    store_location_id = request.args[0]
    mylogger.debug(message='store_location_id:%s' % store_location_id)

    store_location_mapper = STORE_LOCATION_MAPPER()

    _store_location = store_location_mapper.find(store_location_id=store_location_id)[0]

    # updating childrens full path
    for _children in _store_location.retrieve_children():

        mylogger.debug(message='_children:%s' % _children)
        _children.compute_and_set_full_path()
        store_location_mapper.update(_children)

    # and current store location full path
    #_store_location.compute_and_set_full_path()
    #store_location_mapper.update(_store_location)

    cc.clear_menu_cache()

    redirect(URL(request.application,
                 request.controller,
                 'list_reload',
                 args=_store_location.entity.id))


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('delete_sl'))
@auth.requires_login()
@is_auth_user_member_of_store_location
@is_store_location_deletable
def delete():

    store_location_id = request.args[0]

    store_location_mapper = STORE_LOCATION_MAPPER()

    _store_location = store_location_mapper.find(store_location_id=store_location_id)[0]

    form = crud.delete(db.store_location,
                       store_location_id,
                       next=URL(request.application,
                                request.controller,
                                'list_reload',
                                args=_store_location.entity.id))

    cc.clear_menu_cache()

    return dict(form=form)


@auth.requires(auth.has_permission('admin') or
               auth.has_permission('read_sl'))
@auth.requires_login()
@is_auth_user_member_of_store_location
def read():

    form = crud.read(db.store_location,
                     request.args(0))
    return dict(form=form)
