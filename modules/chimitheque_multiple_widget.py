# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id: chimitheque_multiple_widget.py 210 2015-05-11 08:46:57Z tbellemb $
# -*- coding: utf-8 -*-
from gluon import current
from gluon.html import DIV
from gluon.html import IMG
from gluon.html import INPUT
from gluon.html import SCRIPT
from gluon.html import SPAN
from gluon.html import URL
from gluon.html import XML
from types import ListType
from types import StringType
from uuid import uuid4
import json
from chimitheque_logger import chimitheque_logger
mylogger = chimitheque_logger()


class CHIMITHEQUE_MULTIPLE_widget:

    def __init__(self,
                 ref_field,
                 configuration={'*': ''},
                 minchar=2,
                 max_item_length=40,
                 text_confirm_empty_form_field=None,
                 **attributes):

        # reference field (table we will query to autocomplete)
        self.ref_field = ref_field
        # minimum characters to start autocompletion
        self.minchar = minchar
        # max suggestions displayed
        self.max_item_length = max_item_length
        # a dictionary containing configuration options
        self.configuration = configuration
        # an uid to identify the widget
        self.uid = uuid4().hex

        # widget images
        self.image_insert_url = URL('static', 'images/cmw_insert.png')
        self.image_select_url = URL('static', 'images/cmw_select.png')
        self.image_delete_url = URL('static', 'images/cmw_delete.png')
        self.image_disable_url = URL('static', 'images/field_disable.png')

        # widget strings
        self.text_confirm_empty_form_field = current.T(u'confirm empty field') if text_confirm_empty_form_field is None else text_confirm_empty_form_field
        self.text_delete = current.T(u'delete item')
        self.text_no_item_selected = current.T(u'no item selected')
        self.text_item_already_selected = current.T(u'item already selected')
        self.text_submit = current.T(u'submit')
        self.text_close_list = current.T(u'close list')

        # other attributes
        self.attributes = attributes
        if '_class' not in attributes.keys():
            self.attributes['_class'] = 'not_required'

        mylogger.debug(message='ref_field._tablename:%s' % (str(ref_field._tablename)))
        mylogger.debug(message='ref_field.name:%s' % (str(ref_field.name)))
        mylogger.debug(message='ref_field.type:%s' % (str(ref_field.type)))

    def __call__(self, field, value):

        mylogger.debug(message='current.request.vars:%s' % current.request.vars)
        mylogger.debug(message='field._tablename:%s' % (str(field._tablename)))
        mylogger.debug(message='field:%s' % (str(field)))
        mylogger.debug(message='field.name:%s' % (str(field.name)))
        mylogger.debug(message='field.type:%s' % (str(field.type)))
        mylogger.debug(message='field.requires:%s' % (str(field.requires)))
        mylogger.debug(message='type(value):%s' % (str(type(value))))
        mylogger.debug(message='value:%s' % (str(value)))

        if current.request and current.request['function']: function = current.request['function']
        function_configuration = self.configuration['*'] if self.configuration.keys().count('*') > 0 else self.configuration[function] if function in self.configuration.keys() else ''

        # query parameter not used yet...
        if 'query' in function_configuration:
            query = function_configuration['query'].as_json()
        else:
            query = None
        if 'disable_validate' in function_configuration:
            disable_validate = function_configuration['disable_validate']
        else:
            disable_validate = False
        if 'add_in_db' in function_configuration:
            add_in_db = function_configuration['add_in_db']
        else:
            add_in_db = False
        if 'multiple' in function_configuration:
            multiple = function_configuration['multiple']
        else:
            multiple = False
        if 'submit_on_select' in function_configuration:
            submit_on_select = function_configuration['submit_on_select']
        else:
            submit_on_select = False
        max_nb_item = 20
        if 'max_nb_item' in function_configuration:
            max_nb_item = function_configuration['max_nb_item']
        func_lambda = ''
        if 'func_lambda' in function_configuration:
            func_lambda = function_configuration['func_lambda']
        # use this option for no required fields only, to force the user to confirm that the field is empty
        if 'confirm_empty' in function_configuration:
            confirm_empty = function_configuration['confirm_empty']
        else:
            confirm_empty = current.request.vars['confirm_empty_%s' % field.name] == 'on' if 'confirm_empty_%s' % field.name in current.request.vars else False

        is_not_a_reference = (field._tablename == self.ref_field._tablename)

        disabled = '_disabled' in self.attributes.keys()
        mylogger.debug(message='add_in_db:%s' % (str(add_in_db)))
        mylogger.debug(message='multiple:%s' % (str(multiple)))
        mylogger.debug(message='disabled:%s' % (str(disabled)))
        mylogger.debug(message='max_nb_item:%s' % (str(max_nb_item)))
        mylogger.debug(message='is_not_a_reference:%s' % (str(is_not_a_reference)))

        if (value) and (type(value) is StringType) and (value == '0'): nb_item = 0
        elif (value) and (type(value) is StringType) and (value == '|0|'): nb_item = 0
        elif (value) and (type(value) is ListType) and (value[0] == 0): nb_item = 0
        elif (value) and (type(value) is ListType) and (value[0] == '|0|'): nb_item = 0
        elif (value) and (type(value) is ListType): nb_item = len(value)
        elif value and value != '': nb_item = 1
        else: nb_item = 0

        if value and not type(value) is ListType and value != '': value = [value]

        mylogger.debug(message='nb_item:%s' % (str(nb_item)))

        #
        # basic widget structure
        #
        checkboxes_form = DIV()
        suggestions_form = DIV(_id='%s_suggestions' % (self.uid), _class='CHIMITHEQUE_MULTIPLE_widget_suggestions')
        message_form = DIV(_id='%s_message' % (self.uid), _class='CHIMITHEQUE_MULTIPLE_widget_message', _style='display: none;')

        search_input_form = DIV(INPUT(_name='%s_search' % self.uid, _type='text', _title='%s_search' % self.uid),
                                 suggestions_form,
                                 _id='%s_search' % (self.uid),
                                 _class='search_input_form')

        #
        # adding a confirm empty checkbox if needed
        #
        if confirm_empty:

            confirm_empty_form = DIV(INPUT(_name='confirm_empty_%s' % field.name,
                             _id='confirm_empty_%s' % field.name,
                             _type='checkbox',
                             _title=self.text_confirm_empty_form_field,
                             _class='CHIMITHEQUE_MULTIPLE_widget_confirm_empty',
                             _onclick='''$('div[id=%(uid)s]').empty();

                                         if ($('input[type=checkbox][name=confirm_empty_%(field_name)s]').is(':checked')) {
                                             $('div[id=%(uid)s]').append('<span id="%(field_name)s_span_no_selected"></span>');
                                         }
                                         else {
                                             $('div[id=%(uid)s]').append('<span id="%(field_name)s_span_no_selected">%(no_item_selected)s</span>');
                                         }
                             ''' % {'uid': self.uid,
                                    'field_name': field.name,
                                    'no_item_selected': self.text_no_item_selected}))
            
            confirm_empty_form.append(IMG(_src=self.image_disable_url,
                                      _alt='disable',
                                      _id='%s_disable' % self.uid,
                                      _title=self.text_confirm_empty_form_field))
        else:
            confirm_empty_form = DIV()

        #
        # building the AJAX query parameters
        #
        _ajax_parameters = {
                           'uid': self.uid,
                           'multiple': multiple,
                           'disable_validate': disable_validate,
                           'add_in_db': add_in_db,
                           'field_tablename': field._tablename,
                           'ref_field_tablename': self.ref_field._tablename,
                           'ref_field_name': self.ref_field.name,
                           'max_nb_item': max_nb_item,
                           'max_item_length': self.max_item_length,
                           'lambda': func_lambda,
                           'query': query,
                           'text_close_list': str(self.text_close_list),
                           'text_submit': str(self.text_submit),
                           'image_select_url': self.image_select_url,
                           'submit_on_select': submit_on_select
                           }
        ajax_parameters = json.dumps(_ajax_parameters)

        #
        # adding the "add" image
        #
        if not disabled and add_in_db:

                search_input_form.append(IMG(_src=self.image_insert_url,
                                      _alt='submit',
                                      _id='%s_add' % self.uid,
                                      _title=self.text_submit,
                                      _style='visibility: hidden;',
                                      _class='CHIMITHEQUE_MULTIPLE_widget_addindb',
                                      _onclick='''
                                            // adding the search parameter to the JSON object
                                            ajax_parameters = %(ajax_parameters)s;
                                            ajax_parameters["search"] = $('input[name=%(uid)s_search]').val();
                                            var ret = $.ajax({
                                                       type: "POST",
                                                       url: "/%(application)s/chimitheque_multiple_widget/item_add",
                                                       data: JSON.stringify(ajax_parameters),
                                                       dataType: "json",
                                                       contentType: "application/json; charset=utf-8",
                                                       async: false
                                                     }).done(function(data) {
                                                            var _action = data['action'];
                                                            var _id = data['id'];
                                                            var _val = data['val'];
                                                            var _encval = data['encval'];

                                                            var funcCall = "addReplaceCheckBox%(uid)s" + "('" + _action + "','" + _id + "','" + _val + "','" + _encval + "')";
                                                            eval(funcCall);

                                                            $('img#%(uid)s_add').attr('style', 'visibility: hidden;');
                                                        });
                                                    ''' % {'uid': self.uid,
                                                           'application': current.request.application,
                                                           'ajax_parameters': ajax_parameters}))

        #
        # adding the selected items DIV
        #
        if nb_item == 0:

            if 'confirm_empty_%s' % field.name in current.request.vars:
                checkboxes_form.append(SPAN())
            else:
                checkboxes_form.append(SPAN(XML(self.text_no_item_selected),
                                            _id='%s_span_no_selected' % field.name))
            hidden_box_form = DIV(INPUT(_name='%s' % field.name,
                                        _id='%s_hidden' % field.name,
                                        _type='checkbox',
                                        _value='',
                                        _style='visibility: hidden; height: 0px;',
                                        _checked='checked',
                                        requires=field.requires))
        else:
            hidden_box_form = DIV()

            #
            # prepopulating the form
            #
            for i in range(0, nb_item):

                mylogger.debug(message='i:%i' % (i))

                prepop_value_id = None
                prepop_value_label = None

                if is_not_a_reference:
                    # just populating with the value passed in parameter
                    mylogger.debug(message='case 1')
                    prepop_value_id = value[i]
                    prepop_value_label = value[i]
                else:
                    # the parameter value is an id in the reference table, then querying the table
                    mylogger.debug(message='case 2')
                    prepop_value = current.db(current.db['%s' % self.ref_field._tablename]['id'] == (value[i])).select().first()
                    if prepop_value is not None:
                        prepop_value_label = current.db['%s' % self.ref_field._tablename]._format(prepop_value)
                        prepop_value_id = value[i]

                mylogger.debug(message='prepop_value_id:%s' % prepop_value_id)
                mylogger.debug(message='prepop_value_label:%s' % prepop_value_label)

                if prepop_value_id:
                    #
                    # adding the checkboxes or radio for the selected items
                    #
                    if multiple:
                        _input = INPUT(_name='%s' % field.name,
                                         _id='%s' % field.name,
                                         _type='checkbox',
                                         _class='CHIMITHEQUE_MULTIPLE_widget_selected',
                                         _encvalue=self.uid,
                                         _value=prepop_value_id,
                                         value=True,
                                         requires=field.requires)
                    else:
                        if is_not_a_reference:
                            _input = INPUT(_name='%s' % field.name,
                                             _id='%s' % field.name,
                                             _type='radio',
                                             _class='CHIMITHEQUE_MULTIPLE_widget_selected',
                                             _encvalue=self.uid,
                                             _value=prepop_value_label, # or prepop_value_id, don't mind...
                                             value=prepop_value_label, # or prepop_value_id, don't mind...
                                             requires=field.requires)
                        else:
                            _input = INPUT(_name='%s' % field.name,
                                             _id='%s' % field.name,
                                             _type='radio',
                                             _class='CHIMITHEQUE_MULTIPLE_widget_selected',
                                             _encvalue=self.uid,
                                             _value=prepop_value_id,
                                             value=prepop_value_id,
                                             requires=field.requires)
                    #
                    # then the delete selected item image
                    #
                    if not disabled and not multiple:

                        img_del = IMG(_src=self.image_delete_url,
                                      _alt=self.text_delete,
                                      _title=self.text_delete,
                                      _onclick='deleteItem%s();' % self.uid, _style='float: left;')

                    else:

                        img_del = SPAN()

                    #
                    # then the label
                    #
                    checkboxes_form.append(DIV(_input,
                                               img_del,
                                               XML('%s' % prepop_value_label),
                                               _class='CHIMITHEQUE_MULTIPLE_widget_selected'))

                else:
                    # TODO: code identical to line 232...

                    if 'confirm_empty_%s' % field.name in current.request.vars:
                        checkboxes_form.append(SPAN())
                    else:
                        checkboxes_form.append(SPAN(XML(self.text_no_item_selected),
                                                    _id='%s_span_no_selected' % field.name))
                    hidden_box_form = DIV(INPUT(_name='%s' % field.name,
                                                _id='%s_hidden' % field.name,
                                                _type='checkbox',
                                                _value='',
                                                _style='visibility: hidden; height: 0px;',
                                                _checked='checked',
                                                requires=field.requires))

        #
        # building the final form
        #
        final_form = DIV(DIV(DIV(checkboxes_form,
                                 _id='%s' % self.uid,
                                 _class='%s_%s' % (self.ref_field._tablename, self.ref_field.name)),
                             **self.attributes))

        if not disabled:
            final_form.insert(0, confirm_empty_form)
            final_form.insert(0, search_input_form)

        # hidden field to export the uid for the pages
        uid_field = INPUT(_name='uid_%s' % field.name,
                          _type='hidden',
                          value='%s' % self.uid,
                          style='visibility: hidden; height: 0px;')

        return DIV(final_form,
                   uid_field,
                   hidden_box_form,
                   message_form,
                   SCRIPT(
                          """
                            function disableAddButton%(uid)s() {
                                $('#%(uid)s_add').attr('style', 'visibility: hidden;');

                            }

                            function displayMessage%(uid)s(message) {
                                $('#%(uid)s_message span').remove();
                                $('#%(uid)s_message').append('<span class="error">' + message + '</span>');

                            }

                            function deleteItem%(uid)s() {
                                $('#%(uid)s').find('div[class=CHIMITHEQUE_MULTIPLE_widget_selected]').remove();

                                console.log($('input[name=%(field_name)s]').length);
                                /* enabling the hidden field if needed */
                                if ($('input[name=%(field_name)s]').length <= 1) {
                                    console.log("input name '%(field_name)s' was the last element");
                                    $('input[id=%(field_name)s_hidden]').removeAttr('disabled');
                                    $('div[id=%(uid)s]').append('<span id="%(field_name)s_span_no_selected">%(no_item_selected)s</span>');
                                }
                                else {
                                    console.log("input name '%(field_name)s' was not the last element");
                                }
                            }

                            function addReplaceCheckBox%(uid)s(action, id, val, encval) {
                                    console.log(arguments.callee.name);
                                    console.log('action:' + action);
                                    console.log('id:' + id);
                                    console.log('val:' + val);
                                    console.log('encval:' + encval);

                                    /* base64 decoding the string */
                                    val = Base64.decode(val);

                                    /* disabling the hidden field */
                                    $('input[id=%(field_name)s_hidden]').attr('disabled','true');
                                    $('span[id=%(field_name)s_span_no_selected]').remove();

                                    if ($('#%(uid)s').find('input[value="'+id+'"][encvalue='+encval+']').length != 0) {
                                        alert('%(text_item_already_selected)s');
                                    }
                                    else {
                                        var newDiv = $('<div class="CHIMITHEQUE_MULTIPLE_widget_selected"/>');
                                        var newDel = $('<img/>').attr({
                                            'src': '%(image_delete_url)s',
                                            'alt': '%(image_delete_alt)s',
                                            'title': '%(image_delete_title)s',
                                            'onclick': 'deleteItem%(uid)s();'
                                        });
                                        var newElem = $('<input/>').attr({
                                            'id': '%(field_name)s',
                                            'type': '%(type)s',
                                            'checked': 'checked',
                                            'name': '%(field_name)s',
                                            'value': id,
                                            'class': 'CHIMITHEQUE_MULTIPLE_widget_selected',
                                            'encvalue': encval,
                                        });
                                        if (action == 'replace') {
                                            newDiv.append(newDel);
                                        }
                                        newDiv.append(newElem);
                                        newDiv.append(val);
                                        if (action == 'replace') {
                                            $('#%(uid)s div').remove();
                                        }
                                        $('#%(uid)s').append(newDiv);
                                    }
                                    $('input[name=%(uid)s_search]').val('');

                                    $('#' + encval + '_suggestions div').remove();

                            }

                            function autocomplete%(uid)s() {
                                   $elem = $('input[type=text][name=%(uid)s_search]')
                                   var inputLength = $elem.val().length;
                                   if (inputLength >= %(minchar)s) {
                                        // adding the search parameter to the JSON object
                                        ajax_parameters = %(ajax_parameters)s;
                                        ajax_parameters["search"] = $elem.val();
                                        var ret = $.ajax({
                                                   type: "POST",
                                                   url: "/%(application)s/chimitheque_multiple_widget/item_selector",
                                                   data: JSON.stringify(ajax_parameters),
                                                   dataType: "json",
                                                   contentType: "application/json; charset=utf-8",
                                                   async: false
                                                 }).responseText;

                                        $('#%(uid)s_suggestions > *').remove();
                                        $('#%(uid)s_message').show();
                                        $('#%(uid)s_message').text('');
                                        if (ret.substr(0, 5) == 'ERROR') {
                                            $('#%(uid)s_message').text(ret);
                                            $('#%(uid)s_add').attr('style', 'visibility: hidden;');
                                        }else if (ret.substr(0, 4) == 'INDB'){
                                            $('#%(uid)s_add').attr('style', 'visibility: hidden;');
                                            $('#%(uid)s_suggestions').append(ret);
                                        }else if (ret.substr(0, 4) == 'NONE'){
                                            $('#%(uid)s_add').attr('style', 'visibility: visible;');
                                        }
                                        else {
                                            $('#%(uid)s_add').attr('style', 'visibility: visible;');
                                            $('#%(uid)s_suggestions').append(ret);
                                        }
                                   }
                            }

                            $(document).ready(function() {

                                jQuery('input[type=text][name=%(uid)s_search]').bind('paste', function(e) {
                                    setTimeout(function() {
                                        autocomplete%(uid)s();
                                    }, 0);
                                });

                                timer = 0;
                                jQuery('input[type=text][name=%(uid)s_search]').bind('keypress click paste input',function() {
                                        if (timer) {
                                            clearTimeout(timer);
                                        }
                                        timer = setTimeout(autocomplete%(uid)s, 400);                                  
                                });

                            });
                          """ %{'disable_validate': disable_validate,
                                'add_in_db': add_in_db,
                                'multiple': multiple,
                                'uid': self.uid,
                                'field_tablename': field._tablename,
                                'field_name': field.name,
                                'field_label': field.label,
                                'ref_field_tablename': self.ref_field._tablename,
                                'ref_field_name': self.ref_field.name,
                                'minchar': self.minchar,
                                'image_delete_url': self.image_delete_url,
                                'image_delete_alt': self.text_delete,
                                'image_delete_title': self.text_delete,
                                'type': 'checkbox' if multiple else 'radio',
                                'max_nb_item': max_nb_item,
                                'max_item_length': self.max_item_length,
                                'lambda': func_lambda,
                                'image_delete_small': self.image_delete_url,
                                'text_item_already_selected': self.text_item_already_selected,
                                'no_item_selected': self.text_no_item_selected,
                                'application': current.request.application,

                                'ajax_parameters': ajax_parameters
                                }),
                            _class='CHIMITHEQUE_MULTIPLE_widget'
                          )
