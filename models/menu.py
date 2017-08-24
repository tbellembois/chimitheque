# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id
# -*- coding: utf-8 -*-
import chimitheque_strings as cs
from c_store_location_mapper import STORE_LOCATION_MAPPER
from c_entity_mapper import ENTITY_MAPPER
from chimitheque_commons import get_store_location_submenu

#response.title = request.application
#response.subtitle = T('A chemical products management application')
response.meta.author = 'Thomas Bellembois - Elodie Goy'
response.meta.description = 'Chemical product management application'
response.meta.keywords = ''
response.logo = A(IMG(_alt='logo',
                          _src=URL('static','images/logo.png'),
                          _id="logo"),
                          _href=URL(request.application,'default','index.html'))
response.logo_version = A(IMG(_alt='logo_version',
                          _src=URL('static','images/logo_version.png'),
                          _id="logo_version"),
                          _href=URL(request.application,'default','index.html'))
response.logo_lab = A(IMG(_alt='logo_lab',
                          _src=URL('static','images/logo_lab.png'),
                          _id="logo_lab"),
                          _target='new',
                          _href=settings['lab_url'])
response.logo_univ = A(IMG(_alt='logo_univ',
                          _src=URL('static','images/logo_univ.png'),
                          _id="logo_univ"),
                          _target='new',
                          _href=settings['organization_url'])

def build_menu():

    _response_menu = []

    if auth.user:
        _quick_request_menu = []

        _quick_request_menu.append((cc.get_string("MENU_ALL_PC"),
                                    False,
                                    URL(request.application, 'product', 'search.html',
                                    vars={'request': 'all'}),
                                    ))

        if auth.has_permission('select_sc') or \
           auth.has_permission('admin'):
            _quick_request_menu.append((cc.get_string("MENU_PC_BORROW_ENTITY"),
                                        False,
                                        URL(request.application, 'product', 'search.html',
                                        vars={'borrow_entity': '1'}),
                                        ))

        if auth.has_permission('select_sc') or \
           auth.has_permission('admin'):
            _quick_request_menu.append((cc.get_string("MENU_PC_ORG"),
                                        False,
                                        URL(request.application, 'product', 'search.html',
                                        vars={'request': 'organization'}),
                                        ))

        if auth.has_permission('select_sc') or \
           auth.has_permission('admin'):

            for _entity in ENTITY_MAPPER().find(person_id=auth.user.id):

                if _entity.name != 'all_entity':

                    _quick_request_sub_menu = []

                    if auth.has_permission('read_sc') or \
                       auth.has_permission('admin'):

                        for _store_location in STORE_LOCATION_MAPPER().find(entity_id=_entity.id, root=True):

                            if  _store_location.can_store:

                                _quick_request_sub_menu.append((_store_location.name,
                                                                False,
                                                                URL(current.request.application,'product','search.html',
                                                                    vars={'request': 'store_location',
                                                                          'is_in_store_location': _store_location.id,
                                                                          'not_archive': 'True'}),
                                                                get_store_location_submenu(_store_location.id)))
                            else:
                                 _quick_request_sub_menu.append((SPAN(_store_location.name, _class="can_not_store"),
                                                                False,
                                                                None,
                                                                get_store_location_submenu(_store_location.id)))

                    _quick_request_menu.append((_entity.name,
                                               False,
                                               URL(request.application,'product','search.html',
                                                   vars={'request': 'entity',
                                                          'is_in_entity': _entity.id,
                                                          'not_archive': 'True'}),
                                                _quick_request_sub_menu
                                                ))


