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
# $Id: entity.py 195 2015-02-25 09:51:08Z tbellemb $
#
from c_entity_mapper import ENTITY_MAPPER
from c_person_mapper import PERSON_MAPPER
from chimitheque_decorators import is_entity_deletable, is_entity_updatable
from chimitheque_logger import chimitheque_logger
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
import chimitheque_commons as cc

from fake import *

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("ENTITY_CREATED")
crud.messages.record_updated = cc.get_string("ENTITY_UPDATED")
crud.messages.record_deleted = cc.get_string("ENTITY_DELETED")
crud.messages.submit_button = cc.get_string("SUBMIT")


@auth.requires_login()
def list():
    '''
    lists entities of the authenticated user
    '''
    mylogger.debug(message='request.vars:%s' % request.vars)

    entity_mapper = ENTITY_MAPPER()
    person_mapper = PERSON_MAPPER()

    # getting the authenticated user
    auth_user = person_mapper.find(person_id=auth.user.id)[0]

    # pagination stuff
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v': 1},
                          anchor='main',
                          renderstyle=False)
    paginator.records = entity_mapper.count_all() if auth_user.is_all_entity() \
                                                  else auth_user.compute_nb_entities()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    # if the authenticated user is in all entities (ie. 'all_entity' entity)
    # retrieving the whole entitities
    if auth_user.is_all_entity():
        auth_user_entitites = entity_mapper.find(limitby=paginator.limitby())
    # else getting the authenticated user entitities
    else:
        auth_user_entitites = entity_mapper.find(person_id=auth.user.id, limitby=paginator.limitby())
        # adding the all_entity entity for the whole users
        auth_user_entitites.insert(0, entity_mapper.find(role='all_entity')[0])
        mylogger.debug(message='auth_user_entitites:%s' % auth_user_entitites)

    # putting 'all_entity' at the top of the list
    auth_user_entitites = sorted(auth_user_entitites, key=lambda k: k.role if k.role != 'all_entity' else '0_%s' % k.role)

    return dict(entities=auth_user_entitites, paginator=paginator, paginate_selector=paginate_selector, paginate_info=paginate_info)


@auth.requires_login()
@auth.requires(auth.has_permission('admin') or
               auth.has_permission('select_user'))
def list_user():
    '''
    lists users that belongs to the entity given in parameter
    '''
    mylogger.debug(message='request.vars:%s' % request.vars)

    person_mapper = PERSON_MAPPER()

    _entity_id = request.args[0]

    # getting the entity persons
    _persons = person_mapper.find(entity_id=_entity_id)

    return dict(persons=_persons)


@auth.requires_login()
@auth.requires(auth.has_permission('admin') or
               auth.has_permission('create_ent'))
def create():
    '''
    create a new entity
    '''
    person_mapper = PERSON_MAPPER()
    auth_user = person_mapper.find(person_id=auth.user.id)[0]

    db.entity.role.default = ''
    form = crud.create(db.entity,
                       onaccept=lambda form: (auth.add_membership(group_id=form.vars.id) if not auth_user.is_all_entity() else None,
                                              cc.clear_menu_cache()),
                       next=URL(request.application, request.controller, 'page_reload', vars=request.vars))

    cc.clear_menu_cache()

    return dict(form=form)


def page_reload():

    return dict()


@auth.requires_login()
@is_entity_updatable
@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_ent'))
@auth.requires(auth.has_permission('admin') or \
               (auth.has_membership(request.args[0]) if len(request.args) > 0 else True) or \
               auth.has_membership(db(db.entity.role == 'all_entity').select(db.entity.id).first().id))
def update():
    '''
    update one of the authenticated user entity
    '''
    form = crud.update(db.entity,
                       request.args(0),
                       onaccept=cc.clear_menu_cache(),
                       next=URL(request.application,
                                request.controller,
                                'list_reload',
                                args=request.args(0),
                                vars=request.vars))

    cc.clear_menu_cache()

    return dict(form=form)


def list_reload():
    return dict()


# decorator here not really necessary
# actions performed with the buttons listed by this function are protected
@auth.requires_login()
def list_action():
    '''
    return actions for the entity given in parameter
    '''
    mylogger.debug(message='request.vars:%s' % request.vars)

    entity_mapper = ENTITY_MAPPER()

    _entity_id = request.args[0]

    _entity = entity_mapper.find(entity_id=_entity_id)[0]

    _updatable_entity = False
    _deletable_entity = False

    # if the is_updatable method throws an HTTP exception, conditions are not met
    try:
        is_updatable()
        _updatable_entity = True
        mylogger.debug(message='is updatable:%s' % _entity_id)
    except HTTP:
        mylogger.debug(message='is not updatable:%s' % _entity_id)

    # if the is_deletable method throws an HTTP exception, conditions are not met
    try:
        is_deletable()
        _deletable_entity = True
        mylogger.debug(message='is deletable:%s' % _entity_id)
    except HTTP:
        mylogger.debug(message='is not deletable:%s' % _entity_id)

    session.flash = None

    return dict(entity=_entity,
                updatable_entity=_updatable_entity,
                deletable_entity=_deletable_entity)


