# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id: chimitheque_validators.py 206 2015-04-17 09:30:32Z tbellemb $
from c_entity_mapper import ENTITY_MAPPER
from c_store_location_mapper import STORE_LOCATION_MAPPER
from chimitheque_ide_autocomplete import *
from chimitheque_logger import chimitheque_logger
from chimitheque_permission import Permission
from gluon import current
from gluon.validators import IS_IN_DB
from gluon.validators import IS_UPPER
from gluon.validators import Validator
import chimitheque_commons as cc
import chimitheque_strings as cs
import copy
import string

mylogger = chimitheque_logger()


class IS_ONE_SELECTED(object):
    def __init__(self, db=None, table=None, table_set=None, tuple_list=None):
        mylogger.debug(message='__init__')
        self.db = db
        self.table = table
        self.table_set = table_set
        self.tuple_list = tuple_list
    def __call__(self, value):
        mylogger.debug(message='__call__')
        mylogger.debug(message='value:%s' %value)
        if value and value != '' and len(value) != 0:
            return (value, None)
        else:
            return (value, 'enter a value')
    def formatter(self, value):
        return value
    def options(self):
        if self.db:
            if self.table_set:
                rows = self.db(self.table_set).select()
            else:
                rows = self.db(self.table).select()
            return [ (r.id, self.table._format(r)) for r in rows ]
        else:
            return [ l for l in self.tuple_list ]

class IS_VALID_EMPIRICAL_FORMULA(object):
    def __init__(self):
        mylogger.debug(message='__init__')
    def __call__(self, value):
        mylogger.debug(message='__call__')
        mylogger.debug(message='value:%s' %value)
        _value,error=cc.sort_empirical_formula(value)
        if not error:
            mylogger.debug(message='_value:%s' %_value)
            mylogger.debug(message='error:%s' %error)
            return (_value, None)
        else:
            return (value, error)
    def formatter(self, value):
        return value

class IS_UPPER_NAME(IS_UPPER):
    def __init__(self):
        mylogger.debug(message='__init__')
        super(IS_UPPER_NAME, self).__init__()
    def __call__(self, value):
        mylogger.debug(message='type(value):%s' %type(value))
        if '@' in value:
            myval = string.split(value, '@')
            last, error = super(IS_UPPER_NAME, self).__call__(myval[1])
            return ('%s@%s' %(myval[0], last), None)
        else:
            return super(IS_UPPER_NAME, self).__call__(value)
    def formatter(self, value):
        return value

class IS_VALID_CAS(object):
    def __init__(self):
        mylogger.debug(message='__init__')
    def __call__(self, value):
        mylogger.debug(message='__call__')
        mylogger.debug(message='value:%s' %value)
        return cc.is_cas_number(value)

    def formatter(self, value):
        return value

class IS_UNIQUE_WITH_SPECIFICITY(object):
    def __init__(self, specificity, function):
        mylogger.debug(message='__init__')
        self.specificity = specificity
        self.function = function
    def __call__(self, value):
        mylogger.debug(message='__call__')
        mylogger.debug(message='value:%s' %value)
        if value is None or value == '0000-00-0':
            return (value, None)
        if self.function == 'create':
            rows = current.db((current.db.product.cas_number==value) & (current.db.product.specificity==self.specificity)).select(current.db.product.id)
            if rows and len(rows)!=0:
                return (value, cc.get_string("DB_PRODUCT_CAS_NUMBER_COMMENT"))
            else:
                return (value, None)
        else:
            return (value, None)

    def formatter(self, value):
        return value


class IS_IN_DB_AND_SELECTED_ENTITY(IS_IN_DB):
    """
    store location "parent" field validator
    """

    def __init__(self, *args1, **args2):
        super(IS_IN_DB_AND_SELECTED_ENTITY, self).__init__(*args1, **args2)
        mylogger.debug(message='self.__dict__:%s' % str(self.__dict__))

    @property
    def dbset(self):
        return self.__dict__['dbset']

    @dbset.setter
    def dbset(self, v):
        # do NOT use self.varname !
        #http://docs.python.org/2/reference/datamodel.html#object.__setattr__
        self.__dict__['dbset'] = v

    def __call__(self, value):
        # while creating a new store location, self.dbset returns no store locations
        # cf. options method
        # we have then to reinitialize it to avoid a "value not in db" error
        self.dbset = current.db(current.db.store_location)
        return super(IS_IN_DB_AND_SELECTED_ENTITY, self).__call__(value)

    def options(self, *args1, **args2):
        _store_location_id=current.request.args[0] if len(current.request.args) != 0 \
                                                   else None

        # retrieving the ENTITY id of the current store location
        if _store_location_id is not None:
            selected_entity = STORE_LOCATION_MAPPER().find(store_location_id=_store_location_id)[0].entity.id
        else:
            selected_entity = None

        if selected_entity is not None:
            # retrieving the store locations that belongs to the same ENTITY
            self.dbset = current.db((current.db.store_location.entity==selected_entity) &
                                    (~(current.db.store_location.id==_store_location_id)))
        else:
            # while creating a new store location, request.args[0] does not exist
            self.dbset = current.db(current.db.store_location.id==-1)

        return super(IS_IN_DB_AND_SELECTED_ENTITY, self).options(*args1, **args2)