#     _response_menu = [
#         (cc.get_string("INDEX"), False, URL(request.application,'default','index.html'), []),
#         ]

    if auth.user:

        _tools_menu = []
        if auth.has_permission('read_user') or \
           auth.has_permission('update_sl') or \
           auth.has_permission('update_ent') or \
           auth.has_permission('admin'):
            _tools_menu.append((cc.get_string("MENU_MANAGE_USER"), False, URL(request.application,'entity','search.html')))

        if auth.has_permission('update_coc') or \
           auth.has_permission('admin'):
            _tools_menu.append((cc.get_string("MENU_MANAGE_COC"), False, URL(request.application,'class_of_compounds','list.html')))
            _tools_menu.append((cc.get_string("MENU_MANAGE_PHYSICAL_STATE"), False, URL(request.application,'physical_state','list.html')))

        if auth.has_permission('update_sup') or \
           auth.has_permission('admin'):
            _tools_menu.append((cc.get_string("MENU_MANAGE_SUP"), False, URL(request.application,'supplier','list.html')))

        if auth.has_permission('admin'):
            _tools_menu.append((cc.get_string("ADMIN_TOOL_EXPORT_PRODUCT_DATABASE"),
                                      False,
                                      A(cc.get_string("ADMIN_TOOL_EXPORT_PRODUCT_DATABASE"),
                                        _class='noblockui',
                                        _href=URL(a=request.application, c='product', f='export_to_csv'),
                                        _onclick="displayConsole()")))
            _tools_menu.append((cc.get_string("ADMIN_TOOL_IMPORT_PRODUCT_DATABASE"),
                                      False,
                                      URL(a=request.application, c='product', f='import_from_csv')))

        if auth.has_permission('read_pc') or \
           auth.has_permission('admin'):
            _response_menu.append((cc.get_string("MENU_SEARCH_PC"), False, URL(request.application,'product','search.html'), _quick_request_menu))

        if auth.has_permission('create_pc') or \
           auth.has_permission('admin'):
            _response_menu.append((cc.get_string("MENU_ADD_PC"), False, URL(request.application,'product','create.html'), []))

        if auth.has_permission('read_com') or \
           auth.has_permission('admin'):
            _com_menu = []
            _com_menu.append((cc.get_string("MENU_LIST_COM_MINE"), False, URL(request.application,'command','list.html', vars={'request': 'mine'})))
            _com_menu.append((cc.get_string("MENU_LIST_COM_NEW"), False, URL(request.application,'command','list.html', vars={'request': 'new'})))
            _com_menu.append((cc.get_string("MENU_LIST_COM_ACCEPTED"), False, URL(request.application,'command','list.html', vars={'request': 'accepted'})))
            _com_menu.append((cc.get_string("MENU_LIST_COM_ALL"), False, URL(request.application,'command','list.html', vars={'request': 'all'})))
            _response_menu.append((cc.get_string("MENU_LIST_COM"), False, URL(request.application,'command','list.html'), _com_menu))

        if auth.has_permission('read_user') or \
           auth.has_permission('update_sl') or \
           auth.has_permission('update_ent') or \
           auth.has_permission('update_coc') or \
           auth.has_permission('update_sup') or \
           auth.has_permission('delete_archive') or \
           auth.has_permission('admin'):
           _response_menu.append((cc.get_string("MENU_ADMIN"),
                                  False,
                                  URL(request.application,'tools','list.html'),
                                  _tools_menu))

        _response_menu.append((cc.get_string("MESSAGE"), False, URL(request.application,'message','index.html', [])))

#     _response_menu.append(('test', False, A('test',
#                                             _class='noblockui',
#                                             _href=URL(a=request.application, c='test', f='index.html'),
#                                             _onclick="displayConsole()"), []))

        _response_menu.append((cc.get_string("MENU_EXPOSURE_CARD"),
                               False,
                               URL(request.application,
                                   'exposure_card',
                                   'list.html'),
                               []))

    return _response_menu

if auth.user:
    response.menu = cache.ram('menu_%s' % auth.user.id, lambda: build_menu(), time_expire=3600)
else:
    response.menu = build_menu()

##########################################
## this is here to provide shortcuts
## during development. remove in production
##
## mind that plugins may also affect menu
##########################################

#response.menu+=[
#    (T('Edit'), False, URL('admin', 'default', 'design/%s' % request.application),
#     [
#            (T('Controller'), False,
#             URL('admin', 'default', 'edit/%s/controllers/%s.py' \
#                     % (request.application,request.controller=='appadmin' and
#                        'default' or request.controller))),
#            (T('View'), False,
#             URL('admin', 'default', 'edit/%s/views/%s' \
#                     % (request.application,response.view))),
#            (T('Layout'), False,
#             URL('admin', 'default', 'edit/%s/views/layout.html' \
#                     % request.application)),
#            (T('Stylesheet'), False,
#             URL('admin', 'default', 'edit/%s/static/base.css' \
#                     % request.application)),
#            (T('DB Model'), False,
#             URL('admin', 'default', 'edit/%s/models/db.py' \
#                     % request.application)),
#            (T('Menu Model'), False,
#             URL('admin', 'default', 'edit/%s/models/menu.py' \
#                     % request.application)),
#            (T('Database'), False,
#             URL(request.application, 'appadmin', 'index')),
#            ]
#   ),
#  ]