@auth.requires_login()
@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('delete_ent'))
@auth.requires(auth.has_permission('admin') or \
               (auth.has_membership(request.args[0]) if len(request.args) > 0 else True) or \
               auth.has_membership(db(db.entity.role == 'all_entity').select(db.entity.id).first().id))
@is_entity_deletable
def is_deletable():
    '''
    decorators throw an HTTP exception if conditions are not met
    '''
    return True


@auth.requires_login()
@is_entity_updatable
@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_ent'))
@auth.requires(auth.has_permission('admin') or \
               (auth.has_membership(request.args[0]) if len(request.args) > 0 else True) or \
               auth.has_membership(db(db.entity.role == 'all_entity').select(db.entity.id).first().id))
def is_updatable():
    '''
    decorators throw an HTTP exception if conditions are not met
    '''
    return True


@auth.requires_login()
@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('delete_ent'))
@auth.requires(auth.has_permission('admin') or \
               (auth.has_membership(request.args[0]) if len(request.args) > 0 else True) or \
               auth.has_membership(db(db.entity.role == 'all_entity').select(db.entity.id).first().id))
@is_entity_deletable
def delete():
    entity_mapper = ENTITY_MAPPER()

    entity_id = request.args[0]

    mylogger.debug(message='entity_id:%s' %entity_id)

    _entity = entity_mapper.find(entity_id=entity_id)[0]

    entity_mapper.delete(_entity)

    cc.clear_menu_cache()

    redirect(URL(request.application, request.controller, 'list_reload.html', args=entity_id, vars=request.vars))


