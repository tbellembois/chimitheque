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
# $Id: db.py 222 2015-07-21 16:06:35Z tbellemb2 $
#
from chimitheque_multiple_widget import CHIMITHEQUE_MULTIPLE_widget
from chimitheque_logger import chimitheque_logger
from chimitheque_validators import *
from datetime import datetime, timedelta
from gluon import current
from gluon.dal import Row
from gluon.settings import settings
from gluon.sqlhtml import CheckboxesWidget
from gluon.tools import Mail, Auth, Crud, Service, PluginManager
import chimitheque_commons as cc
import re

# TIPS:
# - export production database to SQLITE
# PYTHONPATH="/var/www/chimitheque" python ./scripts/cpdb.py -d /var/www/chimitheque/gluon/dal.py -f ./applications/chimitheque/databases -F /tmp -y 'postgres://user:pass@base:port/chimitheque' -Y 'sqlite://chimitheque.sqlite'
# - retrieve web2py documentation by:
# wget --recursive -l 1 --no-clobber --page-requisites --html-extension --convert-links --restrict-file-names=windows --domains web2py.com --no-parent http://www.web2py.com/book

mylogger = chimitheque_logger()
mylogger.debug(message='db_connection:%s' % settings['db_connection'])
mylogger.debug(message='db_fake_migrate:%s' % settings['db_fake_migrate'])

#
# database definition
#
db = DAL("%s" % settings['db_connection'],
         migrate=True,
         fake_migrate_all=settings['db_fake_migrate'],
         pool_size=10)

#
# store sessions in DB
#
session.connect(request, response, db=db, masterapp='chimitheque')

#
# setting the language
#
if not session.language:
    session.language = settings['language']
mylogger.debug(message='session.language:%s' % session.language)

T.force(session.language)
settings['translator'] = T

#
# authentication
#
mail = Mail()

# Don't use CAS
if request.get_vars['no_cas'] == '1':
  session['no_cas'] = True
elif 'no_cas' not in session:
  session['no_cas'] = False

if settings['cas_enable'] and not session['no_cas']:

    auth = Auth(db,cas_provider = settings['cas_provider'])
    auth.settings.cas_maps = {}
    auth.settings.cas_maps['registration_id'] = lambda v, p=auth.settings.cas_provider: '%s/%s' % (p, v['user'])
    auth.settings.cas_maps['first_name'] = lambda v: v['attributes']['givenName']
    auth.settings.cas_maps['last_name'] = lambda v: v['attributes']['sn']
    auth.settings.cas_maps['email'] = lambda v: v['attributes']['mail'].lower()
    auth.settings.cas_maps['password'] = lambda v: 'NOPASSWD'
    auth.settings.cas_maps['registration_key'] = lambda v: ''
    auth.settings.actions_disabled.append('change_password')
else:
    auth = Auth(globals(),
                db,
                hmac_key=settings['hmac_key'])

auth.settings.actions_disabled = ['retrieve_username', 'register']

crud = Crud(globals(), db)
service = Service(globals())
plugins = PluginManager()

http_proto = 'https' if request.is_https else 'http'

#
# mail
#
mail.settings.server = settings['mail_server']
mail.settings.sender = settings['mail_sender'] if settings['mail_sender'].lower() != 'none' else None
mail.settings.login = settings['mail_login'] if settings['mail_login'].lower() != 'none' else None
mail.settings.tls = settings['mail_tls']

#
# profile management configuration
#
auth.settings.mailer = mail # for user email verification
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.messages.verify_email = cc.get_string("CLICK_ON_LINK_TO_VERIFY_EMAIL") + ' ' + http_proto + '://' + request.env.http_host + URL(r=request, c='default', f='user', args=['verify_email']) + '?key=%(key)s'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = cc.get_string("CLICK_ON_LINK_TO_RESET_PASSWORD") + ' ' + http_proto + '://' + request.env.http_host + URL(r=request, c='default', f='user', args=['reset_password']) + '?key=%(key)s'
auth.settings.remember_me_form = False
auth.settings.login_form.messages.login_button = cc.get_string("LOGIN_FORM_SUBMIT")

#
# web2py tables definition
#
auth.settings.table_user_name = 'person'
auth.settings.table_group_name = 'entity'
auth.settings.table_membership_name = 'membership'
auth.settings.table_permission_name = 'permission'
auth.settings.login_userfield = 'email'
auth.settings.expiration = 60 * int(settings['session_time'])
auth.settings.long_expiration = 60 * int(settings['session_time'])

# we do not enforce authorization on crud
crud.settings.auth = None

