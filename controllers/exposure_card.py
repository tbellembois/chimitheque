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
# $Id
#
from chimitheque_ide_autocomplete import *

from chimitheque_logger import chimitheque_logger
from c_person_mapper import PERSON_MAPPER
from c_product_mapper import PRODUCT_MAPPER
from c_exposure_card_mapper import EXPOSURE_CARD_MAPPER
from c_exposure_item_mapper import EXPOSURE_ITEM_MAPPER
from chimitheque_multiple_widget import CHIMITHEQUE_MULTIPLE_widget
from time import strftime
import chimitheque_commons as cc
import json
from exceptions import AssertionError
from types import StringType

mylogger = chimitheque_logger()

crud.messages.record_created = cc.get_string("EXPOSURE_CARD_CREATED")
crud.messages.record_updated = cc.get_string("EXPOSURE_CARD_UPDATED")
crud.messages.record_deleted = cc.get_string("EXPOSURE_CARD_DELETED")
crud.messages.submit_button = cc.get_string("SUBMIT")


def _set_exposure_item_attr(exposure_item_id, attribute, value):

    _value, _error = db.exposure_item[attribute].validate(value)
    mylogger.debug(message='_value:%s,_error:%s' % (_value, _error))

    if _error is not None:
        return _error

    exposure_item_mapper = EXPOSURE_ITEM_MAPPER()

    exposure_item = exposure_item_mapper.find(exposure_item_id=exposure_item_id)[0]

    setattr(exposure_item, attribute, value)

    exposure_item_mapper.update(exposure_item)

    return None

def ajx_update_accidental_exposure_type():

    exposure_card_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_card_id:%s' % exposure_card_id)
    mylogger.debug(message='title:%s' % field_value)

    mylogger.debug(message='test:%s' % request.vars)

    _value, _error = db.exposure_card.accidental_exposure_type.validate(field_value)
    mylogger.debug(message='_value:%s,_error:%s' % (_value, _error))

    if _error is not None:
        return json.dumps({'error': _error})

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    exposure_card = exposure_card_mapper.find(exposure_card_id=exposure_card_id)[0]

    setattr(exposure_card, "accidental_exposure_type", field_value)

    exposure_card_mapper.update(exposure_card)

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_accidental_exposure_datetime():

    exposure_card_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_card_id:%s' % exposure_card_id)
    mylogger.debug(message='title:%s' % field_value)

    _value, _error = db.exposure_card.accidental_exposure_datetime.validate(field_value)
    mylogger.debug(message='_value:%s,_error:%s' % (_value, _error))

    if _error is not None:
        return json.dumps({'error': _error})

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    exposure_card = exposure_card_mapper.find(exposure_card_id=exposure_card_id)[0]

    setattr(exposure_card, "accidental_exposure_datetime", field_value)

    exposure_card_mapper.update(exposure_card)

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_accidental_exposure_duration_and_extent():

    exposure_card_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_card_id:%s' % exposure_card_id)
    mylogger.debug(message='title:%s' % field_value)

    _value, _error = db.exposure_card.accidental_exposure_duration_and_extent.validate(field_value)
    mylogger.debug(message='_value:%s,_error:%s' % (_value, _error))

    if _error is not None:
        return json.dumps({'error': _error})

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    exposure_card = exposure_card_mapper.find(exposure_card_id=exposure_card_id)[0]

    setattr(exposure_card, "accidental_exposure_duration_and_extent", field_value)

    exposure_card_mapper.update(exposure_card)

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_exposure_card_title():

    exposure_card_id = request.vars['exposure_card_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_card_id:%s' % exposure_card_id)
    mylogger.debug(message='title:%s' % field_value)

    _value, _error = db.exposure_card.title.validate(field_value)
    mylogger.debug(message='_value:%s,_error:%s' % (_value, _error))

    if _error is not None:
        return json.dumps({'error': _error})

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    exposure_card = exposure_card_mapper.find(exposure_card_id=exposure_card_id)[0]

    setattr(exposure_card, "title", field_value)

    exposure_card_mapper.update(exposure_card)

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_kind_of_work():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='kind_of_work:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'kind_of_work', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_cpe():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = json.loads(request.vars['field_value'])

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='cpe:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'cpe', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(db.exposure_item.cpe.represent(field_value))})