@auth.requires_login()
def search():
    mylogger.debug(message='request.vars:%s' % str(request.vars))
    mylogger.debug(message='request.args:%s' % str(request.args))

    # some init
    query_list = []
    rows = None
    persons = None
    entities = None
    paginator = ''
    paginate_selector = ''
    paginate_info = ''
    nb_entries = 1  # number of results
    label = ''  # request title, ie. "products in the Chemical Lab.
    page = int(request.vars['page']) if 'page' in request.vars else 0
    result_per_page = int(request.vars['result_per_page']) if 'result_per_page' in request.vars else 10
    connected_user_entity_ids = db(db.entity.id.belongs([_entity.id for _entity in ENTITY_MAPPER().find(person_id=auth.user.id)])).select(cacheable=True)

    # no way to pass the "keep_last_search" variable while clicking on a "x results per page" link
    if 'paginate' in request.vars:
        request.vars['keep_last_search'] = True

    #
    # restoring session vars if keep_last_search
    #
    if 'keep_last_search' in request.vars:
        if session.search_display_by:
            request.vars['display_by'] = session.search_display_by
        if session.search_person_id:
            request.vars['member'] = session.search_member
        if session.search_role:
            request.vars['role'] = session.search_role
        del request.vars['keep_last_search']

    #
    # and then cleaning up request vars
    #
    for key in ['search_display_by',
                'search_member',
                'search_role']:
        if session.has_key(key):
            mylogger.debug(message='key:%s' %str(key))
            mylogger.debug(message='session[key]:%s' %str(session[key]))
            del session[key]
    mylogger.debug(message='request.vars:%s' %str(request.vars))

    #
    # display by entity or person
    #
    if 'display_by' in request.vars and request.vars['display_by'] == 'person':
        session.search_display_by = 'person'
        display_by_person = True
    else:
        display_by_person = False

    session.search_result_per_page = result_per_page
    session.search_page = page

    #
    # building the request
    #
    if 'member' in request.vars and request.vars['member'] != '':

        mylogger.debug(message='case 1')
        session.search_member = request.vars['member']

        _person_entity_ids = db(db.entity.id.belongs([_entity.id for _entity in ENTITY_MAPPER().find(person_id=request.vars['member'])])).select(cacheable=True)
        _common_entity_ids = [_id for _id in _person_entity_ids if _id in connected_user_entity_ids]

        if len(_common_entity_ids) > 0:
            if display_by_person:
                query_list.append(db.person.id == request.vars['member'])
            else:
                query_list.append(db.entity.id.belongs(_common_entity_ids))

    elif 'role' in request.vars and request.vars['role'] != '':

        mylogger.debug(message='case 2')
        session.search_role = request.vars['role']

        if display_by_person:
            query_list.append((db.entity.role.like('%s%%' %request.vars['role'].strip())) | (db.entity.role.like('%%%s%%' %request.vars['role'].strip())))
            query_list.append(db.membership.group_id.belongs(connected_user_entity_ids))
            query_list.append(db.membership.group_id == db.entity.id)
            query_list.append(db.membership.user_id == db.person.id)
        else:
            query_list.append((db.entity.role.like('%s%%' %request.vars['role'].strip())) | (db.entity.role.like('%%%s%%' %request.vars['role'].strip())))
            query_list.append(db.membership.group_id.belongs(connected_user_entity_ids))
            query_list.append(db.membership.group_id == db.entity.id)

    else:

        mylogger.debug(message='case 3')

        if display_by_person:
            # Need to get users without entities
            #query_list.append(db.membership.group_id.belongs(connected_user_entity_ids))
            query_list.append(db.membership.user_id == db.person.id)
        else:
            query_list.append(db.entity.id.belongs(connected_user_entity_ids))

        #request.vars['member'] = auth.user.id

    if len(query_list) != 0:

        finalQuery = query_list[0]

        for query in query_list[1:]:
            mylogger.debug(message='query:%s' %str(query))
            finalQuery = finalQuery.__and__(query)
        mylogger.debug(message='finalQuery:%s' %str(finalQuery))

        if display_by_person:
            _distinct = db.person.id
        else:
            _distinct = db.entity.id

        #
        # pagination
        #
        range_min = page * result_per_page
        range_max = range_min + result_per_page
        mylogger.debug(message='page:%s' %page)
        mylogger.debug(message='result_per_page:%s' %result_per_page)
        mylogger.debug(message='range_min:%s' %range_min)
        mylogger.debug(message='range_min:%s' %range_max)

        theset = db(finalQuery)
        nb_entries = theset.count(distinct=_distinct)
        mylogger.debug(message='nb_entries:%i' %nb_entries)

        paginate_selector = PaginateSelector(anchor='main')
        paginator = Paginator(paginate=paginate_selector.paginate,
                              extra_vars={'keep_last_search': True},
                              anchor='main',
                              renderstyle=False)
        paginator.records = nb_entries
        paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

        #
        # executing the query
        #
        _limitby = paginator.limitby()

        if display_by_person:
            _orderby = db.person.email
            select_fields = [db.person.ALL]
        else:
            _orderby = db.entity.role
            select_fields = [db.entity.ALL]

        allrows = theset.select(*select_fields,
                                orderby=_orderby,
                                distinct=True,
                                limitby=_limitby,
                                cacheable=True)

        rows = allrows
        mylogger.debug(message='len(rows):%s' % len(rows))
        for row in rows:
            mylogger.debug(message='row:%s' % row)

        if len(rows) > 0:
            if not display_by_person:
                entities = ENTITY_MAPPER().find(entity_id=[row.id for row in rows], orderby=_orderby)
                mylogger.debug(message='len(entities):%s' % len(entities))
            else:
                persons = PERSON_MAPPER().find(person_id=[row.id for row in rows], orderby=_orderby)
                mylogger.debug(message='len(persons):%s' % len(persons))

    #
    # building the search form
    #
    db.entity.role.widget = SQLFORM.widgets.string.widget
    #db.person.email.widget=CHIMITHEQUE_MULTIPLE_widget(db.person.email, configuration={'*': {'disable_validate': True}})

    # prepopulating form values + default values in the following form declaration
    db.entity.role.default = request.vars['role']
    #db.person.email.default = request.vars['member']
    db.entity.role.label = cc.get_string('SEARCH_ENTITY_NAME')
    #db.person.email.label = cc.get_string('SEARCH_PERSON_EMAIL')

    form = SQLFORM.factory(db.entity.role,
                           Field('member',
                                 'reference person',
                                 default=request.vars['member'],
                                 label=cc.get_string('SEARCH_ENTITY_MEMBER'),
                                 widget=CHIMITHEQUE_MULTIPLE_widget(db.person.email, configuration={'*': {'disable_validate': True}})),
                           _action='/%s/%s/search' %(request.application, request.controller),
                           submit_button=cc.get_string("SEARCH"))

    return dict(form=form,
                persons=persons,
                entities=entities,
                nb_entries=nb_entries,
                label=label,
                paginator=paginator,
                paginate_selector=paginate_selector,
                paginate_info=paginate_info)


