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
# $Id: chimitheque_multiple_widget.py 210 2015-05-11 08:46:57Z tbellemb $
#
import base64
import json
import re
from types import ListType

from chimitheque_logger import chimitheque_logger
from fake import *

mylogger = chimitheque_logger()


def lambdaempiricalformula(formula):
    existing_atoms = sorted(current.settings['atom_array'].keys(), key=lambda atom: len(atom), reverse=True)
    regex = '(' + '|'.join([_atom + '[0-9]*' for _atom in existing_atoms]) + ')'
    mylogger.debug(message='regex:%s' % regex)
    return '%%'.join([_atom for _atom in filter(lambda v: v != '', re.split(regex, formula))])


def lambdaname(label):
    return label.replace('-', '_')


def item_add():

    # getting request vars and keys
    request_vars = request.vars # a Gluon.storage.Storage object
    mylogger.debug(message='request_vars:%s' %request_vars)

    # getting the request vars
    uid = request_vars['uid']
    multiple = request_vars['multiple']
    field_tablename = request_vars['field_tablename']
    ref_field_tablename = request_vars['ref_field_tablename']
    ref_field_name = request_vars['ref_field_name']
    search = request_vars['search'].strip()

    mylogger.debug(message='search:%s' %search)
    mylogger.debug(message='type(search):%s' %type(search))
    mylogger.debug(message='ref_field_tablename:%s' % ref_field_tablename)
    mylogger.debug(message='ref_field_name:%s' % ref_field_name)

    is_not_a_reference = (field_tablename == ref_field_tablename)

    if search == '':
            return ''

    _requires = db['%s' %ref_field_tablename]['%s' % ref_field_name].requires
    mylogger.debug(message='_requires:%s' % _requires)

    (value, error) = db['%s' %ref_field_tablename]['%s' %ref_field_name].validate(search.encode('utf8'))
    value = value.decode('utf-8')
    value = value.replace("'", "\'")
    mylogger.debug(message='value:%s' % value)
    mylogger.debug(message='error:%s' % error)
    if error:
        mylogger.debug(message='error')
        return DIV('',
                   SCRIPT("""
                        jQuery(function() {
                            displayMessage%s('%s');
                        });
                        """ %(uid, '%s: %s insert -> %s' %('ERROR', value, error))))
    elif not is_not_a_reference:
        mylogger.debug(message='no error')
        search = value

        try:
            db['%s' %ref_field_tablename].bulk_insert([{'%s' %ref_field_name: value}])
        except:
            mylogger.debug(message='exception catch bulk_insert')
            return DIV('',
                       SCRIPT("""
                              jQuery(function() {
                                  displayMessage%s('%s');
                              });
                              """ %(uid, '%s: %s bulk_insert -> %s' %('ERROR', value, error))))

        row = db((db['%s' %ref_field_tablename]['%s' %ref_field_name] == value)).select().first()
        mylogger.debug(message='row:%s' %row)

        inserted_id = row['id']
        inserted_val = db['%s' %ref_field_tablename]._format(row)
    else:
        inserted_id = value
        inserted_val = value

    mylogger.debug(message='type(inserted_val):%s' %type(inserted_val)) # <type 'str'>
    inserted_val = inserted_val.decode('utf-8')
    mylogger.debug(message='inserted_val:%s' %inserted_val)

    #inserted_val = inserted_val.replace("'", "\\'")

    if multiple:
        action = 'add'
    else:
        action = 'replace'

    return json.dumps({'action': action,
                       'id': inserted_id,
                       'val': base64.b64encode(inserted_val.encode('utf-8')),
                       'encval': uid})