def ajx_update_ppe():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = json.loads(request.vars['field_value'])

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='ppe:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'ppe', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(db.exposure_item.ppe.represent(field_value))})

def ajx_update_nb_exposure():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='nb_exposure:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'nb_exposure', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_exposure_time():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='cpe:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'exposure_time', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

def ajx_update_simultaneous_risk():

    exposure_item_id = request.vars['exposure_item_id']
    field_value = request.vars['field_value']

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)
    mylogger.debug(message='cpe:%s' % field_value)

    _error = _set_exposure_item_attr(exposure_item_id, 'simultaneous_risk', field_value)

    if _error is not None:
        return json.dumps({'error': _error})

    # in case of error, return json.dumps({'error': 'Error message'})
    return json.dumps({'success': True, 'txt': str(field_value)})

@auth.requires_login()
def export_to_csv():

    mylogger.debug(message='request.vars:%s' % request.vars)

    field_names = [
                    'kind_of_work',
                    'cpe',
                    'ppe',
                    'nb_exposure',
                    'exposure_time',
                    'simultaneaous_risk',
                    ]

    if 'exposure_item' not in request.vars:
        return None

    exposure_item_mapper = EXPOSURE_ITEM_MAPPER()

    exposure_item_ids = request.vars['exposure_item']

    if type(exposure_item_ids) is StringType:
        exposure_item_ids = [exposure_item_ids]

    export_list = []

    for exposure_item_id in  exposure_item_ids:

        exposure_item = exposure_item_mapper.find(exposure_item_id=exposure_item_id)[0]

        product_name = exposure_item.product.name.label
        product_cas_number = exposure_item.product.cas_number
        product_cmr_cat = exposure_item.product.cmr_cat
        product_symbol = ','.join([s.label for s in exposure_item.product.symbol])
        product_hazard_statement = ','.join([h.reference for h in exposure_item.product.hazard_statement])

        _row = [product_name,
                product_cas_number,
                product_cmr_cat,
                product_symbol,
                product_hazard_statement]
        for field_name in field_names:

            _field = '%s_%s' % (field_name, exposure_item_id)
            _field_value = request.vars[_field]
            mylogger.debug(message='_field:%s' % _field)
            mylogger.debug(message='_field_value:%s' % _field_value)

            if _field in request.vars:

                if field_name == 'cpe' or field_name == 'ppe':
                    if type(_field_value) is StringType:
                        _row.append(db(db[field_name].id == _field_value).select().first().label)
                    else:
                        _val = ','.join([db(db[field_name].id == _field_value_item).select().first().label for _field_value_item in _field_value])
                        _row.append(_val)
                else:
                    _row.append(_field_value)
            else:
                _row.append('')
        export_list.append(_row)

    mylogger.debug(message='export_list:%s' % export_list)

    response.view = 'product/export_chimitheque.csv'

    export_header = [
                     cc.get_string('DB_PRODUCT_NAME_LABEL'),
                     cc.get_string('DB_PRODUCT_CAS_NUMBER_LABEL'),
                     cc.get_string('DB_PRODUCT_CMR_CATEGORY_LABEL'),
                     cc.get_string('DB_PRODUCT_SYMBOL_LABEL'),
                     cc.get_string('DB_PRODUCT_HAZARD_STATEMENT_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_KIND_OF_WORK_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_CPE_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_PPE_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_NB_EXPOSURE_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_EXPOSURE_TIME_LABEL'),
                     cc.get_string('DB_EXPOSURE_ITEM_SIMULTANEAOUS_RISK_LABEL'),
                    ]

    informations = [
                    '%s %s' % (auth.user.first_name, auth.user.last_name)
                    ]

    return dict(filename='exposure_card_chimitheque.csv',
                informations=informations,
                csvdata=export_list,
                field_names=export_header)


