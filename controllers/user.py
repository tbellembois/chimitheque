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
# $Id: user.py 223 2015-07-23 13:50:59Z tbellemb2 $
#
from types import ListType
import json

from chimitheque_ide_autocomplete import *
from c_entity_mapper import ENTITY_MAPPER
from c_permission import PERMISSION
from c_person_form import PERSON_FORM
from c_person_mapper import PERSON_MAPPER
from chimitheque_decorators import is_not_myself_or_admin, is_in_same_entity, has_same_permission, is_person_deletable
from chimitheque_logger import chimitheque_logger
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
import chimitheque_commons as cc

if settings['ldap_enable']:
    import ldap

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("PERSON_CREATED")
crud.messages.record_updated = cc.get_string("PERSON_UPDATED")
crud.messages.record_deleted = cc.get_string("PERSON_DELETED")

def lang():
    """
    Set the application language
    """
    del(session.language)
    session.language = request.vars['lang']
    mylogger.debug(message='session.language:%s' %session.language)

    cache.ram.clear(regex='.*menu_')

    return redirect(URL(request.application, 'default', 'index'))

def not_authorized():
    return DIV(SPAN(cc.get_string("NOT_AUTHORIZED")))

# CRUD methods
def send_mail():
    return dict(vars=request.vars)
def verify_mail():
    return dict(vars=request.vars)
def reset_password():
    return dict(vars=request.vars)

def search_ldap():
    search = request.vars['search_user'].strip()
    if search == '': return ''
    if settings['ldap_scope'].strip().lower() == 'sub':
        scope = ldap.SCOPE_SUBTREE
    elif settings['ldap_scope'].strip().lower() == 'base':
        scope = ldap.SCOPE_BASE
    elif settings['ldap_scope'].strip().lower() == 'one':
        scope = ldap.SCOPE_ONELEVEL

    try:
        l = ldap.open(settings['ldap_hostname'])
        if settings['ldap_userdn'] and settings['ldap_userdn'].strip().lower() != 'none':
            l.simple_bind_s(settings['ldap_userdn'], settings['ldap_password'])
        else:
            l.simple_bind_s()
        ldap_search = l.search_s(settings['ldap_base'],
                                 scope,
                                 '%s=*%s*' %(settings['ldap_att_lastname'], search),
                                 [settings['ldap_att_firstname'],
                                  settings['ldap_att_lastname'],
                                  settings['ldap_att_username'],
                                  settings['ldap_att_email']])
        mylogger.debug(message='ldap_search: %s ' %ldap_search)
    except ldap.LDAPError, error_message:
        mylogger.error(message='LDAP problem: %s ' %error_message)

    if len(ldap_search) > 20:
        return DIV(cc.get_string("TOO_MANY_RESULT"))
    else:
        return DIV(*[DIV('%s %s' %(k[1][settings['ldap_att_firstname']][0], k[1][settings['ldap_att_lastname']][0]),
                    _id='user_suggestion',
                    _onclick="""
                        jQuery(function() {
                            setUserForm('%s', '%s', '%s', '%s');
                        });
                     """ %(k[1][settings['ldap_att_firstname']][0], k[1][settings['ldap_att_lastname']][0], k[1][settings['ldap_att_username']][0], k[1][settings['ldap_att_email']][0] if k[1].has_key(settings['ldap_att_email']) else '')
                     ) for k in ldap_search ])

@auth.requires_login()
def profile():

    mylogger.debug(message='request.vars:%s' %request.vars)

    person_mapper = PERSON_MAPPER()

    _person_id = auth.user.id

    _person = person_mapper.find(person_id=_person_id)[0] # an existing PERSON

    form = PERSON_FORM(person=_person, readonly_fields=[ 'email', 'creator', 'custom_permission', 'custom_entity', 'is_admin' ]).get_form()

    if form.accepts(request.vars, session, dbio=False):

        mylogger.debug(message='form.vars:%s' %form.vars)

        _person.first_name = form.vars['first_name']
        _person.last_name = form.vars['last_name']
        _person.contact = form.vars['contact']

        # saving the user
        person_mapper.save_or_update(_person)

        session.flash=cc.get_string("PERSON_UPDATED")

        redirect(URL(request.application, 'default', 'index'))

    else:

        return dict(form = form)