def item_selector():

    # getting request vars and keys
    request_vars = request.vars # a Gluon.storage.Storage object
    mylogger.debug(message='request_vars:%s' %request_vars)

    # getting the request vars
    uid = request_vars['uid']
    multiple = request_vars['multiple']
    disable_validate = request_vars['disable_validate']
    field_tablename = request_vars['field_tablename']
    ref_field_tablename = request_vars['ref_field_tablename']
    ref_field_name = request_vars['ref_field_name']
    search = request_vars['search'].strip()
    max_nb_item = int(request_vars['max_nb_item'])
    max_item_length = int(request_vars['max_item_length'])
    func_lambda = request_vars['lambda']
    text_close_list = request_vars['text_close_list']
    text_submit = request_vars['text_submit'],
    image_select_url = request_vars['image_select_url']
    submit_on_select = request_vars['submit_on_select']

    is_not_a_reference = (field_tablename == ref_field_tablename)

    mylogger.debug(message='search:%s' % search)
    mylogger.debug(message='type(search):%s' % type(search)) # Unicode here
    mylogger.debug(message='field_tablename:%s' % field_tablename)
    mylogger.debug(message='ref_field_tablename:%s' % ref_field_tablename)
    mylogger.debug(message='ref_field_name:%s' % ref_field_name)
    mylogger.debug(message='is_not_a_reference:%s' % is_not_a_reference)
    mylogger.debug(message='submit_on_select:%s' % submit_on_select)

    # search var empty = return
    if search == '':
        return ''

    # validating the entry
    error = False

    if not disable_validate:
        _requires = db['%s' %ref_field_tablename]['%s' %ref_field_name].requires
        mylogger.debug(message='_requires:%s' %_requires)

        # removing IS_NOT_IN_DB if present
        # we do not want to throw an error if the value is not in DB
        # note: this procedure will not work with recursive validators
        if type(_requires) is not ListType:
            _requires = [_requires]
        _new_requires = []
        is_in_db = False
        for _require in _requires:
            mylogger.debug(message='type(_require):%s' %type(_require))
            if not isinstance(_require, IS_NOT_IN_DB):
                mylogger.debug(message='_require not IS_NOT_IN_DB')
                _new_requires.append(_require)

        # validating
        mylogger.debug(message='_new_requires:%s' %_new_requires)
        db['%s' %ref_field_tablename]['%s' %ref_field_name].requires = _new_requires
        (search, error) = db['%s' %ref_field_tablename]['%s' %ref_field_name].validate(search.encode('utf8'))

        search = search.decode('utf-8')
        error = error.decode('utf-8') if error is not None else None

        mylogger.debug(message='type(search):%s' % type(search))
        mylogger.debug(message='type(error):%s' % type(error))
        mylogger.debug(message='search:%s' % search)
        mylogger.debug(message='error:%s' % error)

    if error:
        return '%s: %s -> %s' % ('ERROR', search, error)

    else:
        #mylogger.debug(message='search:%s' %search)

        # calling lambda
        if func_lambda != '':
            search = eval(func_lambda)(search)
            mylogger.debug(message='search:%s' %search)

        # search already in DB ?
        _count = db(db['%s' %ref_field_tablename]['%s' %ref_field_name] == '%s' %search).count()
        mylogger.debug(message='_count:%s' %_count)
        is_in_db = _count != 0

        # requesting the DB
        suggestions = []

        _search = search.lower()
        mylogger.debug(message='_search:%s' %_search)
        mylogger.debug(message='type(_search):%s' %type(_search))
        req1 = db(
            (db['%s' %ref_field_tablename]['%s' %ref_field_name].lower().like('%s%%' %_search))).select(orderby=ref_field_name, limitby=(0, max_nb_item))
        req2 = db(
            (db['%s' %ref_field_tablename]['%s' %ref_field_name].lower().like('%%%s%%' %_search))).select(orderby=ref_field_name, limitby=(0, max_nb_item))
        req3 = db(
            (db['%s' %ref_field_tablename]['%s' %ref_field_name].lower().like('%%|%%%s%%|%%' %_search))).select(orderby=ref_field_name, limitby=(0, max_nb_item))

        for _req in req1:
            _suggestion = db['%s' %ref_field_tablename]._format(_req)
            #
            # backward compatibility: some entries may have been stored with different encodings ISO-8859-1 ISO-8859-2 windows-1250...
            # so we utf8 decode the entry with the errors='replace' to get a pure Unicode object
            #
            _suggestion = _suggestion.decode('utf8', errors='replace')
            suggestion_txt = suggestion_txt_small = _suggestion
            if len(suggestion_txt) > max_item_length:
                suggestion_txt_small = suggestion_txt[0:max_item_length] + '...'
            suggestions.append((_req.id, suggestion_txt, suggestion_txt_small))
        for _req in req2:
            if _req.id not in [suggestion[0] for suggestion in suggestions]:
                _suggestion = db['%s' %ref_field_tablename]._format(_req)
                _suggestion = _suggestion.decode('utf8', errors='replace')
                suggestion_txt = suggestion_txt_small = _suggestion
                if len(suggestion_txt) > max_item_length:
                    suggestion_txt_small = suggestion_txt[0:max_item_length] + '...'
                suggestions.append((_req.id, suggestion_txt, suggestion_txt_small))
        for _req in req3:
            if _req.id not in [suggestion[0] for suggestion in suggestions]:
                _suggestion = db['%s' %ref_field_tablename]._format(_req)
                _suggestion = _suggestion.decode('utf8', errors='replace')
                suggestion_txt = suggestion_txt_small = _suggestion
                if len(suggestion_txt) > max_item_length:
                    suggestion_txt_small = suggestion_txt[0:max_item_length] + '...'
                suggestions.append((_req.id, suggestion_txt, suggestion_txt_small))

        mylogger.debug(message='suggestions:%s' %suggestions)

        if len(suggestions) == 0:
            return 'NONE:%s' % search.encode('utf-8')
        else:
            close_list = A(text_close_list, _onclick="""
                                $('input[name=%s_search]').attr('value', '');
                                $('#%s_suggestions div').remove();
                             """ %(uid, uid)) + BR()
            if multiple:
                action = 'add'
            else:
                action = 'replace'
            if is_in_db:
                script = SCRIPT("""
                                disableAddButton%s();
                                """ % uid)
            else:
                script = SCRIPT("")

            suggestion_list = DIV(close_list,
                                  script,
                                  _id='suggestions_list')

            for _suggestion in suggestions:

                _onclick = """
                           jQuery(function() {
                               addReplaceCheckBox%(uid)s("%(action)s", "%(id)s", "%(val)s", "%(encval)s");
                           """ % { 'uid': uid,
                                   'action': action,
                                   'id': search if is_not_a_reference else _suggestion[0],
                                   'val': base64.b64encode(_suggestion[1].encode('utf-8')),
                                   'encval': uid}
                if submit_on_select:
                    _onclick = _onclick + """
                                   $('#%s').closest("form").submit();
                               });
                    """ % uid
                else:
                    _onclick = _onclick + """
                               });
                    """

                suggestion_list.append(DIV(_suggestion[2],
                                       IMG(_src=image_select_url,
                                           _alt=text_submit,
                                           _title=_suggestion[1]),
                                           _onclick=_onclick,
                                           _class='CHIMITHEQUE_MULTIPLE_widget_suggestion'))

            return suggestion_list