class IS_IN_DB_AND_USER_STORE_LOCATION(IS_IN_DB):

    def __init__(self, *args1, **args2):
        super(IS_IN_DB_AND_USER_STORE_LOCATION, self).__init__(*args1, **args2)
        mylogger.debug(message='self.__dict__:%s' % str(self.__dict__))

    @property
    def dbset(self):
        return self.__dict__['dbset']

    @dbset.setter
    def dbset(self, v):
        # do NOT use self.varname !
        #http://docs.python.org/2/reference/datamodel.html#object.__setattr__
        self.__dict__['dbset'] = v

    def options(self, *args1, **args2):
        _auth_user_entities = tuple([_ENTITY.id for _ENTITY in ENTITY_MAPPER().find(person_id=current.auth.user.id)])
        if self.dbset.query is not None:
            self.dbset.query = self.dbset.query.__and__(current.db.store_location.entity.belongs(_auth_user_entities))
        else:
            self.dbset.query = current.db.store_location.entity.belongs(_auth_user_entities)
        return super(IS_IN_DB_AND_USER_STORE_LOCATION, self).options(*args1, **args2)


class IS_IN_DB_AND_USER_ENTITY(IS_IN_DB):

    def __init__(self, *args1, **args2):
        super(IS_IN_DB_AND_USER_ENTITY, self).__init__(*args1, **args2)
        mylogger.debug(message='self.__dict__:%s' % str(self.__dict__))

        self._db_set_query_save = copy.copy(self.dbset.query)

    @property
    def dbset(self):
        return self.__dict__['dbset']

    @dbset.setter
    def dbset(self, v):
        # do NOT use self.varname !
        #http://docs.python.org/2/reference/datamodel.html#object.__setattr__
        self.__dict__['dbset'] = v

    def __call__(self, *args1, **args2):
        _auth_user_entities = tuple([_ENTITY.id for _ENTITY in ENTITY_MAPPER().find(person_id=current.auth.user.id)])
        if self._db_set_query_save is not None:
            self.dbset.query = self._db_set_query_save.__and__(current.db.entity.id.belongs(_auth_user_entities))
        else:
            self.dbset.query = current.db.entity.id.belongs(_auth_user_entities)

        self.build_set()

        return super(IS_IN_DB_AND_USER_ENTITY, self).__call__(*args1, **args2)

    def options(self, *args1, **args2):
        # root_entity already filtered by the ENTITY_MAPPER().find function
        _auth_user_entities = tuple([_ENTITY.id for _ENTITY in ENTITY_MAPPER().find(person_id=current.auth.user.id, 
                                                                                    role='all_entity', 
                                                                                    negate_role_search=True)])
        if self.dbset.query is not None:
            self.dbset.query = self.dbset.query.__and__(current.db.entity.id.belongs(_auth_user_entities))
        else:
            self.dbset.query = current.db.entity.id.belongs(_auth_user_entities)

        return super(IS_IN_DB_AND_USER_ENTITY, self).options(*args1, **args2)


class IS_CHIMITHEQUE_PERMISSION(object):
    def __init__(self):
        mylogger.debug(message='__init__')
    def __call__(self, value):
        mylogger.debug(message='__call__')
        mylogger.debug(message='value:%s' %value)
        return (value, None)
    def options(self):
        _options = []
        for _permission in Permission.get_permission():
            if _permission[-2:] == 'NA':
                _options.append((_permission, '.'))
            else:
                _options.append((_permission, ''))
        return _options

    def formatter(self, value):
        return value


class ALL_OF(Validator): 

    def __init__(self, subs):
        mylogger.debug(message='__init__')
        self.subs = subs

    def __call__(self, value):
        for validator in self.subs:
            value, error = validator(value)
            if error != None:
                break
        return value, error

    def formatter(self, value):
        # Use the formatter of the first subvalidator
        # that validates the value and has a formatter
        for validator in self.subs:
            if hasattr(validator, 'formatter') and validator(value)[1] != None:
                return validator.formatter(value)


class IS_CONFIRM_EMPTY_OR(Validator):

    def __init__(self,
                 field_name,
                 other,
                 error_message=current.T('enter a value (or check the "confirm empty field" checkbox)')):
        mylogger.debug(message='__init__')
        self.other = other
        self.field_name = field_name
        self.error_message = error_message

    def __call__(self, value):

        _confirm_empty = current.request.vars['confirm_empty_%s' % self.field_name]
        mylogger.debug(message='self.field_name:%s' %self.field_name)
        mylogger.debug(message='value:%s' %value)
        mylogger.debug(message='_confirm_empty:%s' %_confirm_empty)

        if _confirm_empty is None and (value is None or value == ''):
            mylogger.debug(message='not validated')
            return value, self.error_message
        if _confirm_empty is None and (value is not None):
            if isinstance(self.other, (list, tuple)):
                error = None
                for item in self.other:
                    mylogger.debug(message='item:%s' %item)
                    value, error = item(value)
                    if error:
                        break
                return value, error
            else:
                return self.other(value)

        mylogger.debug(message='validated')
        return (value, None)