# decorator here not really necessary
# actions performed with the buttons listed by this function are protected
@auth.requires_login()
# @is_not_myself_or_admin
# @is_in_same_entity
def list_action():
    '''
    return actions for the PERSON given in parameter
    '''
    mylogger.debug(message='request.vars:%s' %request.vars)
    mylogger.debug(message='request.args:%s' %request.args)

    person_mapper = PERSON_MAPPER()

    _person_id = request.args[0]

    _person = person_mapper.find(person_id = _person_id)[0]

    _updatable_person = False
    _deletable_person = False
    _can_be_disabled_person = False

    # if the is_updatable method throws an HTTP exception, conditions are not met
    try:
        is_updatable()
        _updatable_person = True
        mylogger.debug(message='is updatable:%s' %_person_id)
    except HTTP:
        mylogger.debug(message='is not updatable:%s' %_person_id)

    # if the is_deletable method throws an HTTP exception, conditions are not met
    try:
        is_deletable()
        _deletable_person = True
        mylogger.debug(message='is deletable:%s' %_person_id)
    except HTTP:
        mylogger.debug(message='is not deletable:%s' %_person_id)

    # if the is_deletable method throws an HTTP exception, conditions are not met
    try:
        can_be_disabled()
        _can_be_disabled_person = True
        mylogger.debug(message='can be disabled:%s' %_person_id)
    except HTTP:
        mylogger.debug(message='can not be disabled:%s' %_person_id)

    return dict(person=_person,
                updatable_person=_updatable_person,
                deletable_person=_deletable_person,
                can_be_disabled_person=_can_be_disabled_person)

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('delete_user'))
@auth.requires_login()
@is_not_myself_or_admin
@is_in_same_entity
@is_person_deletable
def delete():

    person_mapper = PERSON_MAPPER()

    person_id = request.args[0]

    mylogger.debug(message='person_id:%s' %person_id)

    _person = person_mapper.find(person_id=person_id)[0]

    for child in  person_mapper.find(creator_id=person_id):
        child.creator = None
        person_mapper.save_or_update(child)

    person_mapper.delete(_person)

    redirect(URL(request.application, request.controller, 'list_reload.html', args=person_id, vars=request.vars))

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('select_user'))
@auth.requires_login()
def info():
    return _detail()

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('read_user'))
@auth.requires_login()
def detail():
    return _detail()

def _detail():

    mylogger.debug(message='request.vars:%s' %request.vars)

    person_mapper = PERSON_MAPPER()

    _person_id = request.args[0] if len(request.args) > 0 else None # an id or None

    if _person_id is None:
        # TODO: something cleaner
        return None

    _person = person_mapper.find(person_id=_person_id)[0] # an existing PERSON

    form = PERSON_FORM(person=_person, readonly=True).get_form()

    return dict(form=form, person=_person)

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_user'))
@is_not_myself_or_admin
@has_same_permission
@is_in_same_entity
def is_updatable():
    '''
    decorators throw an HTTP exception if conditions are not met
    '''
    return True

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('delete_user'))
@is_person_deletable
@is_not_myself_or_admin
@is_in_same_entity
def is_deletable():
    '''
    decorators throw an HTTP exception if conditions are not met
    '''
    return True

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_user'))
@is_not_myself_or_admin
@is_in_same_entity
def can_be_disabled():
    '''
    decorators throw an HTTP exception if conditions are not met
    '''
    return True

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_user'))
@auth.requires_login()
@is_not_myself_or_admin
@is_in_same_entity
def toogle_disable():

    mylogger.debug(message='request.vars:%s' %request.vars)

    person_mapper = PERSON_MAPPER()

    _person_id = request.args[0] # an id
    _person = person_mapper.find(person_id=_person_id)[0] # an existing PERSON

    if _person.is_disabled():
        _person.enable()
    else:
        _person.disable()

    # saving the user
    person_mapper.save_or_update(_person)

    session.flash=cc.get_string("PERSON_UPDATED")

    return json.dumps({'success': True})

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('update_user'))
@auth.requires_login()
@is_not_myself_or_admin
@is_in_same_entity
@has_same_permission
def update(): return _create()

@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('create_user'))
@auth.requires_login()
@is_in_same_entity
@has_same_permission
def create(): return _create()

