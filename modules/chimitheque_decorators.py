# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id: chimitheque_decorators.py 194 2015-02-23 16:27:16Z tbellemb $
# -*- coding: utf-8 -*-
from chimitheque_logger import chimitheque_logger
from gluon import HTTP
from gluon import current
from types import ListType

mylogger = chimitheque_logger()


def is_store_location_deletable(function):
    '''
    store_location.py function decorator that check that the store location
    passed in parameters can be deleted
    '''
    # conditions:
    # - nb_childrens = 0
    # - nb_store_card = 0
    # - nb_archived_storage_card = 0
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_store_location_deletable')

        from c_store_location_mapper import STORE_LOCATION_MAPPER
        store_location_mapper = STORE_LOCATION_MAPPER()

        store_location = store_location_mapper.find(store_location_id=current.request.args[0])[0]
        mylogger.debug(message='store_location:%s' % store_location)

        if store_location.compute_nb_archived_storage_card() != 0 or store_location.compute_nb_storage_card() != 0 or store_location.compute_nb_children() != 0:
            mylogger.warning(message='store_location %s can not be deleted' % store_location)
            raise HTTP(403, "Not authorized")

        return function(*args, **kwargs)

    return decorator


def is_auth_user_member_of_store_location(function):
    '''
    store_location.py function decorator that check that the authenticated
    user is member of the store location passed in parameter
    (actually member of the store location's ENTITY)
    '''
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_auth_user_member_of_store_location')

        from c_store_location_mapper import STORE_LOCATION_MAPPER
        store_location_mapper = STORE_LOCATION_MAPPER()
        from c_person_mapper import PERSON_MAPPER
        person_mapper = PERSON_MAPPER()

        store_location = store_location_mapper.find(store_location_id=current.request.args[0])[0]
        user = person_mapper.find(person_id = current.auth.user.id)[0]
        mylogger.debug(message='store_location:%s' % store_location)
        mylogger.debug(message='user:%s' % user)

        if (not user.is_all_entity()) and (store_location.entity not in user.entities):
            mylogger.warning(message='store_location %s does not belong to user %s' % (store_location, user))
            raise HTTP(403, "Not authorized")

        return function(*args, **kwargs)

    return decorator


def is_entity_updatable(function):
    '''
    entity.py function decorator that check that the ENTITY passed in parameters
    can be updated
    '''
    # conditions:
    # - ENTITY != all_entity
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_entity_deletable')

        from c_entity_mapper import ENTITY_MAPPER
        entity_mapper = ENTITY_MAPPER()

        entity = entity_mapper.find(entity_id = current.request.args[0])[0]
        mylogger.debug(message='entity:%s' % entity)

        if entity.role == 'all_entity':
            mylogger.warning(message='entity "all_entity" is not deletable')
            raise HTTP(403, "Not authorized")

        return function(*args, **kwargs)

    return decorator


def is_entity_deletable(function):
    '''
    entity.py function decorator that check that the ENTITY passed in parameters
    can be deleted
    '''
    # conditions:
    # - no store location
    # - no people except the authenticated user performing the deletion if
    # he belongs to another ENTITY
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_entity_deletable')

        from c_entity_mapper import ENTITY_MAPPER
        entity_mapper = ENTITY_MAPPER()
        from c_person_mapper import PERSON_MAPPER
        person_mapper = PERSON_MAPPER()

        entity = entity_mapper.find(entity_id = current.request.args[0])[0]
        user = person_mapper.find(person_id = current.auth.user.id)[0]
        mylogger.debug(message='entity:%s' % entity)
        mylogger.debug(message='user:%s' % user)

        if entity.role == 'all_entity':
            mylogger.warning(message='entity "all_entity" is not deletable')
            raise HTTP(403, "Not authorized")

        _is_deletable = entity.compute_nb_store_location() == 0 and \
                ((entity.compute_nb_user() == 1 and entity.retrieve_users()[0] == user and user.compute_nb_entities() > 1) or \
                entity.compute_nb_user() == 0)

        if not _is_deletable:
            mylogger.warning(message='entity %s is not deletable' % entity)
            raise HTTP(403, "Not authorized")

        return function(*args, **kwargs)

    return decorator


def is_person_deletable(function):
    '''
    user.py function decorator that check that the user passed in parameters
    can be deleted
    '''
    # conditions:
    # - nb_storage_card = 0 and nb_archived_storage_card = 0
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_person_deletable')
        mylogger.debug(message='args:%s' % str(args))
        mylogger.debug(message='kwargs:%s' % str(kwargs))
        mylogger.debug(message='current.request.args:%s' % str(current.request.args))
        mylogger.debug(message='current.request.vars:%s' % str(current.request.vars))

        from c_person_mapper import PERSON_MAPPER
        person_mapper = PERSON_MAPPER()

        # current.auth.user is None while debugging with the web2py console
        if current.auth.user is None:
            mylogger.debug(message='validator is_in_same_entity passed')
            return function(*args, **kwargs)

        user = current.request.args[0] if len(current.request.args) != 0 else None
        mylogger.debug(message='person:%s' % user)

        if user is not None:
            if not person_mapper.find(person_id = user)[0].is_deletable():
                mylogger.warning(message='person %s is not deletable' % user)
                raise HTTP(403, "Not authorized")

        mylogger.debug(message='validator is_person_deletable passed')

        return function(*args, **kwargs)

    return decorator


