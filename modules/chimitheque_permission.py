# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_ide_autocomplete import *

import chimitheque_commons as cc
from chimitheque_logger import chimitheque_logger
from gluon.html import INPUT, TABLE, TR, TD, TH, UL, LI, XML, DIV
from gluon.sqlhtml import CheckboxesWidget
from gluon import current

mylogger = chimitheque_logger()

def LINE( back = 0 ):
    return sys._getframe( back + 1 ).f_lineno
def FILE( back = 0 ):
    return sys._getframe( back + 1 ).f_code.co_filename
def FUNC( back = 0):
    return sys._getframe( back + 1 ).f_code.co_name

class PermissionWidget(CheckboxesWidget):

    @classmethod
    def widget(cls, field, value, disable=False, auth_user_permissions=None, **attributes):

        mylogger.debug(message='auth_user_permissions:%s' % auth_user_permissions)
        mylogger.debug(message='value:%s' %value)

        _widget = super(PermissionWidget, cls).widget(field, value, cols=5, **attributes)
        _hidden_fields = []

        for e in _widget.elements('input'):

            _value = e.attributes['_value'] if '_value' in e.attributes else None
            _name = e.attributes['_name']
            checked = e.attributes['_checked'] == 'checked' if '_checked' in e.attributes else False
            mylogger.debug(message='_value:%s' %_value)
            mylogger.debug(message='_name:%s' %_name)

            # tip to "disable" input with None value
            if _value is None:
                e.attributes['_name'] = '%s-renamed-to-disable' % _name

            # disabling checkboxes for default permissions
            if (_value and _value in current.settings['disabled_permissions'].keys()) or disable:
                mylogger.debug(message='NM')
                e.update(_disabled='disabled')
                e.update(_class='NM')

                # checking checkboxes for default permissions set to True
                # adding an hidden field to pass the value in the form
                if not disable and current.settings['disabled_permissions'][_value]:
                        e.update(_checked='checked')
                        _hidden_fields.append(INPUT(_type='hidden', _value=_value, _name=_name))

            # hidding checkboxes for permissions not owned by the authenticated user
            # to avoid action
            elif (auth_user_permissions is not None) and (_value not in auth_user_permissions):
                mylogger.debug(message='blocked')
                e.update(_style='display: none;')
                if checked:
                    e.update(_class='blocked')
                try:
                    e.__delitem__('_checked')
                except KeyError:
                    pass
                # disabling the hidden if the permission was not set
                # we could also remove the input
                if not checked:
                    e.update(_disabled='disabled')

        _v_header1 = [ cc.get_string("PRODUCT_CARD"),
                       cc.get_string("PRODUCT_CARD_RESTRICTED"),
                       cc.get_string("STORAGE_CARD"),
                       cc.get_string("STORAGE_ARCHIVE"),
                       cc.get_string("STORE_LOCATION"),
                       cc.get_string("ENTITY"),
                       cc.get_string("USER"),
                       cc.get_string("COC"),
                       cc.get_string("SUPPLIER"),
                       cc.get_string("MESSAGE"),
                       cc.get_string("COMMAND") ]
        _v_header2 = [ '',
                       '',
                       '*',
                       '*',
                       '*',
                       '*',
                       '*',
                       '',
                       '',
                       '**',
                       '' ]
        _i = 0
        for e in _widget.elements('tr')[:11]:
            e.insert(0, _v_header1[_i])
            _i = _i + 1
        _i = 0
        for e in _widget.elements('tr')[:11]:
            e.insert(6, _v_header2[_i])
            _i = _i + 1

        _h_legend = TR(
                       TR(TD('S: %s' %cc.get_string("PERMISSION_SELECT"), _colspan="7")),
                       TR(TD('R: %s' %cc.get_string("PERMISSION_READ"), _colspan="7")),
                       TR(TD('U: %s' %cc.get_string("PERMISSION_UPDATE"), _colspan="7")),
                       TR(TD('C: %s' %cc.get_string("PERMISSION_CREATE"), _colspan="7")),
                       TR(TD('D: %s' %cc.get_string("PERMISSION_DELETE"), _colspan="7")),
                       TR(TD('*: %s' %cc.get_string("PERMISSION_IN_HIS_ENTITY"), _colspan="7")),
                       TR(TD('**: %s' %cc.get_string("PERMISSION_HIS_MESSAGE"), _colspan="7")))

        _h_header = TR(TH(''),
                       TH('S'),
                       TH('R'),
                       TH('U'),
                       TH('C'),
                       TH('D'),
                       TH(''))

        _widget.element('table').insert(0, _h_header)
        _widget.element('table').insert(0, _h_legend)

        _widget.components.extend(_hidden_fields)

        return _widget

    @staticmethod
    def represent(values):

        if 'admin' in values:
            return 'X'

        _ret = ''
        _i = -1

        for _item in Permission.ITEMS:

            _i = _i + 1

            _ret = _ret + '<div id="value">'

            for _action in Permission.ACTIONS:

                _perm = '%s_%s' %(_action, _item)
                if _perm in values or _perm in current.settings['disabled_permissions'].keys():
                    _ret = _ret + '<img src="%s/%s" title="%s"/>' %(cc.images_base_url,
                                                                    getattr(cc, 'IMAGE_PRIVILEGE_%s' %_action.upper()),
                                                                    cc.get_string('PERMISSION_%s' %_action.upper())) + ' '

            _ret = _ret + '</div>'
            
            _ret = _ret + '<div id="label">%s</div>' %current.T(Permission.LABELS[_i])


        return XML(_ret)

class Permission(object):

    ACTIONS = ('select', 'read', 'update', 'create', 'delete')
    ITEMS = ('pc', 'rpc', 'sc', 'archive', 'sl', 'ent', 'user', 'coc', 'sup', 'message', 'com')
    LABELS = ('product card',
              'restricted product card',
              'storage card',
              'archive',
              'store location',
              'entity',
              'user',
              'class of compounds',
              'supplier',
              'message',
              'command')

    @staticmethod
    def get_permission_label(permission): # permission = an {ACTION}_{ITEM} key

        return Permission.LABELS[Permission.ITEMS.index(permission)]

    @staticmethod
    def get_permission():

        permission = []
        for _item in Permission.ITEMS:
            for _action in Permission.ACTIONS:
                _perm = '%s_%s' %(_action, _item)
                permission.append(_perm)

        return permission
