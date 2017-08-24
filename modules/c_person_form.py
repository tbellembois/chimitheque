# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
from gluon import current
from gluon.dal import Field
from gluon.html import URL
from gluon.html import XML
from gluon.sqlhtml import SQLFORM
from gluon.validators import IS_EMAIL
from gluon.validators import IS_NOT_EMPTY
from gluon.validators import IS_NOT_IN_DB

from c_person_mapper import PERSON_MAPPER
from chimitheque_logger import chimitheque_logger
from chimitheque_permission import PermissionWidget
from chimitheque_validators import IS_CHIMITHEQUE_PERMISSION
from chimitheque_validators import IS_IN_DB_AND_USER_ENTITY
from chimitheque_validators import IS_ONE_SELECTED
import chimitheque_commons as cc


my_logger = chimitheque_logger()


class PERSON_FORM(object):

    def __new__(cls, **kwargs):

        instance = super(PERSON_FORM, cls).__new__(cls)

        instance.person = kwargs.get('person')  # PERSON type
        instance.readonly = kwargs.get('readonly') or False
        instance.readonly_fields = kwargs.get('readonly_fields') or []
        my_logger.debug(message='instance.person:%s' % instance.person)
        my_logger.debug(message='instance.person.creator:%s' % instance.person.creator)

        if instance.person is not None:
            current.db.person.first_name.default = instance.person.first_name
            if 'first_name' in instance.readonly_fields:
                current.db.person.first_name.writable = False
            current.db.person.last_name.default = instance.person.last_name
            if 'last_name' in instance.readonly_fields:
                current.db.person.last_name.writable = False
            current.db.person.email.default = instance.person.email
            if 'email' in instance.readonly_fields:
                current.db.person.email.writable = False
            current.db.person.contact.default = instance.person.contact
            if 'contact' in instance.readonly_fields:
                current.db.person.contact.writable = False

            current.db.person.email.requires = [IS_NOT_EMPTY(),
                                                IS_EMAIL(),
                                                IS_NOT_IN_DB(current.db(current.db.person.id != instance.person.id),
                                                           current.db.person.email)]

            # creator is a computed field and then not shown by web2py
            # we need to add it manually
            instance.form = SQLFORM.factory(Field('creator',
                                                  'string',
                                                  writable=not 'creator' in instance.readonly_fields,
                                                  label=cc.get_string("PERSON_CREATOR_LABEL"),
                                                  default=instance.person.creator.email \
                                                            if instance.person.creator is not None \
                                                            else ''),  # creator should exists - backward compatibility

                                            current.db.person,

                                    Field('is_all_entity',
                                          'boolean',
                                          label=cc.get_string("PERSON_IS_ALL_ENTITY_LABEL"),
                                          comment=cc.get_string("PERSON_IS_ALL_ENTITY_COMMENT"),
                                          represent=lambda r: current.T(str(instance.person.is_all_entity())),
                                          # disabled if the user is not admin
                                          readable=current.auth.has_membership('all_entity') or \
                                                    current.auth.has_membership('admin_entity') or \
                                                    current.auth.has_permission('admin'),  # admin_ENTITY: backward compatibility
                                          writable=(current.auth.has_membership('all_entity') or \
                                          current.auth.has_membership('admin_entity') or \
                                          current.auth.has_permission('admin')) and \
                                          not 'custom_entity' in instance.readonly_fields,
                                          # for an update request, pre populating the widget if the user is in all entities
                                          default=instance.person.is_all_entity(),
                                          ),

                                       Field('custom_entity',
                                            'list:reference entity',
                                            comment=cc.get_string("PERSON_ENTITY_COMMENT"),
                                            label=cc.get_string("PERSON_ENTITY_LABEL"),
                                            required=True,
                                            notnull=True,
                                            writable=not 'custom_entity' in instance.readonly_fields,
                                            # for an update request, pre populating the widget given the user entities
                                            default=[_entity.id for _entity in instance.person.entities] \
                                                      if instance.person.entities is not None \
                                                      else [],
                                            requires=[IS_IN_DB_AND_USER_ENTITY(current.db(current.db.entity.id > 0),
                                                                               current.db.entity.id,
                                                                               current.db.entity._format, multiple=True),
                                                       IS_ONE_SELECTED(db=current.db, table=current.db.entity, table_set=~current.db.entity.role.like('user_%'))],
                                            represent=lambda r: XML(' <br/>'.join(['%s' % (e.name) \
                                                                    for e in instance.person.entities])) \
                                            if (not instance.person.is_all_entity() and instance.person.entities is not None) else 'X',

                                            widget=lambda field, value: SQLFORM.widgets.multiple.widget(field, value, _class='required')),

                                        Field('is_admin',
                                              'boolean',
                                              label=cc.get_string("PERSON_IS_ADMIN_LABEL"),
                                              comment=cc.get_string("PERSON_IS_ADMIN_COMMENT"),
                                              represent=lambda r: current.T(str(instance.person.is_admin())),
                                              # disabled if the user is not admin
                                              readable=current.auth.has_permission('admin'),
                                              writable=current.auth.has_permission('admin') and not 'is_admin' in instance.readonly_fields,
                                              # for an update request, pre populating the widget if the user is admin
                                              default=instance.person.is_admin(),
                                              ),

                                        Field('custom_permission',
                                              'string',  # this does not matter given that we define our own permission widget
                                              label=cc.get_string("PERSON_ENTITY_PERMISSION_LABEL"),
                                              required=True,
                                              notnull=True,
                                              writable=not 'custom_permission' in instance.readonly_fields,
                                              # for an update request, pre populating the widget given the user permissions
                                              default=[_permission.name for _permission in instance.person.permissions],
                                              comment=cc.get_string("PERSON_ENTITY_PERMISSION_COMMENT"),
                                              requires=IS_CHIMITHEQUE_PERMISSION(),
                                              represent=lambda r: PermissionWidget.represent(r),
                                              widget=lambda field, value: PermissionWidget.widget(field,
                                                                                                value,
                                                                                                _class='required',
                                                                                                auth_user_permissions=[_permission.name for _permission in PERSON_MAPPER().find_permissions(current.auth.user.id)] \
                                                                                                                      if not current.auth.has_permission('admin') \
                                                                                                                      else None)),

                                       readonly=instance.readonly,
                                       comments=not instance.readonly,
                                       next=URL(current.request.application, 'user', 'list'),
                                       submit_button=cc.get_string("SUBMIT")
                                       )
        else:

            instance.form = SQLFORM.factory(Field('None', 'string', writable=False, readable=False))

        return instance

    def get_form(self):
        return self.form