#
# chimitheque tables definition
#
db.define_table('hazard_code',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_HAZARD_CODE_LABEL"),
                      comment=cc.get_string("DB_HAZARD_CODE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.hazard_code.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.hazard_code.label)]

db.define_table('symbol',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_SYMBOL_LABEL"),
                      comment=cc.get_string("DB_SYMBOL_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label.replace('SGH', ''))

db.symbol.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.symbol.label)]

db.define_table('signal_word',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_SIGNAL_WORD_LABEL"),
                      comment=cc.get_string("DB_SIGNAL_WORD_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: T(r.label))

db.signal_word.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.signal_word.label)]

db.define_table('physical_state',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_PHYSICAL_STATE_LABEL"),
                      comment=cc.get_string("DB_PHYSICAL_STATE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.physical_state.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.physical_state.label)]
db.physical_state.nb_linked_product = Field.Method(lambda row: db(db.product.physical_state == row.physical_state.id).count())

db.define_table('class_of_compounds',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_CLASS_OF_COMPOUNDS_LABEL"),
                      comment=cc.get_string("DB_CLASS_OF_COMPOUNDS_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.class_of_compounds.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.class_of_compounds.label), IS_LOWER()]
db.class_of_compounds.nb_linked_product = Field.Method(lambda row: db(db.product.class_of_compounds.contains(row.class_of_compounds.id)).count())

db.define_table('supplier',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_SUPPLIER_LABEL"),
                      comment=cc.get_string("DB_SUPPLIER_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.supplier.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.supplier.label), IS_UPPER()]
db.supplier.nb_linked_storage = Field.Method(lambda row: db(db.storage.supplier == row.supplier.id).count())

db.define_table('risk_phrase',
                Field('label',
                      'string',
                      label=cc.get_string("DB_RISK_PHRASE_LABEL"),
                      comment=cc.get_string("DB_RISK_PHRASE_COMMENT"),
                      required=True,
                      notnull=True),
                Field('reference',
                      'string',
                      length=255,
                      label=cc.get_string("DB_RISK_PHRASE_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_RISK_PHRASE_REFERENCE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: '(%s) %s' %(r.reference, T(r.label)))

db.risk_phrase.label.requires = IS_NOT_EMPTY()
db.risk_phrase.reference.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.risk_phrase.reference)]

db.define_table('safety_phrase',
                Field('label',
                      'string',
                      label=cc.get_string("DB_SAFETY_PHRASE_LABEL"),
                      comment=cc.get_string("DB_SAFETY_PHRASE_COMMENT"),
                      required=True,
                      notnull=True),
                Field('reference',
                      'string',
                      length=255,
                      label=cc.get_string("DB_SAFETY_PHRASE_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_SAFETY_PHRASE_REFERENCE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: '(%s) %s' %(r.reference, T(r.label)))

db.safety_phrase.label.requires = IS_NOT_EMPTY()
db.safety_phrase.reference.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.safety_phrase.reference)]

db.define_table('hazard_statement',
                Field('label',
                      'string',
                      label=cc.get_string("DB_HAZARD_STATEMENT_LABEL"),
                      comment=cc.get_string("DB_HAZARD_STATEMENT_COMMENT"),
                      required=True,
                      notnull=True),
                Field('reference',
                      'string',
                      length=255,
                      label=cc.get_string("DB_HAZARD_STATEMENT_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_HAZARD_STATEMENT_REFERENCE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: '(%s) %s' %(r.reference, T(r.label)))

db.hazard_statement.label.requires = IS_NOT_EMPTY()
db.hazard_statement.reference.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.hazard_statement.reference)]

db.define_table('precautionary_statement',
                Field('label',
                      'string',
                      label=cc.get_string("DB_PRECAUTIONARY_STATEMENT_LABEL"),
                      comment=cc.get_string("DB_PRECAUTIONARY_STATEMENT_COMMENT"),
                      required=True,
                      notnull=True),
                Field('reference',
                      'string',
                      length=255,
                      label=cc.get_string("DB_PRECAUTIONARY_STATEMENT_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_PRECAUTIONARY_STATEMENT_REFERENCE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: '(%s) %s' %(r.reference, T(r.label)))

db.precautionary_statement.label.requires = IS_NOT_EMPTY()
db.precautionary_statement.reference.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.precautionary_statement.reference)]

# TODO
# merge the EMPIRICAL and LINEAR FORMULA tables in CHEMICAL_FORMULA: label, type=empirical|linear
db.define_table('empirical_formula',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_EMPIRICAL_FORMULA_LABEL"),
                      comment=cc.get_string("DB_EMPIRICAL_FORMULA_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.empirical_formula.label.requires = [IS_NOT_EMPTY(), IS_VALID_EMPIRICAL_FORMULA(), IS_NOT_IN_DB(db, db.empirical_formula.label)]

db.define_table('linear_formula',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_LINEAR_FORMULA_LABEL"),
                      comment=cc.get_string("DB_LINEAR_FORMULA_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                format=lambda r: r.label)

db.linear_formula.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.linear_formula.label)]

db.define_table('name',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_NAME_LABEL"),
                      comment=cc.get_string("DB_NAME_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                Field('label_nost',
                      'string',
                      readable=False,
                      writable=False,
                      compute=lambda r: compute_name_label_nost(r) if r else ''),
                format=lambda r: r.label.replace('@', '-'))

db.name.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.name.label), IS_UPPER_NAME()]


def represent_product(r):
    if r and isinstance(r, Row):
        mylogger.debug(message='r.name:%s' %r.name)
        rows = db(db.name.id == r.name).select(db.name.label)
        names = ' '.join([row.label.replace('@', '-') for row in rows])
        return '(%s) %s' %(r.cas_number, names.strip())
    else:
        return None


def represent_product_symbol(r):
    if r:
        _symbols = db(db.symbol.id.belongs(r)).select()
        _ret = DIV()
        for _row in _symbols:
            _ret.append(IMG(_src="%s/picto_%s.png" % (cc.images_base_url, _row.label)))
        return _ret
    else:
        return None


def represent_product_hazard_code(r):
    if r:
        _symbols = db(db.hazard_code.id.belongs(r)).select()
        _ret = DIV()
        for _row in _symbols:
            _ret.append(IMG(_src="%s/picto_%s.png" % (cc.images_base_url, _row.label)))
        return _ret
    else:
        return None

def compute_product_cmr_cat(r):
    CMRs = settings['CMR'].keys()
    mylogger.debug(message='r:%s' %r)
    if r:
        rf = r.risk_phrase if r.risk_phrase else []
        hs = r.hazard_statement if r.hazard_statement else []
        mylogger.debug(message='rf:%s' %rf)
        mylogger.debug(message='hs:%s' %hs)
        rf_references = [j.reference for j in db(db.risk_phrase.id.belongs(rf)).select(db.risk_phrase.reference)]
        hs_references = [j.reference for j in db(db.hazard_statement.id.belongs(hs)).select(db.hazard_statement.reference)]
        mylogger.debug(message='rf_references:%s' %rf_references)
        mylogger.debug(message='hs_references:%s' %hs_references)
        phrases = rf_references + hs_references

        cat = ''
        for phrase in phrases:
            if phrase in CMRs:
                cat = cat + settings['CMR'][phrase] + ' '
        return cat
    else:
        return None


def compute_product_is_cmr(r):
    CMRs = settings['CMR'].keys()
    mylogger.debug(message='CMRs:%s' %CMRs)
    if r:
        rf = r.risk_phrase if r.risk_phrase else []
        hs = r.hazard_statement if r.hazard_statement else []
        mylogger.debug(message='rf:%s' %rf)
        mylogger.debug(message='hs:%s' %hs)
        rf_references = [j.reference for j in db(db.risk_phrase.id.belongs(rf)).select(db.risk_phrase.reference)]
        hs_references = [j.reference for j in db(db.hazard_statement.id.belongs(hs)).select(db.hazard_statement.reference)]
        mylogger.debug(message='rf_references:%s' %rf_references)
        mylogger.debug(message='hs_references:%s' %hs_references)
        phrases = rf_references + hs_references
        mylogger.debug(message='phrases:%s' %phrases)
        return len([j for j in phrases if j in CMRs]) != 0
    else:
        return False

def compute_name_label_nost(r):
    """
    Returns name without the stereochemistry part
    """
    m = re.match(".*@\(?(?P<label_nost>.*)$", r.label)
    if m:
        return m.group('label_nost')
    else:
        return r.label

db.define_table('entity',
                # web2py auth
                Field('role',
                      'string',
                      label=cc.get_string("DB_ENTITY_ROLE_LABEL"),
                      comment=cc.get_string("DB_ENTITY_ROLE_COMMENT"),
                      default='generated_by_register',
                      required=True,
                      notnull=True),
                Field('description',
                      'text',
                      label=cc.get_string("DB_ENTITY_DESCRIPTION_LABEL"),
                      comment=cc.get_string("DB_ENTITY_DESCRIPTION_COMMENT"),
                      default='',
                      writable=False,
                      readable=False),
                # web2py auth
                Field('manager',
                      'list:reference person',
                      label=cc.get_string("DB_ENTITY_MANAGER_LABEL"),
                      comment=cc.get_string("DB_ENTITY_MANAGER_COMMENT")),
                format=lambda r: r.role)

db.define_table('person',
                Field('creator',
                      'reference person',
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_PERSON_CREATOR_LABEL"),
                      comment=cc.get_string("DB_PERSON_CREATOR_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None),
                Field('first_name',
                      'string',
                      label=cc.get_string("DB_PERSON_FIRST_NAME_LABEL"),
                      comment=cc.get_string("DB_PERSON_FIRST_NAME_COMMENT"),
                      length=128,
                      required=True,
                      notnull=True),
                Field('last_name',
                      'string',
                      label=cc.get_string("DB_PERSON_LAST_NAME_LABEL"),
                      comment=cc.get_string("DB_PERSON_LAST_NAME_COMMENT"),
                      length=128,
                      required=True,
                      notnull=True),
                Field('email',
                      'string',
                      length=255,
                      label=cc.get_string("DB_PERSON_EMAIL_LABEL"),
                      comment=cc.get_string("DB_PERSON_EMAIL_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True),
                Field('contact',
                      'text',
                      label=cc.get_string("DB_PERSON_CONTACT_LABEL"),
                      comment=cc.get_string("DB_PERSON_CONTACT_COMMENT")),
                Field('password',
                      'password',
                      label=cc.get_string("DB_PERSON_PASSWORD_LABEL"),
                      comment=cc.get_string("DB_PERSON_PASSWORD_COMMENT"),
                      writable=False,
                      readable=False,
                      required=True,
                      notnull=True),
                Field('creation_date',
                      'date',
                      label=cc.get_string("DB_PERSON_CREATION_DATE_LABEL"),
                      comment=cc.get_string("DB_PERSON_CREATION_DATE_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('virtual',
                      'boolean',
                      writable=False,
                      readable=False,
                      default=False),
                Field('archive',
                      'boolean',
                      writable=False,
                      readable=False,
                      default=False),
                Field('exposure_card',
                      'list:reference exposure_card',
                      writable=False,
                      readable=False),
                # web2py auth
                # pending | unactive | active
                Field('registration_key',
                      'string',
                      length=512,
                      label=cc.get_string("DB_PERSON_REGISTRATION_KEY_LABEL"),
                      comment='',
                      default='',
                      writable=False,
                      readable=False),
                Field('reset_password_key',
                      'string',
                      length=512,
                      writable=False,
                      readable=False,
                      default=''),
                Field('registration_id',
                      'string',
                      length=512,
                      writable=False,
                      readable=False,
                      default=''),
                # web2py auth
                format=lambda r: r.email)

db.entity.manager.requires = [IS_EMPTY_OR(IS_LIST_OF(CLEANUP()))]
db.entity.manager.widget = CHIMITHEQUE_MULTIPLE_widget(db.person.email, configuration={'*': {'multiple': True, 'disable_validate': True}})

db.define_table('membership',
                Field('user_id', db.person),
                Field('group_id', db.entity))

db.person.first_name.requires = IS_NOT_EMPTY()
db.person.first_name.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.person.last_name.requires = IS_NOT_EMPTY()
db.person.last_name.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.person.email.requires = [IS_NOT_EMPTY(), IS_EMAIL(), IS_NOT_IN_DB(db, db.person.email)]
db.person.email.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.person.password.requires = [IS_NOT_EMPTY(), CRYPT(key=settings['hmac_key'])]
db.person.password.widget = lambda field, value: SQLFORM.widgets.password.widget(field, None, _class='required')
db.person.registration_key.requires = [IS_ONE_SELECTED(tuple_list=[('unactive', 'unactive'), ('active', 'active')])]
db.person.registration_key.widget = lambda field, value: SQLFORM.widgets.radio.widget(field, value, _class='required')

db.define_table('message',
                Field('text',
                      'text',
                      label=cc.get_string("DB_MESSAGE_TEXT_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_TEXT_COMMENT"),
                      default=''),
                Field('topic',
                      'string',
                      label=cc.get_string("DB_MESSAGE_TOPIC_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_TOPIC_COMMENT"),
                      default=cc.get_string("DB_MESSAGE_TOPIC_DEFAULT")),
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_MESSAGE_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_CREATION_DATETIME_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('expiration_datetime',
                      'datetime',
                      label=cc.get_string("DB_MESSAGE_EXPIRATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_EXPIRATION_DATETIME_COMMENT"),
                      default=datetime.now() + timedelta(days=+7),
                      writable=True,
                      readable=True),
                Field('person',
                      db.person,
                      label=cc.get_string("DB_MESSAGE_PERSON_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_PERSON_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email if r else None)),
                Field('parent',
                      'reference message',
                      label=cc.get_string("DB_MESSAGE_PIN_LABEL"),
                      comment=cc.get_string("DB_MESSAGE_PIN_COMMENT"),
                      readable=False,
                      writable=False),
                Field('pin',
                      'boolean'),
                format=lambda r: r.text)

db.define_table('shout',
                Field('text',
                      'text',
                      label=cc.get_string("DB_SHOUT_TEXT_LABEL"),
                      comment=cc.get_string("DB_SHOUT_TEXT_COMMENT"),
                      default=''),
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_SHOUT_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_SHOUT_CREATION_DATETIME_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('sender',
                      db.person,
                      label=cc.get_string("DB_SHOUT_SENDER_LABEL"),
                      comment=cc.get_string("DB_SHOUT_SENDER_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None),
                Field('receiver',
                      db.person,
                      label=cc.get_string("DB_SHOUT_RECEIVER_LABEL"),
                      comment=cc.get_string("DB_SHOUT_RECEIVER_COMMENT"),
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None),
                format=lambda r: r.text)

db.define_table('store_location',
                Field('label',
                      'string',
                      label=cc.get_string("DB_STORE_LOCATION_LABEL"),
                      comment=cc.get_string("DB_STORE_LOCATION_COMMENT"),
                      default='My store location', # to fix a migration problem
                      required=True,
                      notnull=True,
                      unique=False),
                Field('entity',
                      db.entity,
                      label=cc.get_string("DB_STORE_LOCATION_ENTITY_LABEL"),
                      comment=cc.get_string("DB_STORE_LOCATION_ENTITY_COMMENT")),
                Field('parent',
                      'reference store_location',
                      label=cc.get_string("DB_STORE_LOCATION_PARENT_LABEL"),
                      comment=cc.get_string("DB_STORE_LOCATION_PARENT_COMMENT")),
                Field('can_store',
                      'boolean',
                      label=cc.get_string("DB_STORE_LOCATION_CAN_STORE_LABEL"),
                      comment=cc.get_string("DB_STORE_LOCATION_CAN_STORE_COMMENT"),
                      default=True),
                Field('color',
                      'string',
                      label=cc.get_string("DB_STORE_LOCATION_COLOR_LABEL"),
                      comment=cc.get_string("DB_STORE_LOCATION_COLOR_COMMENT"),
                      default='#FFFFFF'),
                Field('label_full_path',
                      compute=lambda r: cc.get_store_location_label_full_path(r)),
                format=lambda r: r.label_full_path)

subset = db((db.store_location.label == request.vars.label) &
            (db.store_location.parent == request.vars.parent))
db.store_location.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(subset, db.store_location.label)]
db.store_location.label.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.store_location.entity.requires = IS_IN_DB_AND_USER_ENTITY(db(db.entity.id > 0), db.entity.id, db.entity._format)
db.store_location.entity.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required', _onchange="ajax('/chimitheque/store_location/ajax_get_entity_store_location_options', ['entity'], 'store_location_parent');$.blockUI();")
db.store_location.parent.requires = IS_EMPTY_OR(IS_IN_DB_AND_SELECTED_ENTITY(db, db.store_location.id, db.store_location._format, orderby=db.store_location.label_full_path))
db.store_location.parent.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value)

db.define_table('unit',
                Field('label', 'string', length=255, label=cc.get_string("DB_UNIT_LABEL"), comment=cc.get_string("DB_UNIT_COMMENT"), required=True, notnull=True, unique=True),
                Field('reference', 'reference unit', label=cc.get_string("DB_UNIT_REFERENCE_LABEL"), comment=cc.get_string("DB_UNIT_REFERENCE_COMMENT")),
                Field('multiplier_for_reference', 'double', label=cc.get_string("DB_UNIT_MULTIPLIER_FOR_REFERENCE_LABEL"), comment=cc.get_string("DB_UNIT_MULTIPLIER_FOR_REFERENCE_COMMENT")),
                format=lambda r: r.label)

db.unit.label.requires = IS_NOT_EMPTY()

db.define_table('product',
                Field('cas_number',
                      'string',
                      label=cc.get_string("DB_PRODUCT_CAS_NUMBER_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_CAS_NUMBER_COMMENT"),
                      required=True),
                Field('ce_number',
                      'string',
                      label=cc.get_string("DB_PRODUCT_CE_NUMBER_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_CE_NUMBER_COMMENT")),
                Field('person',
                      db.person,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_PRODUCT_PERSON_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_PERSON_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None),
                Field('name',
                      db.name,
                      label=cc.get_string("DB_PRODUCT_NAME_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_NAME_COMMENT"),
                      notnull=True,
                      required=True,
                      represent=lambda r: str(db(db.name.id == r).select(db.name.label).first().label).replace('@', '-') if r else None),
                Field('synonym',
                      'list:reference name',
                      label=cc.get_string("DB_PRODUCT_SYNONYM_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_SYNONYM_COMMENT")),
                Field('restricted_access',
                      'boolean',
                      label=cc.get_string("DB_PRODUCT_RESTRICTED_ACCESS_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_RESTRICTED_ACCESS_COMMENT"),
                      default=False),
                Field('specificity',
                      'string',
                      label=cc.get_string("DB_PRODUCT_SPECIFICITY_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_SPECIFICITY_COMMENT")),
                Field('tdformula',
                      'string',
                      label=cc.get_string("DB_PRODUCT_TD_FORMULA_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_TD_FORMULA_COMMENT")),
                Field('empirical_formula',
                      db.empirical_formula,
                      label=cc.get_string("DB_PRODUCT_EMPIRICAL_FORMULA_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_EMPIRICAL_FORMULA_COMMENT"),
                      required=True,
                      represent=lambda r: str(db(db.empirical_formula.id == r).select(db.empirical_formula.label).first().label) if r else None),
                Field('linear_formula',
                      db.linear_formula,
                      label=cc.get_string("DB_PRODUCT_LINEAR_FORMULA_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_LINEAR_FORMULA_COMMENT"),
                      represent=lambda r: str(db(db.linear_formula.id == r).select(db.linear_formula.label).first().label) if r else None),
                Field('msds',
                      'string',
                      label=cc.get_string("DB_PRODUCT_MSDS_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_MSDS_COMMENT")),
                Field('physical_state',
                      db.physical_state,
                      label=cc.get_string("DB_PRODUCT_PHYSICAL_STATE_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_PHYSICAL_STATE_COMMENT"),
                      represent=lambda r: str(db(db.physical_state.id == r).select(db.physical_state.label).first().label) if r else None),
                Field('class_of_compounds',
                      'list:reference class_of_compounds',
                      label=cc.get_string("DB_PRODUCT_CLASS_OF_COMPOUNDS_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_CLASS_OF_COMPOUNDS_COMMENT")),
                Field('hazard_code',
                      'list:reference hazard_code',
                      label=cc.get_string("DB_PRODUCT_HAZARD_CODE_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_HAZARD_CODE_COMMENT"),
                      represent=lambda r: represent_product_hazard_code(r)),
                Field('symbol',
                      'list:reference symbol',
                      label=cc.get_string("DB_PRODUCT_SYMBOL_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_SYMBOL_COMMENT"),
                      represent=lambda r: represent_product_symbol(r)),
                Field('signal_word',
                      db.signal_word,
                      label=cc.get_string("DB_PRODUCT_SIGNAL_WORD_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_SIGNAL_WORD_COMMENT"),
                      represent=lambda r: T(str(db(db.signal_word.id == r).select(db.signal_word.label).first().label)) if r else None),
                Field('risk_phrase',
                      'list:reference risk_phrase',
                      label=cc.get_string("DB_PRODUCT_RISK_PHRASE_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_RISK_PHRASE_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s-%s' %(row.reference, T(row.label)) \
                                              for row in db(db.risk_phrase.id.belongs(r)).select()])) \
                                              if r else None),
                Field('safety_phrase',
                      'list:reference safety_phrase',
                      label=cc.get_string("DB_PRODUCT_SAFETY_PHRASE_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_SAFETY_PHRASE_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s-%s' %(row.reference, T(row.label)) \
                                              for row in db(db.safety_phrase.id.belongs(r)).select()])) \
                                              if r else None),
                Field('hazard_statement',
                      'list:reference hazard_statement',
                      label=cc.get_string("DB_PRODUCT_HAZARD_STATEMENT_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_HAZARD_STATEMENT_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s-%s' %(row.reference, T(row.label)) \
                                              for row in db(db.hazard_statement.id.belongs(r)).select()])) \
                                              if r else None),
                Field('precautionary_statement',
                      'list:reference precautionary_statement',
                      label=cc.get_string("DB_PRODUCT_PRECAUTIONARY_STATEMENT_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_PRECAUTIONARY_STATEMENT_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s-%s' %(row.reference, T(row.label)) \
                                              for row in db(db.precautionary_statement.id.belongs(r)).select()])) \
                                              if r else None),
                Field('disposal_comment',
                      'text',
                      label=cc.get_string("DB_PRODUCT_DISPOSAL_COMMENT_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_DISPOSAL_COMMENT_COMMENT")),
                Field('remark',
                      'text',
                      label=cc.get_string("DB_PRODUCT_REMARK_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_REMARK_COMMENT")),
                Field('is_cmr',
                      'boolean',
                      label=cc.get_string("DB_PRODUCT_IS_CMR_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_IS_CMR_COMMENT"),
                      compute=lambda r: compute_product_is_cmr(r),
                      default=False),
                Field('is_radio',
                      'boolean',
                      label=cc.get_string("DB_PRODUCT_IS_RADIO_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_IS_RADIO_COMMENT"),
                      default=False),
                Field('cmr_cat',
                      'string',
                      label=cc.get_string("DB_PRODUCT_CMR_CATEGORY_LABEL"),
                      compute=lambda r: compute_product_cmr_cat(r),
                      writable=False,
                      default=None,
                      represent=lambda r: r.replace('|', ' ') if r else None),
                Field('archive',
                      'boolean',
                      writable=False,
                      default=False),
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_PRODUCT_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_PRODUCT_CREATION_DATETIME_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                format=lambda r: represent_product(r))

db.product.hazard_code.widget = lambda field, value: CheckboxesWidget.widget(field, value, cols=10)
db.product.hazard_code.requires = IS_EMPTY_OR(IS_IN_DB(db, db.hazard_code.id, db.symbol._format, multiple=True))
db.product.symbol.widget = lambda field, value: CheckboxesWidget.widget(field, value, cols=10)
db.product.symbol.requires = IS_EMPTY_OR(IS_IN_DB(db, db.symbol.id, db.symbol._format, multiple=True))
db.product.cas_number.widget = CHIMITHEQUE_MULTIPLE_widget(db.product.cas_number,
                                                           _class='required',
                                                           minchar=4,
                                                           text_confirm_empty_form_field=cc.get_string('NCE'),
                                                           configuration={'create': {'add_in_db': True,
                                                                                     'confirm_empty': True},
                                                                          'update': {'add_in_db': True,
                                                                                     'confirm_empty': True}})
db.product.cas_number.requires = IS_CONFIRM_EMPTY_OR('cas_number',
                                                     [IS_VALID_CAS(),
                                                      IS_UNIQUE_WITH_SPECIFICITY(request.vars.specificity, request.function)])
db.product.ce_number.requires = IS_EMPTY_OR(CLEANUP())
db.product.physical_state.widget = SQLFORM.widgets.radio.widget
db.product.physical_state.requires = IS_EMPTY_OR(IS_IN_DB(db, db.physical_state.id, '%(label)s'))
db.product.class_of_compounds.widget = CHIMITHEQUE_MULTIPLE_widget(db.class_of_compounds.label,
                                                                   minchar=1,
                                                                   configuration={'create': {'add_in_db': True,
                                                                                             'multiple': True,},
                                                                                  'update': {'add_in_db': True,
                                                                                             'multiple': True,}})

db.product.class_of_compounds.requires = [IS_EMPTY_OR(IS_IN_DB(db, db.class_of_compounds.id,
                                                               label=db.class_of_compounds._format,
                                                               multiple=True,
                                                               sort=db.class_of_compounds.label))]
db.product.signal_word.widget = SQLFORM.widgets.radio.widget
db.product.signal_word.requires = IS_EMPTY_OR(IS_IN_DB(db, db.signal_word.id, '%(label)s'))
db.product.name.widget = CHIMITHEQUE_MULTIPLE_widget(db.name.label,
                                                     ref_field_info='cas_number',
                                                     _class='required',
                                                     configuration={'create': {'add_in_db': True,
                                                                               'max_nb_item': 25,
                                                                               'func_lambda': 'lambdaname'},
                                                                    'update': {'add_in_db': True,
                                                                               'search': '',
                                                                               'func_lambda': 'lambdaname'}})
db.product.name.requires = IS_NOT_EMPTY()
db.product.synonym.widget = CHIMITHEQUE_MULTIPLE_widget(db.name.label,
                                                        configuration={'create': {'add_in_db': True,
                                                                                  'multiple': True,
                                                                                  'func_lambda': 'lambdaname'},
                                                                       'update': {'add_in_db': True,
                                                                                  'multiple': True,
                                                                                  'func_lambda': 'lambdaname'},
                                                                       'search': {}})
db.product.synonym.requires = IS_EMPTY_OR(IS_LIST_OF(CLEANUP()))
db.product.risk_phrase.widget = CHIMITHEQUE_MULTIPLE_widget(db.risk_phrase.reference,
                                                            minchar=1,
                                                            configuration={'*': {'add_in_db': False, 'multiple': True}})
db.product.risk_phrase.requires = IS_EMPTY_OR(IS_IN_DB(db, db.risk_phrase.id, '(%(reference)s) %(label)s', multiple=True))
db.product.safety_phrase.widget = CHIMITHEQUE_MULTIPLE_widget(db.safety_phrase.reference,
                                                              minchar=1,
                                                              configuration={'*': {'add_in_db': False, 'multiple': True}})
db.product.safety_phrase.requires = IS_EMPTY_OR(IS_IN_DB(db, db.safety_phrase.id, '(%(reference)s) %(label)s', multiple=True))
db.product.hazard_statement.widget = CHIMITHEQUE_MULTIPLE_widget(db.hazard_statement.reference,
                                                                 minchar=1,
                                                                 configuration={'*': {'add_in_db': False, 'multiple': True}})
db.product.hazard_statement.requires = IS_EMPTY_OR(IS_IN_DB(db, db.hazard_statement.id, '(%(reference)s) %(label)s', multiple=True))
db.product.precautionary_statement.widget = CHIMITHEQUE_MULTIPLE_widget(db.precautionary_statement.reference,
                                                                        minchar=1,
                                                                        configuration={'*': {'add_in_db': False, 'multiple': True}})
db.product.precautionary_statement.requires = IS_EMPTY_OR(IS_IN_DB(db, db.precautionary_statement.id, '(%(reference)s) %(label)s', multiple=True))
db.product.msds.widget = CHIMITHEQUE_MULTIPLE_widget(db.product.msds,
                                                     _class='required',
                                                     minchar=4,
                                                     text_confirm_empty_form_field=cc.get_string('NO_MSDS'),
                                                     configuration={'create': {'add_in_db': True,
                                                                               'confirm_empty': True},
                                                                    'update': {'add_in_db': True,
                                                                               'confirm_empty': True}})
db.product.msds.requires = IS_CONFIRM_EMPTY_OR('msds', IS_NOT_EMPTY())
db.product.empirical_formula.widget = CHIMITHEQUE_MULTIPLE_widget(db.empirical_formula.label,
                                                                  _class='required',
                                                                  minchar=1,
                                                                  text_confirm_empty_form_field=cc.get_string('NO_EMPIRICAL_FORMULA'),
                                                                  configuration={'search': {'func_lambda': 'lambdaempiricalformula'},
                                                                                 'create': {'add_in_db': True, 'confirm_empty': True},
                                                                                 'update': {'add_in_db': True, 'confirm_empty': True}})
db.product.empirical_formula.requires = IS_CONFIRM_EMPTY_OR('empirical_formula', IS_IN_DB(db, db.empirical_formula.id, '%(label)s'))
db.product.linear_formula.widget = CHIMITHEQUE_MULTIPLE_widget(db.linear_formula.label, configuration={'*': {'add_in_db': True}})
db.product.linear_formula.requires = IS_EMPTY_OR(CLEANUP())
db.product.disposal_comment.widget = lambda field, value: SQLFORM.widgets.text.widget(field, value, _rows=5)
db.product.remark.widget = lambda field, value: SQLFORM.widgets.text.widget(field, value, _rows=5)

db.define_table('product_history',
                Field('current_record', db.product),
                Field('modification_datetime', 'datetime', writable=False, default=datetime.now()),
                db.product)

db.define_table('bookmark',
                Field('person',
                      db.person,
                      compute=lambda r: db.person[auth.user.id] if auth.user else None),
                Field('product',
                      db.product))

db.define_table('storage',
                Field('product',
                      db.product,
                      label=cc.get_string("DB_STORAGE_PRODUCT_LABEL"),
                      comment=cc.get_string("DB_STORAGE_PRODUCT_COMMENT"),
                      required=True,
                      notnull=True,
                      represent=lambda r: represent_product(r)),
                Field('person',
                      db.person,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_STORAGE_PERSON_LABEL"),
                      comment=cc.get_string("DB_STORAGE_PERSON_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id==r).select(db.person.email).first().email) if r else None),
                Field('store_location',
                      db.store_location,
                      label=cc.get_string("DB_STORAGE_STORE_LOCATION_LABEL"),
                      comment=cc.get_string("DB_STORAGE_STORE_LOCATION_COMMENT"),
                      required=True,
                      notnull=True,
                      ),
                Field('volume_weight',
                      'double',
                      label=cc.get_string("DB_STORAGE_VOLUME_WEIGHT_LABEL"),
                      comment=cc.get_string("DB_STORAGE_VOLUME_WEIGHT_COMMENT")),
                Field('unit',
                      db.unit,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_STORAGE_UNIT_LABEL"),
                      comment=cc.get_string("DB_STORAGE_UNIT_COMMENT"),
                      represent=lambda r: str(db(db.unit.id == r).select(db.unit.label).first().label) if r else None),
                Field('nb_items',
                      'integer',
                      label=cc.get_string("DB_STORAGE_NB_ITEMS_LABEL"),
                      comment=cc.get_string("DB_STORAGE_NB_ITEMS_COMMENT"),
                      default=1),
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_STORAGE_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_STORAGE_CREATION_DATETIME_COMMENT"),
                      default=datetime.now()),
                Field('entry_datetime',
                      'datetime',
                      label=cc.get_string("DB_STORAGE_ENTRY_DATETIME_LABEL"),
                      comment=cc.get_string("DB_STORAGE_ENTRY_DATETIME_COMMENT"),
                      default=datetime.now()),
                Field('exit_datetime',
                      'datetime',
                      label=cc.get_string("DB_STORAGE_EXIT_DATETIME_LABEL"),
                      comment=cc.get_string("DB_STORAGE_EXIT_DATETIME_COMMENT"),
                      writable=False,
                      readable=True),
                Field('expiration_datetime',
                      'datetime',
                      label=cc.get_string("DB_STORAGE_EXPIRATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_STORAGE_EXPIRATION_DATETIME_COMMENT")),
                Field('opening_datetime',
                      'datetime',
                      label=cc.get_string("DB_STORAGE_OPENING_DATETIME_LABEL"),
                      comment=cc.get_string("DB_STORAGE_OPENING_DATETIME_COMMENT")),
                Field('comment',
                      'text',
                      label=cc.get_string("DB_STORAGE_COMMENT_LABEL"),
                      comment=cc.get_string("DB_STORAGE_COMMENT_COMMENT")),
                # autogenerated barecode
                Field('barecode',
                      'string',
                      label=cc.get_string("DB_STORAGE_BARECODE_LABEL"),
                      comment=cc.get_string("DB_STORAGE_BARECODE_COMMENT")),
                Field('reference',
                      'string',
                      label=cc.get_string("DB_STORAGE_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_STORAGE_REFERENCE_COMMENT")),
                Field('batch_number',
                      'string',
                      label=cc.get_string("DB_STORAGE_BATCH_NUMBER_LABEL"),
                      comment=cc.get_string("DB_STORAGE_BATCH_NUMBER_COMMENT")),
                Field('supplier',
                      db.supplier,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_STORAGE_SUPPLIER_LABEL"),
                      comment=cc.get_string("DB_STORAGE_SUPPLIER_COMMENT"),
                      represent=lambda r: str(db(db.supplier.id == r).select(db.supplier.label).first().label) if r else None),
                Field('archive',
                      'boolean',
                      label=cc.get_string("DB_STORAGE_ARCHIVE_LABEL"),
                      comment=cc.get_string("DB_STORAGE_ARCHIVE_COMMENT"),
                      writable=False,
                      default=False),
                Field('to_destroy',
                      'boolean',
                      label=cc.get_string("DB_STORAGE_TO_DESTROY_LABEL"),
                      comment=cc.get_string("DB_STORAGE_TO_DESTROY_COMMENT"),
                      writable=False,
                      default=False),
                # computed field to make coding easier
                Field('computed_entity',
                      'integer',
                      compute=lambda r: db(db.store_location.id == (r['STORE_LOCATION'])).select(db.store_location.entity).first().entity if r else None,
                      writable=False,
                      readable=False))


db.storage.product.requires = IS_NOT_EMPTY()
db.storage.product.widget = CHIMITHEQUE_MULTIPLE_widget(db.product.name, _class='required')
db.storage.store_location.requires = IS_IN_DB_AND_USER_STORE_LOCATION(db(db.store_location.can_store==True), db.store_location.id, db.store_location._format, orderby=db.store_location.label_full_path)
db.storage.store_location.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')
db.storage.volume_weight.requires = IS_EMPTY_OR(IS_FLOAT_IN_RANGE(cc.MIN_FLOAT, cc.MAX_FLOAT))
db.storage.volume_weight.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value)
# prevent users from giving a volume_weight without a unit
db.storage.unit.requires = IS_IN_DB(db, db.unit.id, db.unit._format) if request.vars.volume_weight != '' else IS_EMPTY_OR(IS_IN_DB(db, db.unit.id, db.unit._format))
db.storage.unit.widget = lambda field, value: SQLFORM.widgets.radio.widget(field, value, cols=10)
db.storage.nb_items.requires = IS_EMPTY_OR(IS_INT_IN_RANGE(1, 31))
db.storage.nb_items.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value)
db.storage.supplier.requires = IS_EMPTY_OR(IS_IN_DB(db, db.supplier.id, '%(label)s'))

db.define_table('storage_history',
                Field('current_record', db.storage),
                Field('modification_datetime', 'datetime', writable=False, default=datetime.now()),
                db.storage)

db.define_table('stock',
                Field('maximum',
                      'double',
                      label=cc.get_string("DB_STOCK_MAXIMUM_LABEL"),
                      comment=cc.get_string("DB_STOCK_MAXIMUM_COMMENT")),
                Field('maximum_unit',
                      db.unit,
                      label=cc.get_string("DB_STOCK_MAXIMUM_UNIT_LABEL"),
                      comment=cc.get_string("DB_STOCK_MAXIMUM_UNIT_COMMENT"),
                      represent=lambda r: str(db(db.unit.id == r).select(db.unit.label).first().label) if r else None),
                Field('minimum',
                      'double',
                      label=cc.get_string("DB_STOCK_MINIMUM_LABEL"),
                      comment=cc.get_string("DB_STOCK_MINIMUM_COMMENT")),
                Field('minimum_unit',
                      db.unit,
                      label=cc.get_string("DB_STOCK_MINIMUM_UNIT_LABEL"),
                      comment=cc.get_string("DB_STOCK_MINIMUM_UNIT_COMMENT"),
                      represent=lambda r: str(db(db.unit.id == r).select(db.unit.label).first().label) if r else None),
                Field('product',
                      db.product,
                      label=cc.get_string("DB_STOCK_PRODUCT_LABEL"),
                      comment=cc.get_string("DB_STOCK_PRODUCT_COMMENT"),
                      writable=False),
                Field('entity',
                      db.entity,
                      label=cc.get_string("DB_STOCK_ENTITY_LABEL"),
                      comment=cc.get_string("DB_STOCK_ENTITY_COMMENT"),
                      writable=False))

db.stock.minimum.requires = [IS_NOT_EMPTY(), IS_FLOAT_IN_RANGE(cc.MIN_FLOAT, cc.MAX_FLOAT)]
db.stock.minimum.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.stock.maximum.requires = [IS_NOT_EMPTY(), IS_FLOAT_IN_RANGE(cc.MIN_FLOAT, cc.MAX_FLOAT)]
db.stock.maximum.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')

db.define_table('cpe',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_CPE_LABEL"),
                      comment=cc.get_string("DB_CPE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True,
                      represent=lambda r: r.label),
                format=lambda r: r.label)

db.define_table('ppe',
                Field('label',
                      'string',
                      length=255,
                      label=cc.get_string("DB_PPE_LABEL"),
                      comment=cc.get_string("DB_PPE_COMMENT"),
                      required=True,
                      notnull=True,
                      unique=True,
                      represent=lambda r: r.label),
                format=lambda r: r.label)

db.define_table('exposure_item',
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_EXPOSURE_ITEM_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_CREATION_DATETIME_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('product',
                      db.product,
                      label=cc.get_string("DB_EXPOSURE_ITEM_PRODUCT_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_PRODUCT_COMMENT"),
                      required=True,
                      notnull=True,
                      represent=lambda r: represent_product(r)),
                Field('kind_of_work',
                      'text',
                      label=cc.get_string("DB_EXPOSURE_ITEM_KIND_OF_WORK_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_KIND_OF_WORK_COMMENT")),
                Field('cpe',
                      'list:reference cpe',
                      label=cc.get_string("DB_EXPOSURE_ITEM_CPE_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_CPE_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s' %(T(row.label)) \
                                              for row in db(db.cpe.id.belongs(r)).select()])) \
                                              if r else None),
                Field('ppe',
                      'list:reference ppe',
                      label=cc.get_string("DB_EXPOSURE_ITEM_PPE_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_PPE_COMMENT"),
                      represent=lambda r: XML(' <br/>'.join(['%s' %(T(row.label)) \
                                              for row in db(db.ppe.id.belongs(r)).select()])) \
                                              if r else None),
                Field('nb_exposure',
                      'integer',
                      label=cc.get_string("DB_EXPOSURE_ITEM_NB_EXPOSURE_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_NB_EXPOSURE_COMMENT"),
                      default=1),
                Field('exposure_time',
                      'time',
                      label=cc.get_string("DB_EXPOSURE_ITEM_EXPOSURE_TIME_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_EXPOSURE_TIME_COMMENT")),
                Field('simultaneous_risk',
                      'text',
                      label=cc.get_string("DB_EXPOSURE_ITEM_SIMULTANEAOUS_RISK_LABEL"),
                      comment=cc.get_string("DB_EXPOSURE_ITEM_SIMULTANEAOUS_RISK_COMMENT")))

db.define_table('exposure_card',
                Field('title',
                      'string',
                      default='card: %s' % datetime.now()),
                Field('accidental_exposure_type',
                      'text',
                       label=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_TYPE_LABEL"),
                       comment=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_TYPE_COMMENT")),
                Field('accidental_exposure_datetime',
                      'datetime',
                       label=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_DATETIME_LABEL"),
                       comment=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_DATETIME_COMMENT")),
                Field('accidental_exposure_duration_and_extent',
                      'text',
                       label=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_DURATION_AND_EXTENT_LABEL"),
                       comment=cc.get_string("DB_EXPOSURE_CARD_ACCIDENTAL_EXPOSURE_DURATION_AND_EXTENT_COMMENT")),
                Field('creation_datetime',
                      'datetime',
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('modification_datetime',
                      'datetime',
                      default=datetime.now(),
                      compute=lambda r: datetime.now(),
                      writable=False,
                      readable=True),
                Field('archive',
                      'boolean',
                      writable=False,
                      default=False),
                Field('exposure_item',
                      'list:reference exposure_item'))

db.exposure_item.product.requires = []
db.exposure_item.kind_of_work.widget = lambda field, value, **kwargs: SQLFORM.widgets.string.widget(field, value, **kwargs)
db.exposure_item.cpe.requires = IS_EMPTY_OR(IS_IN_DB(db, db.cpe.id, '%(label)s', multiple=True))
db.exposure_item.cpe.widget = lambda field, value, **kwargs: SQLFORM.widgets.options.widget(field, value, _multiple="multiple", **kwargs)
db.exposure_item.ppe.requires = IS_EMPTY_OR(IS_IN_DB(db, db.ppe.id, '%(label)s', multiple=True))
db.exposure_item.ppe.widget = lambda field, value, **kwargs: SQLFORM.widgets.options.widget(field, value, _multiple="multiple", **kwargs)
db.exposure_item.nb_exposure.requires = IS_INT_IN_RANGE(1, 3650)
db.exposure_item.nb_exposure.widget = lambda field, value, **kwargs: SQLFORM.widgets.string.widget(field, value, **kwargs)
db.exposure_item.exposure_time.requires = IS_TIME()
db.exposure_item.exposure_time.widget = lambda field, value, **kwargs: SQLFORM.widgets.time.widget(field, value, **kwargs)
db.exposure_item.simultaneous_risk.widget = lambda field, value, **kwargs: SQLFORM.widgets.text.widget(field, value, **kwargs)


db.exposure_card.title.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value)
db.exposure_card.accidental_exposure_type.widget = lambda field, value, **kwargs: SQLFORM.widgets.string.widget(field, value, **kwargs)
db.exposure_card.accidental_exposure_datetime.widget = lambda field, value, **kwargs: SQLFORM.widgets.datetime.widget(field, value, **kwargs)
db.exposure_card.accidental_exposure_duration_and_extent.widget = lambda field, value, **kwargs: SQLFORM.widgets.string.widget(field, value, **kwargs)

db.define_table('borrow',
                Field('creation_datetime',
                      'datetime',
                      label=cc.get_string("DB_USE_CREATION_DATETIME_LABEL"),
                      comment=cc.get_string("DB_USE_CREATION_DATETIME_COMMENT"),
                      default=datetime.now(),
                      writable=False,
                      readable=True),
                Field('person',
                      db.person,
                      label=cc.get_string("DB_USE_PERSON_LABEL"),
                      comment=cc.get_string("DB_USE_PERSON_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None),
                Field('borrower',
                      db.person,
                      label=cc.get_string("DB_USE_BORROWER_LABEL"),
                      comment=cc.get_string("DB_USE_BORROWER_COMMENT"),
                      represent=lambda r: str(db(db.person.id == r).select(db.person.email).first().email) if r else None,
                      required=True,
                      notnull=True),
                Field('storage',
                      db.storage,
                      label=cc.get_string("DB_USE_STORAGE_LABEL"),
                      comment=cc.get_string("DB_USE_STORAGE_COMMENT"),
                      writable=False,
                      readable=False),
                Field('comment',
                      'text',
                      label=cc.get_string("DB_USE_COMMENT_LABEL"),
                      comment=cc.get_string("DB_USE_COMMENT_COMMENT")))

db.borrow.borrower.requires = [IS_IN_DB(db, db.person.id, label=db.person._format, sort=db.person.email)]
db.borrow.borrower.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')

db.define_table('command_status',
                Field('label',
                      'string',
                      label=cc.get_string("DB_COMMAND_STATUS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_STATUS_COMMENT"),
                      required=True,
                      notnull=True),
                Field('state',
                      'integer',
                      writable=False,
                      readable=False,
                      default=False),
                Field('rank',
                      'integer',
                      writable=False,
                      readable=False,
                      default=False),
                format=lambda r: T(r.label))

db.command_status.label.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.command_status.label)]

db.define_table('command',
                Field('product',
                      db.product,
                      required=True,
                      notnull=True,
                      represent=lambda r: represent_product(r)),
                Field('submitter',
                      db.person,
                      ondelete='NO ACTION',
                      required=True,
                      notnull=True,
                      represent=lambda r: str(db(db.person.id==r).select(db.person.email).first().email) if r else None),
                Field('status',
                      db.command_status,
                      label=cc.get_string("DB_COMMAND_STATUS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_STATUS_COMMENT"),
                      required=True,
                      notnull=True,
                      represent=lambda r: T(r.label)),
                Field('volume_weight',
                      'double',
                      label=cc.get_string("DB_COMMAND_VOLUME_WEIGHT_LABEL"),
                      comment=cc.get_string("DB_COMMAND_VOLUME_WEIGHT_COMMENT"),
                      required=True,
                      notnull=True,
                     ),
                Field('unit',
                      db.unit,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_COMMAND_UNIT_LABEL"),
                      comment=cc.get_string("DB_COMMAND_UNIT_COMMENT"),
                      represent=lambda r: str(db(db.unit.id == r).select(db.unit.label).first().label) if r else None,
                      required=True,
                      notnull=True,
                     ),
                Field('nb_items',
                      'integer',
                      label=cc.get_string("DB_COMMAND_NB_ITEMS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_NB_ITEMS_COMMENT"),
                      required=True,
                      notnull=True,
                      default=1),
                Field('store_location',
                      db.store_location,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_COMMAND_STORE_LOCATION_LABEL"),
                      comment=cc.get_string("DB_COMMAND_STORE_LOCATION_COMMENT"),
                      represent=lambda r: str(db(db.store_location.id == r).select(db.store_location.label).first().label) if r else None,
                      required=True,
                      notnull=True,
                     ),
                Field('entity',
                      db.entity,
                      label=cc.get_string("DB_COMMAND_ENTITY_LABEL"),
                      comment=cc.get_string("DB_COMMAND_ENTITY_COMMENT")),
                Field('subteam',
                      'string',
                      label=cc.get_string("DB_COMMAND_SUBTEAM_LABEL"),
                      comment=cc.get_string("DB_COMMAND_SUBTEAM_COMMENT"),
                      required=True,
                      notnull=True,
                     ),
                Field('creation_datetime',
                      'datetime',
                      writable=False,
                      readable=True,
                      default=datetime.now()),
                Field('modification_datetime',
                      'datetime',
                      writable=False,
                      readable=True,
                      default=datetime.now(),
                      update=datetime.now()),
                Field('supplier',
                      db.supplier,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_COMMAND_SUPPLIER_LABEL"),
                      comment=cc.get_string("DB_COMMAND_SUPPLIER_COMMENT"),
                      represent=lambda r: str(db(db.supplier.id == r).select(db.supplier.label).first().label) if r else None),
                Field('unit_price',
                      'double',
                      label=cc.get_string("DB_COMMAND_UNIT_PRICE_LABEL"),
                      comment=cc.get_string("DB_COMMAND_UNIT_PRICE_COMMENT")),
                Field('funds',
                      'string',
                      label=cc.get_string("DB_COMMAND_FUNDS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_FUNDS_COMMENT"),
                      required=True,
                      notnull=True,
                     ),
                Field('reference',
                      'string',
                      label=cc.get_string("DB_COMMAND_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_COMMAND_REFERENCE_COMMENT")),
                Field('product_reference',
                      'string',
                      label=cc.get_string("DB_COMMAND_PRODUCT_REFERENCE_LABEL"),
                      comment=cc.get_string("DB_COMMAND_PRODUCT_REFERENCE_COMMENT")),
                Field('retailer',
                      'string',
                      label=cc.get_string("DB_COMMAND_RETAILER_LABEL"),
                      comment=cc.get_string("DB_COMMAND_RETAILER_COMMENT")),
                 Field('comment',
                      'text',
                      label=cc.get_string("DB_COMMAND_COMMENT_LABEL"),
                      comment=cc.get_string("DB_COMMAND_COMMENT_COMMENT")),
                )


db.command.product.requires = IS_NOT_EMPTY()
db.command.status.requires = IS_IN_DB(db, db.command_status.id, lambda field: T(field.label), orderby=db.command_status.rank)
db.command.status.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')
db.command.volume_weight.requires = [IS_NOT_EMPTY(), IS_FLOAT_IN_RANGE(cc.MIN_FLOAT, cc.MAX_FLOAT)]
db.command.volume_weight.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
# prevent users from giving a volume_weight without a unit
db.command.unit.requires = IS_IN_DB(db, db.unit.id, db.unit._format) if request.vars.volume_weight != '' else IS_EMPTY_OR(IS_IN_DB(db, db.unit.id, db.unit._format))
db.command.unit.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')
db.command.nb_items.requires = IS_INT_IN_RANGE(1, 31)
db.command.nb_items.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.command.supplier.requires = IS_EMPTY_OR(IS_IN_DB(db, db.supplier.id, '%(label)s'))
db.command.funds.requires = IS_NOT_EMPTY()
db.command.funds.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')
db.command.store_location.requires = IS_IN_DB_AND_USER_STORE_LOCATION(db(db.store_location.can_store==True), db.store_location.id, db.store_location._format, orderby=db.store_location.label_full_path)
db.command.store_location.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')
db.command.entity.requires = IS_IN_DB_AND_USER_ENTITY(db(db.entity.id > 0), db.entity.id, db.entity._format)
db.command.entity.widget = lambda field, value: SQLFORM.widgets.options.widget(field, value, _class='required')
db.command.subteam.requires = IS_NOT_EMPTY()
db.command.subteam.widget = lambda field, value: SQLFORM.widgets.string.widget(field, value, _class='required')

db.define_table('command_log',
                Field('command',
                      db.command),
                Field('modifier',
                      db.person,
                      ondelete='NO ACTION',
                      label=cc.get_string("DB_COMMAND_LOG_MODIFIER_LABEL"),
                      comment=cc.get_string("DB_COMMAND_LOG_MODIFIER_COMMENT"),
                      compute=lambda r: db.person[auth.user.id] if auth.user else None,
                      writable=False,
                      readable=True,
                      represent=lambda r: str(db(db.person.id==r).select(db.person.email).first().email) if r else None),
                Field('before_status',
                      db.command_status,
                      label=cc.get_string("DB_COMMAND_LOG_BEFORE_STATUS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_LOG_BEFORE_STATUS_COMMENT"),
                      required=True,
                      notnull=True,
                      represent=lambda r: T(r.label)),
                Field('after_status',
                      db.command_status,
                      label=cc.get_string("DB_COMMAND_LOG_AFTER_STATUS_LABEL"),
                      comment=cc.get_string("DB_COMMAND_LOG_AFTER_STATUS_COMMENT"),
                      required=True,
                      notnull=True,
                      represent=lambda r: T(r.label)),
                Field('log_datetime',
                      'datetime',
                      label=cc.get_string("DB_COMMAND_LOG_DATETIME_LABEL"),
                      comment=cc.get_string("DB_COMMAND_LOG_DATETIME_COMMENT"),
                      default=datetime.now()),
                )


auth.define_tables(username=False) # creates all needed tables

# for the online users DIV
session['auth_user_email'] = auth.user.email if auth.user else None

current.db = db
current.auth = auth
current.settings = settings