def _create():

    mylogger.debug(message='request.vars:%s' %request.vars)
    mylogger.debug(message='request.args:%s' %request.args)

    person_mapper = PERSON_MAPPER()
    entity_mapper = ENTITY_MAPPER()

    _person_id = request.args[0] if len(request.args) > 0 else None # an id or None
    if _person_id is None:
        _person = person_mapper.create()
    else:
        _person = person_mapper.find(person_id=_person_id)[0]

    _all_entity_id = entity_mapper.find(role='all_entity')[0].id

    form = PERSON_FORM(person=_person).get_form()

    if form.accepts(request.vars, session, dbio=False):
        mylogger.debug(message='form.vars:%s' %form.vars)

        is_virtual = 'is_virtual' in request.vars
        mylogger.debug(message='is_virtual:%s' %is_virtual)

        _person.first_name = form.vars['first_name']
        _person.last_name = form.vars['last_name']
        _person.email = form.vars['email']
        _person.contact = form.vars['email'] # initializing the contact with the email address

        if 'custom_permission' in form.vars.keys():
            _person.permissions = [ PERMISSION(name=_permission_name) for _permission_name in form.vars['custom_permission'] ]

        if 'custom_entity' in form.vars.keys():
            _custom_entity = form.vars['custom_entity']
            if type(_custom_entity) is not ListType:
                _custom_entity = [ _custom_entity ]

            if str(_all_entity_id) in _custom_entity:
                _custom_entity = [ _all_entity_id ]
            _person.entities = [ entity_mapper.find(entity_id=_entity_id)[0] for _entity_id in _custom_entity ]

        if is_virtual:
            # this is a new person
            # sending an email to the creator
            message = cc.get_string("PERSON_VIRTUAL_CREATION_MESSAGE_BODY") %(_person.first_name + ' ' + \
                                                                              _person.last_name, \
                                                                              _person.email, \
                                                                              _person.password)

            _creator = person_mapper.find(person_id=auth.user.id)[0]

            # enabling the new person
            _person.enable()
            _person.virtual=True

            mail_sent = mail.send(_creator.email, subject= cc.get_string("PERSON_VIRTUAL_CREATION_MESSAGE_SUBJECT"), message=message)

            if mail_sent:
                # saving the user
                _new_person_id = person_mapper.save_or_update(_person)

                session.flash=cc.get_string("EMAIL_SENT")
            else:
                del(_person)

                session.flash=cc.get_string("ERROR") + mail.error

        # sending an email to the new user
        elif _person.new_person:

            message = cc.get_string("PERSON_CREATION_MESSAGE_BODY") %(_person.first_name + ' ' + \
                                                        _person.last_name, \
                                                        _person.email, \
                                                        settings['application_url'], \
                                                        _person.password_key)

            mail_sent = mail.send(_person.email, subject= cc.get_string("PERSON_CREATION_MESSAGE_SUBJECT"), message=message)

            if mail_sent:
                # saving the user
                _new_person_id = person_mapper.save_or_update(_person)

                session.flash=cc.get_string("EMAIL_SENT")
            else:
                del(_person)

                mylogger.error(message='mail.error:%s' % mail.error)
                session.flash=cc.get_string("ERROR") + str(mail.error)

                redirect(URL(request.application, request.controller, 'page_reload'))
        else:
            # saving the user
            _new_person_id = person_mapper.save_or_update(_person)

            session.flash=cc.get_string("PERSON_UPDATED")

        mylogger.debug(message='_person:%s' %_person)
        cc.clear_menu_cache()

        if _person_id is not None:
            redirect(URL(request.application, request.controller, 'list_reload', args=_person.id, vars=request.vars))
        else:
            redirect(URL(request.application, request.controller, 'page_reload', vars={'member': _new_person_id, 'display_by': 'person'}))

    else:

        return dict(form=form, all_entities_id=_all_entity_id)

def page_reload():

    return dict()

def list_reload():

    return dict()


@auth.requires(auth.has_permission('admin') or \
               auth.has_permission('select_user'))
@auth.requires_login()
def list():

    '''
    lists users that belongs to the same ENTITY as the authenticated user
    '''
    mylogger.debug(message='request.vars:%s' %request.vars)

    person_mapper = PERSON_MAPPER()

    _person_id = auth.user.id

    # pagination stuff
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,
                          extra_vars={'v': 1},
                          anchor='main',
                          renderstyle=False)
    paginator.records = person_mapper.count_in_same_entity(person_id=_person_id)
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    # getting the ENTITY PERSONs
    _persons = person_mapper.find_in_same_entity(person_id=_person_id, limitby=paginator.limitby())

    return dict(persons=_persons, paginator=paginator, paginate_selector=paginate_selector, paginate_info=paginate_info)