@auth.requires_login()
def list():

    person_mapper = PERSON_MAPPER()

    # getting the auth user
    auth_user = person_mapper.find(person_id=auth.user.id)[0]

    # and his exposure cards
    exposure_cards = sorted(auth_user.exposure_cards, key=lambda x: (x.creation_datetime))

    return dict(exposure_cards=exposure_cards)

@auth.requires_login()
def create():

    person_mapper = PERSON_MAPPER()
    exposure_card_mapper = EXPOSURE_CARD_MAPPER()

    # getting the auth user
    auth_user = person_mapper.find(person_id=auth.user.id)[0]

    auth_user.create_exposure_card(title=strftime("%c"))
    person_mapper.update_exposure_card(auth_user)

    redirect(URL(request.application, 'exposure_card', 'list.html'))

@auth.requires_login()
def update():
    return dict()

@auth.requires_login()
def read():

    mylogger.debug(message='request.vars:%s' % request.vars)

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()
    product_mapper = PRODUCT_MAPPER()
    error = ''

    # getting the exposure card
    exposure_card = exposure_card_mapper.find(exposure_card_id=request.args[0])[0]

    if 'cas_number' in request.vars:
        _product_id = request.vars.cas_number

        # duclicity check not performed by the field validator
        #_value, _error =  db.exposure_item.product.validate(_product_id)
        #mylogger.debug(message='_error, _value:%s, %s' % (_error, _value))

        # but in the c_exposure_card.py class with an exceptions.AssertionError
        _product = product_mapper.find(product_id=_product_id)[0]

        try:
            exposure_card.add_exposure_item_for_product(_product)
            exposure_card_mapper.update(exposure_card)
        except AssertionError, e:
            error = cc.get_string('EXPOSURE_CARD_PRODUCT_ALREADY_PRESENT_ERROR')

    db.product.cas_number.widget = CHIMITHEQUE_MULTIPLE_widget(db.product.cas_number,
                                                               minchar=4,
                                                               configuration={'*': {'add_in_db': False,
                                                                                    'submit_on_select': True}})

    form = SQLFORM.factory(db.product.cas_number)

    return dict(exposure_card=exposure_card,
                form=form,
                error=error)

@auth.requires_login()
def delete():

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()
    person_mapper = PERSON_MAPPER()

    exposure_card = exposure_card_mapper.find(exposure_card_id=request.args[0])[0]

    exposure_card_mapper.delete(exposure_card)

    redirect(URL(request.application, 'exposure_card', 'list.html'))

@auth.requires_login()
def delete_item():

    exposure_item_id = request.args[0]
    exposure_card_id = request.vars.exposure_card_id

    mylogger.debug(message='exposure_item_id:%s' % exposure_item_id)

    exposure_item_mapper = EXPOSURE_ITEM_MAPPER()

    exposure_item = exposure_item_mapper.find(exposure_item_id=exposure_item_id)[0]

    exposure_item_mapper.delete(exposure_item)

    redirect(URL(request.application, 'exposure_card', 'read.html', args=exposure_card_id))


def set_active():

    exposure_card_id = request.args[0]

    mylogger.debug(message='exposure_card_id:%s' % exposure_card_id)

    exposure_card_mapper = EXPOSURE_CARD_MAPPER()
    person_mapper = PERSON_MAPPER()

    # getting the auth user
    auth_user = person_mapper.find(person_id=auth.user.id)[0]

    # desactivating the current active exposure card
    active_ec = auth_user.get_active_exposure_card()
    active_ec.archive = True
    mylogger.debug(message='desactivating:%s' % active_ec)
    exposure_card_mapper.update(active_ec)

    # activating the given exposure card
    given_ec = exposure_card_mapper.find(exposure_card_id=exposure_card_id)[0]
    given_ec.archive = False
    mylogger.debug(message='activating:%s' % given_ec)
    exposure_card_mapper.update(given_ec)

    redirect(URL(request.application, 'exposure_card', 'list.html'))