def is_in_same_entity(function):
    '''
    user.py functions decorator that check that the authenticated user is in the same ENTITY as
    the user passed in parameters or as the entities passed in parameters
    '''
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_in_same_entity')
        mylogger.debug(message='args:%s' % str(args))
        mylogger.debug(message='kwargs:%s' % str(kwargs))
        mylogger.debug(message='current.request.args:%s' % str(current.request.args))
        mylogger.debug(message='current.request.vars:%s' % str(current.request.vars))

        # if only one ENTITY is selected, custom_entity is a string
        if type(current.request.vars['custom_entity']) is not ListType:
            _custom_entity = [ current.request.vars['custom_entity'] ]
        else:
            _custom_entity = current.request.vars['custom_entity']
        mylogger.debug(message='_custom_entity:%s' %_custom_entity)

        from c_person_mapper import PERSON_MAPPER
        person_mapper = PERSON_MAPPER()

        # admins can do everything - current.auth.user is None while debugging with the web2py console       
        if current.auth.user is None or current.auth.has_permission(name='admin'):
            mylogger.debug(message='validator is_in_same_entity passed')
            return function(*args, **kwargs)

        user = current.request.args[0] if len(current.request.args) != 0 else None
        mylogger.debug(message='user:%s' %user)

        if user is not None:
            # this is a user modification
            # checking that the authenticated user belongs to the same entities as this user
            user_entities = [ _entity.id for _entity in person_mapper.find(person_id = user)[0].entities ]
            mylogger.debug(message='user_entities:%s' %user_entities)

            for _entity in user_entities:
                mylogger.debug(message='_entity:%s' %_entity)

                if (not current.auth.has_membership(group_id=_entity)):
                    mylogger.warning(message='ENTITY %s not authorized' %_entity)
                    raise HTTP(403, "Not authorized")

        if 'custom_entity' in current.request.vars.keys():
            # the user modification has new entities (create or update call)
            # checking that the authenticated user belongs to these entities
            # note:
            # we do not include this code into the "if" below because when the form is
            # submitted after a user modification the user id is not in request.args
            user_entities = _custom_entity 

            for _entity in user_entities:
                mylogger.debug(message='_entity:%s' %_entity)

                if (not current.auth.has_membership(group_id=_entity)):
                    mylogger.warning(message='ENTITY %s not authorized' %_entity)
                    raise HTTP(403, "Not authorized")

        mylogger.debug(message='validator is_in_same_entity passed')

        return function(*args, **kwargs)

    return decorator


def has_same_permission(function):
    '''
    user.py functions decorator that
    check that the authenticated user is allowed to change the permissions
    of the user passed in parameters
    '''
    def decorator(*args, **kwargs):

        mylogger.debug(message='has_same_permission')
        mylogger.debug(message='args:%s' %str(args))
        mylogger.debug(message='kwargs:%s' %str(kwargs))
        mylogger.debug(message='current.request.args:%s' %str(current.request.args))
        mylogger.debug(message='current.request.vars:%s' %str(current.request.vars))

        from c_person_mapper import PERSON_MAPPER
        person_mapper = PERSON_MAPPER()

        # admins can do everything - current.auth.user is None while debugging with the web2py console
        if current.auth.user is None or current.auth.has_permission(name='admin'):
            mylogger.debug(message='validator has_same_permission passed')
            return function(*args, **kwargs)

        user = current.request.args[0] if len(current.request.args) != 0 else None
        mylogger.debug(message='user:%s' %user)

        if user is not None:
            # this is a user modification
            # checking that the authenticated user has the same permissions as this user
            user_permissions = person_mapper.find(person_id = user)[0].permissions

            for _permission in user_permissions:
                mylogger.debug(message='_permission:%s' %_permission)

                if (not current.auth.has_permission(_permission.name)):
                    mylogger.warning(message='permission %s not authorized' %_permission)
                    raise HTTP(403, "Not authorized")

        if 'custom_permission' in current.request.vars.keys():

            for _permission in current.request.vars['custom_permission']:
                mylogger.debug(message='_permission:%s' %_permission)

                if (not current.auth.has_permission(name=_permission)):
                    mylogger.warning(message='permission %s not authorized' %_permission)
                    raise HTTP(403, "Not authorized")

        mylogger.debug(message='validator has_same_permission passed')
        
        return function(*args, **kwargs)

    return decorator


def is_not_myself_or_admin(function):
    '''
    user.py functions decorator that performs additional permissions controls
    while updating a user
    '''
    def decorator(*args, **kwargs):

        mylogger.debug(message='is_not_myself_or_admin')
        mylogger.debug(message='args:%s' %str(args))
        mylogger.debug(message='kwargs:%s' %str(kwargs))
        mylogger.debug(message='current.request.args[0]:%s' %str(current.request.args[0]))
        mylogger.debug(message='current.auth.user.id:%s' %str(current.auth.user.id))

        user = current.request.args[0]

        # a user can not change himself
        if str(user) == str(current.auth.user.id):
            mylogger.warning(message='a user can not change himself')
            raise HTTP(403, "Not authorized")

        # admins can do everything - current.auth.user is None while debugging with the web2py console
        if current.auth.user is not None and not current.auth.has_permission(name='admin'):

            if not current.auth.has_permission(name='admin') and current.auth.has_permission(name='admin', user_id=user):
                mylogger.warning(message='non admins can not change admins')
                raise HTTP(403, "Not authorized")  

        mylogger.debug(message='validator is_not_myself_or_admin passed')

        return function(*args, **kwargs)

    return decorator
