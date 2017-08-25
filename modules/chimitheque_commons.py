# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id: chimitheque_commons.py 222 2015-07-21 16:06:35Z tbellemb2 $
from collections import defaultdict
from types import ListType
import urllib2
import ssl
import cPickle
import datetime
import re
import socket
import os

# Go integration
import ctypes

from chimitheque_logger import chimitheque_logger
from gluon.dal import Row
from gluon import current
from gluon.html import URL
from gluon.settings import settings
from c_storage_mapper import STORAGE_MAPPER
import chimitheque_strings as cs

mylogger = chimitheque_logger()

# Go integration
dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(dir_path, 'gochimithequeutils.so'))
mylogger.info(message='Loaded the Go library') 
l2ef = lib.LinearToEmpiricalFormula
l2ef.restype = ctypes.c_char_p
l2ef.argtypes = [ctypes.c_char_p]

MIN_INT = 0
MAX_INT = 100000000
MIN_FLOAT = 0
MAX_FLOAT = 10000000
images_base_url = settings['application_url'] + '/static/images' if 'application_url' in settings else 'static/images'

IMAGE_LOGO = 'logo.png'
IMAGE_LOGO_UNIV = 'logo_univ.png'
UNIV_URL = 'http://www.univ-bpclermont.fr'
LAB_URL = 'http://iccf.univ-bpclermont.fr'
IMAGE_ICEWEASEL = 'iceweasel.png'
IMAGE_FLAG_FR = 'flag_fr.gif'
IMAGE_FLAG_EN = 'flag_en.gif'
IMAGE_WAIT = 'ajax-loader.gif'
IMAGE_MANAGER = 'manager.png'
IMAGE_ADMIN = 'admin.png'
IMAGE_VIRTUAL = 'virtual.png'
IMAGE_EXPORT_CSV = 'export_csv.png'
IMAGE_CLOSE_WINDOW = 'close_window.png'
IMAGE_LAST = 'last.png'
IMAGE_ELODIE = 'elodie.png'
IMAGE_CMR = 'cmr.png'
IMAGE_RADIO = 'radio.png'
IMAGE_LOCK = 'lock.png'
IMAGE_WARNING = 'warning.png'
IMAGE_ENTITY = 'entity.png'
IMAGE_ORGANIZATION = 'organization.png'
IMAGE_UPDATE = 'update.png'
IMAGE_UPDATE_SMALL = 'update_small.png'
IMAGE_UPDATE_STORAGE = 'update_storage.png'
IMAGE_UPDATE_ENTITY = 'update_entity.png'
IMAGE_DELETE = 'delete.png'
IMAGE_DELETE_ARROW_SMALL = 'delete_arrow_small.png'
IMAGE_DELETE_SMALL = 'delete_small.png'
IMAGE_DELETE_SMALL_BLUE = 'delete_small_blue.png'
IMAGE_CONFIRM_SMALL = 'confirm_small.png'
IMAGE_CONFIRM_BIG = 'confirm_big.png'
IMAGE_DESTROY_SMALL = 'destroy_small.png'
IMAGE_UNDESTROY_SMALL = 'undestroy_small.png'
IMAGE_DETAIL = 'detail.png'
IMAGE_DETAIL_SMALL = 'detail_small.png'
IMAGE_ONLINE = 'online.png'
IMAGE_CREATE_MESSAGE = 'create_message.png'
IMAGE_ANSWER_MESSAGE = 'answer_message.png'
IMAGE_UNIMPERSONATE = 'unimpersonate.png'
IMAGE_IMPERSONATE = 'impersonate.png'
IMAGE_BORROW = 'borrow.png'
IMAGE_CLONE_STORAGE = 'clone_storage.png'
IMAGE_CLONE_PRODUCT = 'clone_product.png'
IMAGE_STORE = 'store.png'
IMAGE_STORAGE = 'storage.png'
IMAGE_STORAGE_OTHER = 'storage_other.png'
IMAGE_STORAGE_HISTORY = 'storage_history.png'
IMAGE_STORAGE_ARCHIVE = 'storage_archive.png'
IMAGE_PRODUCT_HISTORY = 'product_history.png'
IMAGE_ENABLE_SMALL = 'enable_small.png'
IMAGE_DISABLE_SMALL = 'disable_small.png'
IMAGE_PRIVILEGE_SELECT = 'privilege_select.png'
IMAGE_PRIVILEGE_READ = 'privilege_read.png'
IMAGE_PRIVILEGE_CREATE = 'privilege_create.png'
IMAGE_PRIVILEGE_UPDATE = 'privilege_update.png'
IMAGE_PRIVILEGE_DELETE = 'privilege_delete.png'
IMAGE_PENDING = 'pending_small.png'
IMAGE_DISABLED = 'disabled_small.png'
IMAGE_BOOKMARK = 'bookmark.png'
IMAGE_UNBOOKMARK = 'unbookmark.png'
IMAGE_QUICK_ADD_EXPOSURE_CARD = 'quick_add_to_exposure_card.png'
IMAGE_QUICK_DELETE_EXPOSURE_CARD = 'quick_delete_to_exposure_card.png'
IMAGE_EXPOSURE_CARD = 'exposure_card.png'
IMAGE_EXPOSURE_CARD_ACTIVE = 'exposure_card_active.png'
IMAGE_EXPOSURE_CARD_ACTIVATE = 'exposure_card_activate.png'
IMAGE_EDIT = 'edit.png'
IMAGE_SAVE = 'save.png'
IMAGE_UNDO = 'undo.png'
IMAGE_CHECK_ALL = 'check_all.png'
IMAGE_COMMAND = 'command.png'
IMAGE_COMMAND_CLONE = 'command_clone.png'

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def flatten(l):
    if isinstance(l,list):
        return sum(map(flatten,l),[])
    else:
        return [l]


def flatten_row(r, label=None):

    _result = {}

    for key in r.keys():
        mylogger.debug(message='key:%s' % key)
        mylogger.debug(message='r(key):%s' % r(key))
        if not isinstance(r(key), Row):
            _label = '%s.%s' % (label, key)

            _i = current.db
            for _field in _label.split('.'):
                _i = getattr(_i, _field)
            mylogger.debug(message='_i:%s' % _i)

            try:
                _represent = _i.represent(r[key])
            except TypeError:
                mylogger.debug(message='TypeError:_i:%s:r[key]:%s' % (_i, r[key]))
                _represent = r[key]

            mylogger.debug(message='_represent:%s' % _represent)
            _result.update({_label: _represent})
        else:
            _result.update(flatten_row(r(key), key))

    return _result


def get_string(the_string):
    """Return strings for the chimitheque_strings.py file
    """
    try:
        _str = getattr(cs, the_string)
        _translated_str = current.T(_str, lazy=False)
        return _translated_str

    except KeyError:
        return current.T(_str, lazy=False)

def create_barecode(product_id):
    """Return the generated barecode from a product
    """
    mylogger.debug(message='create_barecode')
    product_cas_number = current.db(current.db.product.id == product_id).select(current.db.product.cas_number).first().cas_number

    mylogger.debug(message='product_id:%s' % product_id)
    mylogger.debug(message='product_cas_number:%s' % product_cas_number)

    last_storage_id = current.db(current.db.storage).count()
    mylogger.debug(message='last_storage_id:%s' % last_storage_id)

    today = datetime.date.today()
    today = today.strftime('%Y%m%d')

    barecode = '%s_%s_%s.1' % (product_cas_number, today, last_storage_id)
    mylogger.debug(message='barecode:%s' % barecode)

    return barecode

def is_cas_number(value):
    """Check if value is a CAS number.
    
    Returns value or an error.
    """
    if value is None:
        return (value, get_string("CAS_NUMBER_WRONG_FORMAT_ERROR"))
    if value == "0000-00-0":
        return (value, None)
    mylogger.debug(message='value:%s' % value)
    # testing the pattern
    m = re.match("^(?P<groupone>[0-9]{1,7})-(?P<grouptwo>[0-9]{2})-(?P<groupthree>[0-9]{1})$", value)
    if m:
        groupone = m.group('groupone')
        grouptwo = m.group('grouptwo')
        groupthree = m.group('groupthree')
        mylogger.debug(message='groupone:%s' % groupone)
        mylogger.debug(message='grouptwo:%s' % grouptwo)
        mylogger.debug(message='groupthree:%s' % groupthree)
        checkdigit = 0
        for i in range(1, len(groupone)+1):
            mylogger.debug(message='(i+2):%s' % (i+2))
            mylogger.debug(message='groupone[-i]:%s' % groupone[-i])
            checkdigit += (i+2) * int(groupone[-i])
            mylogger.debug(message='checkdigit:%s' % checkdigit)
        checkdigit += int(grouptwo[1]) + 2*int(grouptwo[0])
        checkdigit = checkdigit % 10
        mylogger.debug(message='checkdigit:%s' % checkdigit)
        if checkdigit == int(groupthree):
            return (value, None)
        else:
            return (value, get_string("CAS_NUMBER_CHECK_DIGIT_ERROR"))
    else:
        return (value, get_string("CAS_NUMBER_WRONG_FORMAT_ERROR"))


def get_lastest_app_version(return_string=False):
    """Get the lastest application version.

    return_string -- if True returns a string version_number-version_date
                     else returns a tuple ('version_number', 'version_date').
    """
    url = settings['chimitheque_repository'] + '?format=txt'
    try:
        chimitheque_repository_response = urllib2.urlopen(url, timeout=4)
    except ssl.SSLError:
        return None
    except urllib2.HTTPError:
        return None
    except socket.timeout:
        return None
    except urllib2.URLError:
        return None

    packages = chimitheque_repository_response.read()
    package_list = packages.split('|')

    mylogger.debug(message='packages:%s' % packages)

    date_list = []
    for package in package_list:
        date_search = re.search('_(.*)-([0-9]{8})', package)
        if date_search is not None:
            date_list.append((date_search.group(1), date_search.group(2)))

    last_date = max(date_list) if len(date_list) > 0 else None

    if return_string:
        return '%s-%s' % (last_date[0], last_date[1])
    else:
        return last_date


def is_new_app_version():
    """Check if there is an available Chimithèque update.
    """
    lastest_version_date = get_lastest_app_version()
    current_version_date=settings['release_date']

    mylogger.debug(message='lastest_version_date:%s' % str(lastest_version_date))

    if lastest_version_date is None:
        return False
    elif lastest_version_date[1] > current_version_date:
        return "%s-%s" % (lastest_version_date[0], lastest_version_date[1])


def clean_session():
    current.db(current.db.web2py_session_chimitheque).delete()



def has_list_dups(l):
    """Check if the list l has duplicate entries.
    """
    for i in count_list_dups(l):
        if i[1] != 1:
            return True
    return False


def count_list_dups(l):
    """Count duplicates in the list l.
    """
    tally = defaultdict(int)
    for x in l:
        tally[x] += 1
    return tally.items()


def linear_to_empirical_formula(formula):
    """Convert the given formula into the empirical formula
    """
    return l2ef(ctypes.c_char_p(formula))


def is_empirical_formula(formula):
    """Check if the given formula is an empirical formula.
    """
    return sort_empirical_formula(formula)[1] is None


def sort_empirical_formula(formula):
    """Sort atoms of the given formula.
    """
    # removing spaces
    formula = formula.replace(' ', '')

    # if the formula is like abc.def.ghi, spliting it
    split_formula = formula.split(".")
    if len(split_formula) > 1:
        formula = split_formula[0]

    new_formula = ''
    # sorting each part
    for formula_part in split_formula[1:]:
        # sorting the formula part
        sorted_formula_part, error_code = sort_simple_formula(formula_part, method='simple')
        # an error occur when the formula part has a wrong syntax
        if error_code:
            return (None, error_code)
        else:
            new_formula += '.' + sorted_formula_part

    sorted_formula, error_code = sort_simple_formula(formula)
    # an error occur when the formula part has a wrong syntax
    if error_code:
        return (None, error_code)
    new_formula = sorted_formula + new_formula

    # no error
    mylogger.debug(message='new_formula:%s' % new_formula)
    return (new_formula, None)


def sort_simple_formula(formula, method=None):
    has_c_atom = False
    has_h_atom = False
    has_other_atom = False
    has_upper_lower_atom = False

    upper_lower_atoms = []
    other_atoms = []
    last_part = ''

    mylogger.debug(message='formula:%s' % formula)

    # removing spaces
    formula = formula.replace(' ', '')

    # checking the allowed characters
    m = re.match("[A-Za-z0-9,\^]+", formula)
    if not m:
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_MAIN_SYNTAX"))

    # for the simple method we do nothing else - TO BE IMPROVED
    if method == 'simple':
        return (formula, None)

    # sometimes the formula is like C12H22O11.H2O.C12
    # dealing only with the part before the first dot
    # last_part = formula.split('.')
    # if len(last_part) > 1:
    #    last_part = formula.split('.')[1]
    #    formula = formula.replace(last_part, '')
    #    formula = formula.replace('.', '')

    # search atoms with and uppercase followed by lowercase letters like Na or Cl
    # return a list of tuples like:
    # [('Cl', 'Cl'), ('Na', 'Na'), ('Cl3', 'Cl')]
    # for ClNaHCl3
    # the second member of the tupple is used to detect duplicated atoms
    _upper_lower_atoms = re.findall("((?:\^[0-9]+)?([A-Z][a-wy-z]{1,3})[0-9,]*)", formula)
    upper_lower_atoms = [a[0] for a in _upper_lower_atoms]
    mylogger.debug(message='_upper_lower_atoms:%s' % _upper_lower_atoms)
    mylogger.debug(message='upper_lower_atoms:%s' % upper_lower_atoms)

    # detecting wrong atoms
    for a in _upper_lower_atoms:
        if a[1] not in settings['atom_array'].keys():
            return (None, get_string("EMPIRICAL_FORMULA_ERROR_WRONG_ATOMS"))

    # detecting duplicated atoms
    if has_list_dups([a[1] for a in _upper_lower_atoms]):
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_DUPLICATED_ULATOMS"))

    if upper_lower_atoms and len(upper_lower_atoms) != 0:
        has_upper_lower_atom = True
        # removing the atoms from the formula
        for atom in upper_lower_atoms:
            formula = formula.replace(atom, '')

    mylogger.debug(message='formula:%s' % formula)
    # here we should have only one uppercase letter (and digits) per atom for the rest of
    # the formula

    # searching the C atom
    _c_atom = re.findall("((?:\^[0-9]+)?(C)[0-9,]*)", formula)
    # will return [('C2', 'C'), ('C', 'C')] for C2HC
    # if there are more than 1 C: syntax error
    if _c_atom and len(_c_atom) > 1:
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_DUPLICATED_CATOMS"))
    elif _c_atom:
        atomc = _c_atom[0][0]
        formula = formula.replace(atomc, '')
        has_c_atom = True
    mylogger.debug(message='formula:%s' % formula)

    # searching the H atom
    _h_atom = re.findall("((?:\^[0-9]+)?(H)[0-9,]*)", formula)
    # will return [('H2', 'H'), ('H', 'H')] for H2CH
    # if there are more than 1 H: syntax error
    if _h_atom and len(_h_atom) > 1:
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_DUPLICATED_HATOMS"))
    elif _h_atom:
        atomh = _h_atom[0][0]
        formula = formula.replace(atomh, '')
        has_h_atom = True
    mylogger.debug(message='formula:%s' % formula)

    # search the other atoms
    _other_atoms = re.findall("(?:\^[0-9]+)?(([A-Z])[0-9,]*)", formula)
    other_atoms = [a[0] for a in _other_atoms]
    mylogger.debug(message='other_atoms:%s' % other_atoms)

    # detecting wrong atoms
    for a in _other_atoms:
        if a[1] not in settings['atom_array'].keys():
            return (None, get_string("EMPIRICAL_FORMULA_ERROR_WRONG_ATOMS"))

    # detecting duplicated atoms
    if has_list_dups([a[1] for a in _other_atoms]):
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_DUPLICATED_OTHERATOMS"))

    if other_atoms and len(other_atoms) != 0:
        has_other_atom = True
        # removing the atoms from the formula
        for atom in other_atoms:
            formula = formula.replace(atom, '')

    mylogger.debug(message='formula:%s' % formula)
    mylogger.debug(message='len(formula):%s' % len(formula))
    # if formula is not emty, this is an error
    # except for the simple test where formula can still contain thinks
    if len(formula) != 0:
        return (None, get_string("EMPIRICAL_FORMULA_ERROR_LOWERCASE_ATOMS"))

    # rebuilding the formula
    new_formula = ''
    if has_c_atom:
        new_formula += atomc
    if has_h_atom:
        new_formula += atomh
    if has_other_atom or has_upper_lower_atom:
        for atom in sorted(other_atoms + upper_lower_atoms):
            new_formula += atom

    if len(last_part) != 0:
        new_formula += '.%s' % last_part

    return (new_formula, None)


def or_ify(query_list):
    """Return a gluon.dal.Query object that is a OR of each query_list element.

    query_list -- a list of gluon.dal.Query
    """
    list_len = len(query_list) if type(query_list) is ListType else 1
    mylogger.debug(message='list_len:%s-list_len/2:%s' % (list_len, list_len/2))
    if list_len == 1:
        mylogger.debug(message='==1-query_list:%s' % query_list)
        return query_list[0] if type(query_list) is ListType else query_list
    elif list_len == 2:
        mylogger.debug(message='==2-query_list:%s' % query_list)
        return or_ify(query_list[0]).__or__(or_ify(query_list[1]))
    else:
        mylogger.debug(message='==3+query_list:%s' % query_list)
        mylogger.debug(message='query_list[0:(list_len/2)+1]:%s' % query_list[0:(list_len/2)+1])
        mylogger.debug(message='query_list[(list_len/2)+1:]:%s' % query_list[(list_len/2)+1:])
        return or_ify(query_list[0:(list_len/2)+1]).__or__(or_ify(query_list[(list_len/2)+1:]))


def pretty_link(link):
    """Return a short version of the link.

    example: http://foo.bar.com... if the link is http://foo.bar.com/a/b/c/d?a=1,b=2
    """
    _pretty_link = re.search('(http(s)?://[^/]*)/.*', link)

    return '%s...' % _pretty_link.group(1) if _pretty_link is not None else link


def get_admins():
    """
    Returns users with the 'admin' permission
    """
    rows = current.db((current.auth.settings.table_permission.name == 'admin') &
                      (current.auth.settings.table_membership.group_id == current.auth.settings.table_permission.group_id) &
                      (current.auth.settings.table_user.id == current.auth.settings.table_membership.user_id)).select(current.auth.settings.table_user.ALL)
    mylogger.debug(message='rows:%s' % rows)
    return rows


def get_connected_user():
    """
    Return the currently connected users
    """
    session_time = int(settings['session_time'])
    now_datetime = datetime.datetime.now()
    max_age_session_datetime = now_datetime - datetime.timedelta(seconds=60*session_time)
    active_session_datetime = now_datetime - datetime.timedelta(seconds=60*2)

    users = []
    users_email = []
    rows = current.db(current.db.web2py_session_chimitheque.modified_datetime >= max_age_session_datetime).select()
    mylogger.debug(message='len(rows):%s' % len(rows))

    active_unique_keys = [r.unique_key for r in current.db(current.db.web2py_session_chimitheque.modified_datetime >= active_session_datetime).select()]

    for row in rows:
        session_data = row.session_data
        pickle_data = cPickle.loads(session_data)
        auth_user_email = pickle_data['auth_user_email'] if 'auth_user_email' in pickle_data else None
        if auth_user_email and auth_user_email not in users_email:
            if row.unique_key not in active_unique_keys:
                active = get_string("PERSON_UNACTIVE")
            else:
                active = ''
            _user = current.db(current.db.person.email==auth_user_email).select(current.db.person.id).first()
            if _user is not None: # when you delete a connected user he can still remain in the session data
                user_id = _user.id
                users.append((user_id, auth_user_email, active))
                users_email.append(auth_user_email)

    mylogger.debug(message='users:%s' %users)
    return users


def get_store_location_submenu(store_location_id):
    """
    Return a hierarchical menu for the given store location id
    """
    from c_store_location_mapper import STORE_LOCATION_MAPPER

    _sl = current.db(current.db.store_location.id==store_location_id).select().first()

    _store_location_children_rows = current.db(current.db.store_location.parent==store_location_id).select()
    _ret = []

    for _store_location_row in _store_location_children_rows:
        if (STORE_LOCATION_MAPPER().get_nb_children(store_location_id = _store_location_row['id'])) == 0 or (_store_location_row == 0):
            _ret.append(
                        (_store_location_row['label'],
                        False,
                        URL(current.request.application,'product','search',
                        vars={'request': 'store_location',
                              'is_in_store_location': _store_location_row['id'],
                              'not_archive': 'True'}),
                        []
                        )
                        )
        else:
            _ret.append(
                        (_store_location_row['label'],
                        False,
                        URL(current.request.application,'product','search',
                        vars={'request': 'STORE_LOCATION',
                              'is_in_store_location': _store_location_row['id'],
                              'not_archive': 'True'}),
                        get_store_location_submenu(_store_location_row['id'])
                        )
                        )
    return _ret


def get_child_message(message_id, depth):

    child_messages = current.db(current.db.message.parent==message_id).select(orderby=current.db.message.id)

    return [ [depth + 1, child_message.id, get_child_message(child_message.id, depth + 1)] for child_message in child_messages ]


def get_message_hierarchy():

    root_messages_pin = current.db((current.db.message.parent==None) & 
                               (current.db.message.pin==True) & 
                               (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.creation_datetime)
    root_messages_not_pin = current.db((current.db.message.parent==None) & 
                               (current.db.message.pin==False) &
                               (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.creation_datetime)

    message_pin_id_hierarchy = flatten([[0, message.id, get_child_message(message.id, 0)] for message in root_messages_pin ])
    message_not_pin_id_hierarchy = flatten([[0, message.id, get_child_message(message.id, 0)] for message in root_messages_not_pin ])

    message_hierarchy = []
    for depth, message_id in chunks(message_pin_id_hierarchy + message_not_pin_id_hierarchy, 2):
        message_hierarchy.append((depth, current.db(current.db.message.id==message_id).select().first()))

    return message_hierarchy


def get_pin_message():

    messages = current.db((current.db.message.pin==True) & (current.db.message.expiration_datetime >= datetime.datetime.now())).select(orderby=current.db.message.id)

    return messages


def get_store_location_parents(store_location_id):
    """
    Return the parents of the given store location id
    """
    mylogger.debug(message='get_store_location_parents')
    _sl = current.db(current.db.store_location.id == store_location_id).select().first()
    mylogger.debug(message='_sl:%s' % _sl)
    _parent = _sl.parent
    mylogger.debug(message='_parent:%s' % _parent)
    if _parent is None:
        return [_sl]
    else:
        return [_sl] + get_store_location_parents(_parent.id)


def get_store_location_label_full_path(r):

    mylogger.debug(message='r:%s' % str(r))

    if r is not None:
        mylogger.debug(message='r.parent:%s' % str(r.parent))
        
        if r.parent is None:
            mylogger.debug(message='r.label:%s' % str(r.label))
            return r.label
        else:
            return ' / '.join(_parent.label for _parent in reversed(get_store_location_parents(r.parent))) + ' / %s' % r.label
    else:
        mylogger.debug(message='get_store_location_label_full_path has returned None')
        return None


def clear_menu_cache():
    current.cache.ram.clear(regex='menu_.*')


def compute_stock_total(product, store_location):
    """Return the stock total of the given product in the store location
    and its sub store locations.
    
    A product can be stored several times in different units.
    
    product -- a PRODUCT instance
    return: a dictionary { unit: volume_weight } with
            unit -- the reference unit id
            volume_weight -- the volume or weight
    """
    _stock = {}
    _stock_current = compute_stock_current(product, store_location)
    
    for _child in store_location.retrieve_children():
        _child_stock_current = compute_stock_current(product, _child)
    
        for _reference in _child_stock_current.keys():
            if _reference in _stock.keys():
                _stock[_reference] = _stock[_reference]  + _child_stock_current[_reference]
            else:
                _stock[_reference] = _child_stock_current[_reference]
    
    # adding the stock_current
    for _reference in _stock_current.keys():
        if _reference in _stock.keys():
            _stock[_reference] = _stock[_reference]  + _stock_current[_reference]
        else:
            _stock[_reference] = _stock_current[_reference]
    
    return _stock

def compute_stock_current(product, store_location):
    """Return the stock of the product in the given store location.
    
    A product can be stored several times in different units.
    
    store_location -- a STORE_LOCATION instance
    return: a dictionary { unit: volume_weight } with
            unit -- the reference unit id
            volume_weight -- the volume or weight
    """
    _stock = {}
    
    for _storage in STORAGE_MAPPER().find(store_location_id=store_location.id, product_id=product.id):
    
        mylogger.debug(message='_storage:%s' % _storage)
    
        # using the number 99 (random choice) as a dictionary key if the storage has no unit
        _reference = _storage.unit.reference.id if _storage.unit is not None else 99
        _multiplier = _storage.unit.multiplier_for_reference if _storage.unit is not None else 1
        _volume_weight = _storage.volume_weight if _storage.volume_weight is not None else 1
    
        if _reference in _stock.keys():
            _stock[_reference] = _stock[_reference] + (_volume_weight * _multiplier)
        else:
            _stock[_reference] = _volume_weight * _multiplier
    
    return _stock

#
# startup tasks
#
def startup_clean_product_missing_references():
    
    _products = current.db(current.db.product.id>0).select()
    _number_of_products = len(_products)
    mylogger.info(message='total products:%s' % _number_of_products)
    
    _counter = 1
    for _product in _products:
    
        broken_reference = False
        mylogger.info(message='processing product %s/%s' % (_counter, _number_of_products))
        for table in ['physical_state',
                      'class_of_compounds',
                      'hazard_code',
                      'symbol',
                      'signal_word',
                      'risk_phrase',
                      'safety_phrase',
                      'hazard_statement',
                      'precautionary_statement']:
            
            mylogger.debug(message='table:%s' % table)
            
            _reference_value=_product[table]
                        
            if not type(_reference_value) is ListType:
                if _reference_value is not None:
                    _count = current.db(current.db[table]['id']==_reference_value).count()
                    mylogger.debug(message='table:%s _reference_value:%s _count:%s' % (table, _reference_value, _count))
                    if _count == 0:
                        broken_reference = True
                        del _product[table]
            else:
                for _ref in _reference_value:
                    if _ref is not None:
                        _count = current.db(current.db[table]['id']==_ref).count()
                        mylogger.debug(message='table:%s _ref:%s _count:%s' % (table, _ref, _count))
                        if _count == 0:
                            broken_reference = True
                            _product[table].remove(_ref)
                        
        if broken_reference:
            mylogger.info(message='product id=%s cas_number=%s had broken references' % (_product.id, _product.cas_number))
        
        _product.update_record()
        _counter = _counter + 1

    mylogger.info(message='finished')
    current.db.commit()


def _startup_fix_wrong_empirical_formula():
    formulas = current.db(current.db.empirical_formula).select()
    nb_errors = 0
    nb_fixed_formula = 0
    for formula in formulas:
        fixed_formula_label, error = sort_empirical_formula(formula.label)
        if error:
            nb_errors += 1
            mylogger.debug(message='formula error:%s' %formula.label)
            # we have to update products that have "formula" empirical formula
            products_to_update = current.db(current.db.product.empirical_formula == formula.id).select()
            for product in products_to_update:
                product.update_record(empirical_formula=0)
            # then removing the wrong empirical formula
            current.db(current.db.empirical_formula.label==formula.label).delete()

        elif formula.label != fixed_formula_label:
            # before updating, checking that the fixed_formula_label does not exist yet
            row = current.db(current.db.empirical_formula.label == fixed_formula_label).select().first()
            if row:
                # we have to update products that have "formula" empirical formula
                products_to_update = current.db(current.db.product.empirical_formula == formula.id).select()
                for product in products_to_update:
                    product.update_record(empirical_formula=row.id)
                # then removing the wrong empirical formula
                current.db(current.db.empirical_formula.label==formula.label).delete()
            else:
                # updating the formula
                nb_fixed_formula += 1
                mylogger.debug(message='formula fixed:%s' %formula.label)
                current.db(current.db.empirical_formula.label==formula.label).select().first().update_record(label=fixed_formula_label)
    current.db.commit()


def _startup_update_product_name_computed_field():
    rows = current.db(current.db.name).select()
    _count = 0
    for row in rows:
        _count += 1
        row.update_record(label = row.label)


def _update_user_permission(permission, user_id):

    if permission in settings['permission_dependencies'].keys():
        mylogger.debug(message='permission %s has dependencies' % permission)

        for _permission in settings['permission_dependencies'][permission]:

            if not current.auth.has_permission(_permission, user_id=user_id):
                mylogger.debug(message='adding permission %s for user %s' % (_permission, user_id))
                _user_group = current.auth.user_group(user_id=user_id)
                current.auth.add_permission(_user_group, name=_permission)
                _update_user_permission(_permission, user_id)

        current.db.commit()


def startup_update_stock_store_locations():

    mylogger.debug(message='startup_update_STOCK_store_locations()')

    from c_storage_mapper import STORAGE_MAPPER
    from c_stock_store_location_mapper import STOCK_STORE_LOCATION_MAPPER
    storage_mapper = STORAGE_MAPPER()
    stock_store_location_mapper = STOCK_STORE_LOCATION_MAPPER()

    # cleaning the table
    current.db(current.db.stock_store_location).delete()

    _storages = storage_mapper.find()
    for _storage in _storages:
        mylogger.debug('_storage:%s' % _storage)

        _storage_unit_reference = _storage.unit.reference \
                                  if _storage.unit is not None \
                                  else None
        _storage_unit_reference_id = _storage.unit.reference.id \
                                  if _storage.unit is not None \
                                  else None

        if stock_store_location_mapper.exists(store_location_id=_storage.store_location.id,
                                              product_id=_storage.product.id,
                                              unit_reference_id=_storage_unit_reference_id,
                                              no_unit_reference=_storage_unit_reference_id is None):

            _stock = stock_store_location_mapper.find(store_location_id=_storage.store_location.id,
                                                      product_id=_storage.product.id,
                                                      unit_reference_id=_storage_unit_reference_id,
                                                      no_unit_reference=_storage_unit_reference_id is None)[0]
            mylogger.debug('_stock:%s' % _stock)
            _stock.update_stock_total(_storage)

            stock_store_location_mapper.update(_stock)
        else:
            _stock = stock_store_location_mapper.new_for_store_location_and_product_and_unit(store_location_id=_storage.store_location.id,
                                                                                             product_id=_storage.product.id,
                                                                                             unit_reference_id=_storage_unit_reference_id)
            mylogger.debug('_stock:%s' % _stock)
            _stock.update_stock_total(_storage)

            stock_store_location_mapper.save(_stock)

        if _storage.store_location.has_parent():

            for _store_location in _storage.store_location.retrieve_parents():

                if _store_location is not None:

                    if stock_store_location_mapper.exists(store_location_id=_storage.store_location.id,
                                                          product_id=_storage.product.id,
                                                          unit_reference_id=_storage_unit_reference.id if _storage_unit_reference is not None else None,
                                                          no_unit_reference=_storage_unit_reference is None):

                        _stock = stock_store_location_mapper.find(store_location_id=_storage.store_location.id,
                                                                  product_id=_storage.product.id,
                                                                  unit_reference_id=_storage_unit_reference.id if _storage_unit_reference is not None else None,
                                                                  no_unit_reference=_storage_unit_reference is None)[0]
                        mylogger.debug('_stock:%s' % _stock)
                        _stock.update_stock_total(_storage)

                        stock_store_location_mapper.update(_stock)
                    else:
                        _stock = stock_store_location_mapper.new_for_store_location_and_product_and_unit(_store_location.id,
                                                                                                         _storage.product.id,
                                                                                                         _storage_unit_reference_id)
                        mylogger.debug('_stock:%s' % _stock)
                        _stock.update_stock_total(_storage)

                        stock_store_location_mapper.save(_stock)

def startup_update_user_permissions():
    #
    # update users permissions at application startup
    #    
    is_user_permission_updated = current.cache.disk('is_user_permission_updated', lambda: False, time_expire = None)
    if is_user_permission_updated:
        return True

    mylogger.debug(message='update_user_permissions()')

    for _PERSON in current.db(current.db.person).select():
        mylogger.debug(message='_PERSON:%s' % _PERSON)

        # setting dependent permissions
        for _permission in settings['permission_dependencies'].keys():
            if current.auth.has_permission(_permission, user_id=_PERSON.id):
                mylogger.debug(message='user %s has permission %s' % (_PERSON.email, _permission))
                _update_user_permission(_permission, user_id=_PERSON.id)

        # setting default permissions
        for _permission in settings['disabled_permissions'].keys():
            if settings['disabled_permissions'][_permission] and not current.auth.has_permission(_permission, user_id=_PERSON.id):
                mylogger.debug(message='adding default permission %s for user %s' % (_permission, _PERSON.id))
                _user_group = current.auth.user_group(user_id=_PERSON.id)
                current.auth.add_permission(_user_group, name=_permission)

        current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_user_permission_updated', None)
    current.cache.disk('is_user_permission_updated', lambda: True, time_expire = None)

def startup_update_entity():

    is_entity_updated = current.cache.disk('is_entity_updated', lambda: False, time_expire = None)
    if is_entity_updated:
        return True

    mylogger.debug(message='startup_update_entity()')

    mylogger.debug(message='renaming admin_entity into all_entity')

    _row = current.db(current.db.entity.role=='admin_entity').select().first()
    if _row:
        _row.update_record(role='all_entity')

def startup_update_storage():

    is_storage_updated = current.cache.disk('is_storage_updated', lambda: False, time_expire = None)
    if is_storage_updated:
        return True

    mylogger.debug(message='startup_update_storage()')

    current.db(current.db.storage.volume_weight==None).update(unit=None)

    current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_storage_updated', None)
    current.cache.disk('is_storage_updated', lambda: True, time_expire = None)

def startup_update_unit():

    is_unit_updated = current.cache.disk('is_unit_updated', lambda: False, time_expire = None)
    if is_unit_updated:
        return True

    mylogger.debug(message='startup_update_unit()')

    current.db(current.db.unit.label=='item').delete()

    current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_unit_updated', None)
    current.cache.disk('is_unit_updated', lambda: True, time_expire = None)

def startup_update_product_class_of_compounds():

    is_product_class_of_compounds_updated = current.cache.disk('is_product_class_of_compounds_updated', lambda: False, time_expire = None)
    if is_product_class_of_compounds_updated:
        return True

    mylogger.debug(message='startup_update_product_class_of_compounds()')

    current.db(current.db.product.class_of_compounds==None).update(class_of_compounds='')
    current.db(current.db.product_history.class_of_compounds==None).update(class_of_compounds='')

    current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_product_class_of_compounds_updated', None)
    current.cache.disk('is_product_class_of_compounds_updated', lambda: True, time_expire = None)

def startup_update_product_empirical_formula():

    is_product_empirical_formula_updated = current.cache.disk('is_product_empirical_formula_updated', lambda: False, time_expire = None)
    if is_product_empirical_formula_updated:
        return True

    mylogger.debug(message='startup_update_product_empirical_formula()')

    current.db(current.db.product.empirical_formula==0).update(empirical_formula=None)

    current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_product_empirical_formula_updated', None)
    current.cache.disk('is_product_empirical_formula_updated', lambda: True, time_expire = None)

def startup_update_store_location():
    #
    # update store locations at application startup
    # 
    is_store_location_updated = current.cache.disk('is_store_location_updated',
                                                   lambda: False,
                                                   time_expire=None)
    if is_store_location_updated:
        return True

    mylogger.debug(message='startup_update_store_location()')

#    # inserting root store location and entity if needed
#    # they were included in the populate_database funtion at the revision 91
#    # so databases created before this version do not include them
#    if current.db(current.db.entity.role == 'root_entity').count() == 0:
#        _id_root_entity = current.db.entity.insert(role='root_entity', description='root_entity', manager=None)
#    else:
#        _id_root_entity = current.db(current.db.entity.role == 'root_entity').select().first().id
#    mylogger.debug(message='_id_root_entity:%s' % _id_root_entity)
#
#    if current.db(current.db.store_location.label == 'root_store_location').count() == 0:
#        _id_root_store_location = current.db.store_location.insert(label='root_store_location', entity=_id_root_entity)
#    else:
#        _id_root_store_location = current.db(current.db.store_location.label == 'root_store_location').select().first().id
#
#    current.db(current.db.store_location.parent==None).update(parent=_id_root_store_location)
#    current.db(current.db.store_location.can_store==None).update(can_store=True)
#    
#    rows = current.db(current.db.store_location).select()
#    for row in rows:
#        row.update_record(label_full_path=get_store_location_label_full_path(row))

    # is there a root_store_location
    if not current.db(current.db.store_location.label == 'root_store_location').count() == 0:

        # yes, then retrieving its id
        _id_root_store_location = current.db(current.db.store_location.label == 'root_store_location').select().first().id
        # updating store locations parent references
        current.db(current.db.store_location.parent == _id_root_store_location).update(parent=None)

        # finally deleting the root_store_location
        current.db(current.db.store_location.id == _id_root_store_location).delete()

    current.db(current.db.store_location.can_store==None).update(can_store=True)
    
    current.db.commit()

    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_store_location_updated', None)
    current.cache.disk('is_store_location_updated', lambda: True, time_expire = None)

def startup_update_cmr():
    #
    # update cmr categories at application startup
    #    
    is_cmr_updated = current.cache.disk('is_cmr_updated', lambda: False, time_expire = None)
    if is_cmr_updated:
        return True
    
    mylogger.debug(message='startup_update_cmr()')
    
    _products = current.db(current.db.product).select()
    for _product in _products:
        current.db(current.db.product.id==_product.id).update(cas_number=_product.cas_number)

    current.db.commit()
    
    # we need to clear the cache key before reinitializing it
    current.cache.disk('is_cmr_updated', None)
    current.cache.disk('is_cmr_updated', lambda: True, time_expire = None)


def startup_populate_database():
    #
    # populate database if needed
    #
    #is_db_empty = current.cache.ram('is_db_empty', lambda: current.db(current.db.empirical_formula.id >= 0).count() == 0, time_expire = None)
    #if not is_db_empty:
    #    return True

    mylogger.debug(message='startup_populate_database()')
    try:
        for table in current.db.tables:
            current.db.executesql("SELECT nextval('%s_id_seq')" %table);
    except Exception as ex:
        mylogger.debug(message='exception:%s' %type(ex))
        pass

    if current.db(current.db.cpe.id > 0).count() == 0:
        mylogger.debug(message='-populating cpe')
        current.db.cpe.insert(label=u'extraction arm'.encode('utf8'))
        current.db.cpe.insert(label=u'chemical fume hood'.encode('utf8'))
        current.db.cpe.insert(label=u'laboratorie fume hood'.encode('utf8'))

    if current.db(current.db.ppe.id > 0).count() == 0:
        mylogger.debug(message='-populating ppe')
        current.db.ppe.insert(label=u'lab coat'.encode('utf8'))
        current.db.ppe.insert(label=u'latex gloves'.encode('utf8'))
        current.db.ppe.insert(label=u'nitrile gloves'.encode('utf8'))
        current.db.ppe.insert(label=u'neoprene gloves'.encode('utf8'))
        current.db.ppe.insert(label=u'safety glasses'.encode('utf8'))
        current.db.ppe.insert(label=u'gaz mask'.encode('utf8'))

    if current.db(current.db.class_of_compounds.id > 0).count() == 0:
        mylogger.debug(message='-populating class_of_compounds')
        _id_sample_family = current.db.class_of_compounds.insert(label=u'sample_family'.encode('utf8'))

    if current.db(current.db.entity.id > 0).count() == 0:
        mylogger.debug(message='-populating entity')
        _id_root_entity = current.db.entity.insert(role='root_entity', description='root_entity', manager=None)
        _id_user_1_entity = current.db.entity.insert(role='user_1', description='Group uniquely assigned to user 1', manager=None)
        _id_all_entity_entity = current.db.entity.insert(role='all_entity', description='', manager=None)
        _id_sample_entity_entity = current.db.entity.insert(role='sample_entity', description='', manager=None)

    if current.db(current.db.store_location.id > 0).count() == 0:
        mylogger.debug(message='-populating store_location')
        current.db.store_location.insert(label=u'sample_store_location_A'.encode('utf8'), entity=_id_sample_entity_entity)
        current.db.store_location.insert(label=u'sample_store_location_B', entity=_id_sample_entity_entity)

    if current.db(current.db.person.id > 0).count() == 0:
        mylogger.debug(message='-populating person')
        _id_admin = current.db.person.insert(first_name='Admin', last_name='Admin', email='admin@admin.fr', password='0a80ce158486ab2a3ea52112023afd37d8dae11f27f01f4f66902e9bcfcd2bb7273fd28f34aa4e5eae8f1d2bc9c86ae7ed42d4f6f2d0ca570ddde46e55983a5d', creation_date='2010-12-21', archive='F', registration_key='', reset_password_key='', registration_id='')

    if current.db(current.db.membership.id > 0).count() == 0:
        mylogger.debug(message='-populating membership')
        current.db.membership.insert(user_id=_id_admin, group_id=_id_user_1_entity)
        current.db.membership.insert(user_id=_id_admin, group_id=_id_all_entity_entity)

    if current.db(current.db.permission.id > 0).count() == 0:
        mylogger.debug(message='-populating permission')
        current.db.permission.insert(group_id=_id_user_1_entity, name='admin', table_name='', record_id=0)

    if current.db(current.db.hazard_code.id > 0).count() == 0:
        mylogger.debug(message='-populating hazard_code')
        current.db.hazard_code.insert( label=u'E'.encode('utf8'))
        current.db.hazard_code.insert( label=u'F'.encode('utf8'))
        current.db.hazard_code.insert( label=u'F+'.encode('utf8'))
        current.db.hazard_code.insert( label=u'O'.encode('utf8'))
        current.db.hazard_code.insert( label=u'T'.encode('utf8'))
        current.db.hazard_code.insert( label=u'T+'.encode('utf8'))
        current.db.hazard_code.insert( label=u'Xi'.encode('utf8'))
        current.db.hazard_code.insert( label=u'Xn'.encode('utf8'))
        current.db.hazard_code.insert( label=u'C'.encode('utf8'))
        current.db.hazard_code.insert( label=u'N'.encode('utf8'))

    if current.db(current.db.hazard_statement.id > 0).count() == 0:
        mylogger.debug(message='-populating hazard_statement')
        current.db.hazard_statement.insert( label=u'.Unstable explosives.'.encode('utf8'), reference='H200');
        current.db.hazard_statement.insert( label=u'.Explosive; mass explosion hazard.'.encode('utf8'), reference='H201');
        current.db.hazard_statement.insert( label=u'.Explosive'.encode('utf8'), reference='H202');
        current.db.hazard_statement.insert( label=u'.Explosive; fire'.encode('utf8'), reference='H203');
        current.db.hazard_statement.insert( label=u'.Fire or projection hazard.'.encode('utf8'), reference='H204');
        current.db.hazard_statement.insert( label=u'.May mass explode in fire.'.encode('utf8'), reference='H205');
        current.db.hazard_statement.insert( label=u'.Extremely flammable gas.'.encode('utf8'), reference='H220');
        current.db.hazard_statement.insert( label=u'.Flammable gas.'.encode('utf8'), reference='H221');
        current.db.hazard_statement.insert( label=u'.Extremely flammable aerosol.'.encode('utf8'), reference='H222');
        current.db.hazard_statement.insert( label=u'.Flammable aerosol.'.encode('utf8'), reference='H223');
        current.db.hazard_statement.insert( label=u'.Extremely flammable liquid and vapour.'.encode('utf8'), reference='H224');
        current.db.hazard_statement.insert( label=u'.Highly flammable liquid and vapour.'.encode('utf8'), reference='H225');
        current.db.hazard_statement.insert( label=u'.Flammable liquid and vapour.'.encode('utf8'), reference='H226');
        current.db.hazard_statement.insert( label=u'.Flammable solid.'.encode('utf8'), reference='H228');
        current.db.hazard_statement.insert( label=u'.Heating may cause an explosion.'.encode('utf8'), reference='H240');
        current.db.hazard_statement.insert( label=u'.Heating may cause a fire or explosion.'.encode('utf8'), reference='H241');
        current.db.hazard_statement.insert( label=u'.Heating may cause a fire.'.encode('utf8'), reference='H242');
        current.db.hazard_statement.insert( label=u'.Catches fire spontaneously if exposed to air.'.encode('utf8'), reference='H250');
        current.db.hazard_statement.insert( label=u'.Self-heating: may catch fire.'.encode('utf8'), reference='H251');
        current.db.hazard_statement.insert( label=u'.Self-heating in large quantities; may catch fire.'.encode('utf8'), reference='H252');
        current.db.hazard_statement.insert( label=u'.In contact with water releases flammable gases which may ignite spontaneously.'.encode('utf8'), reference='H260');
        current.db.hazard_statement.insert( label=u'.In contact with water releases flammable gas.'.encode('utf8'), reference='H261');
        current.db.hazard_statement.insert( label=u'.May cause or intensify fire; oxidizer.'.encode('utf8'), reference='H270');
        current.db.hazard_statement.insert( label=u'.May cause fire or explosion; strong oxidizer.'.encode('utf8'), reference='H271');
        current.db.hazard_statement.insert( label=u'.May intensify fire; oxidizer.'.encode('utf8'), reference='H272');
        current.db.hazard_statement.insert( label=u'.Contains gas under pressure; may explode if heated.'.encode('utf8'), reference='H280');
        current.db.hazard_statement.insert( label=u'.Contains refrigerated gas; may cause cryogenic burns or injury.'.encode('utf8'), reference='H281');
        current.db.hazard_statement.insert( label=u'.May be corrosive to metals.'.encode('utf8'), reference='H290');
        current.db.hazard_statement.insert( label=u'.Fatal if swallowed.'.encode('utf8'), reference='H300');
        current.db.hazard_statement.insert( label=u'.Toxic if swallowed.'.encode('utf8'), reference='H301');
        current.db.hazard_statement.insert( label=u'.Harmful if swallowed.'.encode('utf8'), reference='H302');
        current.db.hazard_statement.insert( label=u'.May be fatal if swallowed and enters airways.'.encode('utf8'), reference='H304');
        current.db.hazard_statement.insert( label=u'.Fatal in contact with skin.'.encode('utf8'), reference='H310');
        current.db.hazard_statement.insert( label=u'.Toxic in contact with skin.'.encode('utf8'), reference='H311');
        current.db.hazard_statement.insert( label=u'.Harmful in contact with skin.'.encode('utf8'), reference='H312');
        current.db.hazard_statement.insert( label=u'.Causes severe skin burns and eye damage.'.encode('utf8'), reference='H314');
        current.db.hazard_statement.insert( label=u'.Causes skin irritation.'.encode('utf8'), reference='H315');
        current.db.hazard_statement.insert( label=u'.May cause an allergic skin reaction.'.encode('utf8'), reference='H317');
        current.db.hazard_statement.insert( label=u'.Causes serious eye damage.'.encode('utf8'), reference='H318');
        current.db.hazard_statement.insert( label=u'.Causes serious eye irritation.'.encode('utf8'), reference='H319');
        current.db.hazard_statement.insert( label=u'.Fatal if inhaled.'.encode('utf8'), reference='H330');
        current.db.hazard_statement.insert( label=u'.Toxic if inhaled.'.encode('utf8'), reference='H331');
        current.db.hazard_statement.insert( label=u'.Harmful if inhaled.'.encode('utf8'), reference='H332');
        current.db.hazard_statement.insert( label=u'.May cause allergy or asthma symptoms or breathing difficulties if inhaled.'.encode('utf8'), reference='H334');
        current.db.hazard_statement.insert( label=u'.May cause respiratory irritation.'.encode('utf8'), reference='H335');
        current.db.hazard_statement.insert( label=u'.May cause drowsiness or dizziness.'.encode('utf8'), reference='H336');
        current.db.hazard_statement.insert( label=u'.May cause genetic defects <state route of exposure if it is conclusively proven that no other routes of exposure cause the hazard>.'.encode('utf8'), reference='H340');
        current.db.hazard_statement.insert( label=u'.Suspected of causing genetic defects <state route of exposure if it is conclusively proven that no other routes of exposure cause the hazard>.'.encode('utf8'), reference='H341');
        current.db.hazard_statement.insert( label=u'.May cause cancer <state route of exposure if it is conclusively proven that no other routes of exposure cause the hazard>.'.encode('utf8'), reference='H350');
        current.db.hazard_statement.insert( label=u'.May cause cancer by inhalation.'.encode('utf8'), reference='H350i');
        current.db.hazard_statement.insert( label=u'.Suspected of causing cancer <state route of exposure if it is conclusively proven that no other routs of exposure cause the hazard>.'.encode('utf8'), reference='H351');
        current.db.hazard_statement.insert( label=u'.May damage fertility or the unborn child <state specific effect if known > <state route of exposure if it is conclusively proven that no other routes of exposure cause the hazard>.'.encode('utf8'), reference='H360');
        current.db.hazard_statement.insert( label=u'.May damage the unborn child.'.encode('utf8'), reference='H360D');
        current.db.hazard_statement.insert( label=u'.May damage the unborn child. Suspected of damaging fertility.'.encode('utf8'), reference='H360Df');
        current.db.hazard_statement.insert( label=u'.May damage fertility.'.encode('utf8'), reference='H360F');
        current.db.hazard_statement.insert( label=u'.May damage fertility. Suspected of damaging the unborn child.'.encode('utf8'), reference='H360Fd');
        current.db.hazard_statement.insert( label=u'.May damage fertility. May damage the unborn child.'.encode('utf8'), reference='H360FD2');
        current.db.hazard_statement.insert( label=u'.Suspected of damaging fertility or the unborn child <state specific effect if known> <state route of exposure if it is conclusively proven that no other routes of exposure cause the hazard>.'.encode('utf8'), reference='H361');
        current.db.hazard_statement.insert( label=u'.Suspected of damaging the unborn child.'.encode('utf8'), reference='H361d');
        current.db.hazard_statement.insert( label=u'.Suspected of damaging fertility.'.encode('utf8'), reference='H361f');
        current.db.hazard_statement.insert( label=u'.Suspected of damaging fertility. Suspected of damaging the unborn child.'.encode('utf8'), reference='H361fd');
        current.db.hazard_statement.insert( label=u'.May cause harm to breast-fed children.'.encode('utf8'), reference='H362');
        current.db.hazard_statement.insert( label=u'.Causes damage to organs <or state all organs affected'.encode('utf8'), reference='H370');
        current.db.hazard_statement.insert( label=u'.May cause damage to organs <or state all organs affected'.encode('utf8'), reference='H371');
        current.db.hazard_statement.insert( label=u'.Causes damage to organs <or state all organs affected'.encode('utf8'), reference='H372');
        current.db.hazard_statement.insert( label=u'.May cause damage to organs <or state all organs affected'.encode('utf8'), reference='H373');
        current.db.hazard_statement.insert( label=u'.Very toxic to aquatic life.'.encode('utf8'), reference='H400');
        current.db.hazard_statement.insert( label=u'.Very toxic to aquatic life with long lasting effects.'.encode('utf8'), reference='H410');
        current.db.hazard_statement.insert( label=u'.Toxic to aquatic life with long lasting effects.'.encode('utf8'), reference='H411');
        current.db.hazard_statement.insert( label=u'.Harmful to aquatic life with long lasting effects.'.encode('utf8'), reference='H412');
        current.db.hazard_statement.insert( label=u'.May cause long lasting harmful effects to aquatic life.'.encode('utf8'), reference='H413');
        current.db.hazard_statement.insert( label=u'.Explosive when dry'.encode('utf8'), reference='EUH001');
        current.db.hazard_statement.insert( label=u'.Explosive with or without contact with air.'.encode('utf8'), reference='EUH006');
        current.db.hazard_statement.insert( label=u'.Reacts violently with water.'.encode('utf8'), reference='EUH014');
        current.db.hazard_statement.insert( label=u'.In use may form flammable/explosive vapour-air mixture.'.encode('utf8'), reference='EUH018');
        current.db.hazard_statement.insert( label=u'.May form explosive peroxides.'.encode('utf8'), reference='EUH019');
        current.db.hazard_statement.insert( label=u'.Can become highly flammable in use.'.encode('utf8'), reference='EUH30');
        current.db.hazard_statement.insert( label=u'.Contact with water liberates toxic gas.'.encode('utf8'), reference='EUH029');
        current.db.hazard_statement.insert( label=u'.Contact with acids liberates toxic gas.'.encode('utf8'), reference='EUH031');
        current.db.hazard_statement.insert( label=u'.Contact with acids liberates very toxic gas.'.encode('utf8'), reference='EUH032');
        current.db.hazard_statement.insert( label=u'.Risk of explosion if heated under confinement.'.encode('utf8'), reference='EUH044');
        current.db.hazard_statement.insert( label=u'.Hazardous to the ozone layer.'.encode('utf8'), reference='EUH059');
        current.db.hazard_statement.insert( label=u'.Repeated exposure may cause skin dryness or cracking.'.encode('utf8'), reference='EUH066');
        current.db.hazard_statement.insert( label=u'.Toxic by eye contact'.encode('utf8'), reference='EUH070');
        current.db.hazard_statement.insert( label=u'.Corrosive to the respiratory tract.'.encode('utf8'), reference='EUH071');
        current.db.hazard_statement.insert( label=u'.Contains lead. Should not be used on surfaces liable to be chewed or sucked by children.Warning! Contains lead.'.encode('utf8'), reference='EUH201');
        current.db.hazard_statement.insert( label=u'.Warning! Contains lead.'.encode('utf8'), reference='EUH201A');
        current.db.hazard_statement.insert( label=u'.Cyanoacrylate. Danger. Bonds skin and eyes in seconds. Keep out of the reach of children.'.encode('utf8'), reference='EUH202');
        current.db.hazard_statement.insert( label=u'.Contains chromium (VI). May produce an allergic reaction.'.encode('utf8'), reference='EUH203');
        current.db.hazard_statement.insert( label=u'.Contains isocyanates. See information supplied by the manufacturer.'.encode('utf8'), reference='EUH204');
        current.db.hazard_statement.insert( label=u'.Contains epoxy constituents. See information supplied by the manufacturer.'.encode('utf8'), reference='EUH205');
        current.db.hazard_statement.insert( label=u'.Warning! Do not use together with other products. May release dangerous gases (chlorine).'.encode('utf8'), reference='EUH206');
        current.db.hazard_statement.insert( label=u'.Warning! Contains cadmium. Dangerous fumes are formed during use. See informationsupplied by the manufacturer. Comply with the safety instructions. Contains (name of sensitising substance). May produce an allergic reaction'.encode('utf8'), reference='EUH207');
        current.db.hazard_statement.insert( label=u'.Contains (name of sensitising substance). May produce an allergic reaction.'.encode('utf8'), reference='EUH208');
        current.db.hazard_statement.insert( label=u'.Can become highly flammable in use or can become flammable in use.'.encode('utf8'), reference='EUH209');
        current.db.hazard_statement.insert( label=u'.Can become flammable in use.'.encode('utf8'), reference='EUH209A');
        current.db.hazard_statement.insert( label=u'.Safety data sheet available on request'.encode('utf8'), reference='EUH210');
        current.db.hazard_statement.insert( label=u'.To avoid risks to human health and the environment'.encode('utf8'), reference='EUH401');

    if current.db(current.db.physical_state.id > 0).count() == 0:
        mylogger.debug(message='-populating physical_state')
        current.db.physical_state.insert( label=u'gaz'.encode('utf8'))
        current.db.physical_state.insert( label=u'liquid'.encode('utf8'))
        current.db.physical_state.insert( label=u'solid'.encode('utf8'))

    if current.db(current.db.precautionary_statement.id > 0).count() == 0:
        mylogger.debug(message='-populating precautionary_statement')
        current.db.precautionary_statement.insert( label=u'.If medical advice is needed'.encode('utf8'), reference='P101');
        current.db.precautionary_statement.insert( label=u'.Keep out of reach of children.'.encode('utf8'), reference='P102');
        current.db.precautionary_statement.insert( label=u'.Read label before use.'.encode('utf8'), reference='P103');
        current.db.precautionary_statement.insert( label=u'.Obtain special instructions before use.'.encode('utf8'), reference='P201');
        current.db.precautionary_statement.insert( label=u'.Do not handle until all safety precautions have been read and understood.'.encode('utf8'), reference='P202');
        current.db.precautionary_statement.insert( label=u'.Keep away from heat/sparks/open flames/hot surfaces. - No smoking.'.encode('utf8'), reference='P210');
        current.db.precautionary_statement.insert( label=u'.Do not spray on an open flame or other ignition source.'.encode('utf8'), reference='P211');
        current.db.precautionary_statement.insert( label=u'.Keep/Store away from clothing/.../combustible materials.'.encode('utf8'), reference='P220');
        current.db.precautionary_statement.insert( label=u'.Take any precaution to avoid mixing with combustibles...'.encode('utf8'), reference='P221');
        current.db.precautionary_statement.insert( label=u'.Do not allow contact with air.'.encode('utf8'), reference='P222');
        current.db.precautionary_statement.insert( label=u'.Keep away from any possible contact with water'.encode('utf8'), reference='P223');
        current.db.precautionary_statement.insert( label=u'.Keep wetted with...'.encode('utf8'), reference='P230');
        current.db.precautionary_statement.insert( label=u'.Handle under inert gas.'.encode('utf8'), reference='P231');
        current.db.precautionary_statement.insert( label=u'.Protect from moisture.'.encode('utf8'), reference='P232');
        current.db.precautionary_statement.insert( label=u'.Keep container tightly closed.'.encode('utf8'), reference='P233');
        current.db.precautionary_statement.insert( label=u'.Keep only in original container.'.encode('utf8'), reference='P234');
        current.db.precautionary_statement.insert( label=u'.Keep cool.'.encode('utf8'), reference='P235');
        current.db.precautionary_statement.insert( label=u'.Ground/bond container and receiving equipment.'.encode('utf8'), reference='P240');
        current.db.precautionary_statement.insert( label=u'.Use explosion-proof electrical/ventilating/lighting/.../ equipment.'.encode('utf8'), reference='P241');
        current.db.precautionary_statement.insert( label=u'.Use only non-sparking tools.'.encode('utf8'), reference='P242');
        current.db.precautionary_statement.insert( label=u'.Take precautionary measures against static discharge.'.encode('utf8'), reference='P243');
        current.db.precautionary_statement.insert( label=u'.Keep reduction valves free from grease and oil.'.encode('utf8'), reference='P244');
        current.db.precautionary_statement.insert( label=u'.Do not subject to grinding/shock/.../friction.'.encode('utf8'), reference='P250');
        current.db.precautionary_statement.insert( label=u'.Pressurized container: Do not pierce or burn'.encode('utf8'), reference='P251');
        current.db.precautionary_statement.insert( label=u'.Do not breathe dust/fume/gas/mist/vapours/spray.'.encode('utf8'), reference='P260');
        current.db.precautionary_statement.insert( label=u'.Avoid breathing dust/fume/gas/mist/vapours/spray.'.encode('utf8'), reference='P261');
        current.db.precautionary_statement.insert( label=u'.Do not get in eyes'.encode('utf8'), reference='P262');
        current.db.precautionary_statement.insert( label=u'.Avoid contact during pregnancy/while nursing.'.encode('utf8'), reference='P263');
        current.db.precautionary_statement.insert( label=u'.Wash ... thoroughly after handling.'.encode('utf8'), reference='P264');
        current.db.precautionary_statement.insert( label=u'.Do no eat'.encode('utf8'), reference='P270');
        current.db.precautionary_statement.insert( label=u'.Use only outdoors or in a well-ventilated area.'.encode('utf8'), reference='P271');
        current.db.precautionary_statement.insert( label=u'.Contaminated work clothing should not be allowed out of the workplace.'.encode('utf8'), reference='P272');
        current.db.precautionary_statement.insert( label=u'.Avoid release to the environment.'.encode('utf8'), reference='P273');
        current.db.precautionary_statement.insert( label=u'.Wear protective gloves/protective clothing/eye protection/face protection.'.encode('utf8'), reference='P280');
        current.db.precautionary_statement.insert( label=u'.Use PERSONal protective equipment as required.'.encode('utf8'), reference='P281');
        current.db.precautionary_statement.insert( label=u'.Wear cold insulating gloves/face shield/eye protection.'.encode('utf8'), reference='P282');
        current.db.precautionary_statement.insert( label=u'.Wear fire/flame resistant/retardant clothing.'.encode('utf8'), reference='P283');
        current.db.precautionary_statement.insert( label=u'.Wear respiratory protection.'.encode('utf8'), reference='P284');
        current.db.precautionary_statement.insert( label=u'.In case of inadequate ventilation wear respiratory protection.'.encode('utf8'), reference='P285');
        current.db.precautionary_statement.insert( label=u'.Handle under inert gas. Protect from moisture.'.encode('utf8'), reference='P231+P232');
        current.db.precautionary_statement.insert( label=u'.Keep cool. Protect from sunlight.'.encode('utf8'), reference='P235+P410');
        current.db.precautionary_statement.insert( label=u'.IF SWALLOWED:'.encode('utf8'), reference='P301');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN:'.encode('utf8'), reference='P302');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN:'.encode('utf8'), reference='P303');
        current.db.precautionary_statement.insert( label=u'.IF INHALED:'.encode('utf8'), reference='P304');
        current.db.precautionary_statement.insert( label=u'.IF IN EYES:'.encode('utf8'), reference='P305');
        current.db.precautionary_statement.insert( label=u'.IF ON CLOTHING:'.encode('utf8'), reference='P306');
        current.db.precautionary_statement.insert( label=u'.IF exposed:'.encode('utf8'), reference='P307');
        current.db.precautionary_statement.insert( label=u'.IF exposed or concerned:'.encode('utf8'), reference='P308');
        current.db.precautionary_statement.insert( label=u'.IF exposed or if you feel unwell:'.encode('utf8'), reference='P309');
        current.db.precautionary_statement.insert( label=u'.Immediately call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P310');
        current.db.precautionary_statement.insert( label=u'.Call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P311');
        current.db.precautionary_statement.insert( label=u'.Call a POISON CENTER or doctor/physician if you feel unwell.'.encode('utf8'), reference='P312');
        current.db.precautionary_statement.insert( label=u'.Get medical advice/attention.'.encode('utf8'), reference='P313');
        current.db.precautionary_statement.insert( label=u'.Get medical advice/attention if you feel unwell.'.encode('utf8'), reference='P314');
        current.db.precautionary_statement.insert( label=u'.Get immediate medical advice/attention.'.encode('utf8'), reference='P315');
        current.db.precautionary_statement.insert( label=u'.Specific treatment is urgent (see... on this label).'.encode('utf8'), reference='P320');
        current.db.precautionary_statement.insert( label=u'.Specific treatment (see ... on this label).'.encode('utf8'), reference='P321');
        current.db.precautionary_statement.insert( label=u'.Specific measures (see ... on this label).'.encode('utf8'), reference='P322');
        current.db.precautionary_statement.insert( label=u'.Rinse mouth.'.encode('utf8'), reference='P330');
        current.db.precautionary_statement.insert( label=u'.Do NOT induce vomiting.'.encode('utf8'), reference='P331');
        current.db.precautionary_statement.insert( label=u'.If skin irritation occurs:'.encode('utf8'), reference='P332');
        current.db.precautionary_statement.insert( label=u'.If skin irritation or rash occurs:'.encode('utf8'), reference='P333');
        current.db.precautionary_statement.insert( label=u'.Immerse in cool water/wrap in wet bandages.'.encode('utf8'), reference='P334');
        current.db.precautionary_statement.insert( label=u'.Brush off loose particles from skin.'.encode('utf8'), reference='P335');
        current.db.precautionary_statement.insert( label=u'.Thaw frosted parts with lukewarm water. Do no rub affected area.'.encode('utf8'), reference='P336');
        current.db.precautionary_statement.insert( label=u'.If eye irritation persists:'.encode('utf8'), reference='P337');
        current.db.precautionary_statement.insert( label=u'.Remove contact lenses'.encode('utf8'), reference='P338');
        current.db.precautionary_statement.insert( label=u'.Remove to fresh air and keep at rest in a position comfortable for breathing.'.encode('utf8'), reference='P340');
        current.db.precautionary_statement.insert( label=u'.If breathing is difficult'.encode('utf8'), reference='P341');
        current.db.precautionary_statement.insert( label=u'.If experiencing respiratory symptoms:'.encode('utf8'), reference='P342');
        current.db.precautionary_statement.insert( label=u'.Gently wash with plenty of soap and water.'.encode('utf8'), reference='P350');
        current.db.precautionary_statement.insert( label=u'.Rinse cautiously with water for several minutes.'.encode('utf8'), reference='P351');
        current.db.precautionary_statement.insert( label=u'.Wash with plenty of soap and water.'.encode('utf8'), reference='P352');
        current.db.precautionary_statement.insert( label=u'.Rinse skin with water/shower.'.encode('utf8'), reference='P353');
        current.db.precautionary_statement.insert( label=u'.Rinse immediately contaminated clothing and skin with plenty of water before removing clothes.'.encode('utf8'), reference='P360');
        current.db.precautionary_statement.insert( label=u'.Remove/Take off immediately all contaminated clothing.'.encode('utf8'), reference='P361');
        current.db.precautionary_statement.insert( label=u'.Take off contaminated clothing and wash before reuse.'.encode('utf8'), reference='P362');
        current.db.precautionary_statement.insert( label=u'.Wash contaminated clothing before reuse.'.encode('utf8'), reference='P363');
        current.db.precautionary_statement.insert( label=u'.In case of fire:'.encode('utf8'), reference='P370');
        current.db.precautionary_statement.insert( label=u'.In case of major fire and large quantities:'.encode('utf8'), reference='P371');
        current.db.precautionary_statement.insert( label=u'.Explosion risk in case of fire.'.encode('utf8'), reference='P372');
        current.db.precautionary_statement.insert( label=u'.DO NOT fight fire when fire reaches explosives.'.encode('utf8'), reference='P373');
        current.db.precautionary_statement.insert( label=u'.Fight fire with normal precautions from a reasonable distance'.encode('utf8'), reference='P374');
        current.db.precautionary_statement.insert( label=u'.Fight fire remotely due to the risk of explosion.'.encode('utf8'), reference='P375');
        current.db.precautionary_statement.insert( label=u'.Stop leak if safe to do so.'.encode('utf8'), reference='P376');
        current.db.precautionary_statement.insert( label=u'.Leaking gas fire - Do not extinguish'.encode('utf8'), reference='P377');
        current.db.precautionary_statement.insert( label=u'.Use... for extinction.'.encode('utf8'), reference='P378');
        current.db.precautionary_statement.insert( label=u'.Evacuate area.'.encode('utf8'), reference='P380');
        current.db.precautionary_statement.insert( label=u'.Eliminate all ignition sources if safe to do so.'.encode('utf8'), reference='P381');
        current.db.precautionary_statement.insert( label=u'.Absorb spillage to prevent material damage.'.encode('utf8'), reference='P390');
        current.db.precautionary_statement.insert( label=u'.Collect spillage.'.encode('utf8'), reference='P391');
        current.db.precautionary_statement.insert( label=u'.IF SWALLOWED: Immediately call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P301+P310');
        current.db.precautionary_statement.insert( label=u'.IF SWALLOWED: Call a POISON CENTER or doctor/physician if you feel unwell.'.encode('utf8'), reference='P301+P312');
        current.db.precautionary_statement.insert( label=u'.IF SWALLOWED: rinse mouth. Do NOT induce vomiting.'.encode('utf8'), reference='P301+P330+P331');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN: Immerse in cool water/wrap in wet bandages.'.encode('utf8'), reference='P302+P334');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN: Gently wash with plenty of soap and water.'.encode('utf8'), reference='P302+P350');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN: Wash with plenty of soap and water.'.encode('utf8'), reference='P302+P352');
        current.db.precautionary_statement.insert( label=u'.IF ON SKIN (or hair): Remove/Take off immediately all contaminated clothing. Rinse skin with water/shower.'.encode('utf8'), reference='P303+P361+P353');
        current.db.precautionary_statement.insert( label=u'.IF INHALED: Call a POISON CENTER or doctor/physician if you feel unwell.'.encode('utf8'), reference='P304+P312');
        current.db.precautionary_statement.insert( label=u'.IF INHALED: Remove to fresh air and keep at rest in a position comfortable for breathing.'.encode('utf8'), reference='P304+P340');
        current.db.precautionary_statement.insert( label=u'.IF INHALED: If breathing is difficult'.encode('utf8'), reference='P304+P341');
        current.db.precautionary_statement.insert( label=u'.IF IN EYES: Rinse cautiously with water for several minuts. Remove contact lenses'.encode('utf8'), reference='P305+P351+P338');
        current.db.precautionary_statement.insert( label=u'.IF ON CLOTHING: rinse immediately contaminated clothing and skin with plenty of water before removing clothes.'.encode('utf8'), reference='P306+P360');
        current.db.precautionary_statement.insert( label=u'.IF exposed: Call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P307+P311');
        current.db.precautionary_statement.insert( label=u'.IF exposed or concerned: Get medical advice/attention.'.encode('utf8'), reference='P308+P313');
        current.db.precautionary_statement.insert( label=u'.IF exposed or if you feel unwell: Call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P309+P311');
        current.db.precautionary_statement.insert( label=u'.If skin irritation occurs: Get medical advice/attention.'.encode('utf8'), reference='P332+P313');
        current.db.precautionary_statement.insert( label=u'.If skin irritation or rash occurs: Get medical advice/attention.'.encode('utf8'), reference='P333+P313');
        current.db.precautionary_statement.insert( label=u'.Brush off loose particles from skin. Immese in cool water/wrap in wet bandages.'.encode('utf8'), reference='P335+P334');
        current.db.precautionary_statement.insert( label=u'.If eye irritation persists: Get medical advice/attention.'.encode('utf8'), reference='P337+P313');
        current.db.precautionary_statement.insert( label=u'.If experiencing respiratory symptoms: Call a POISON CENTER or doctor/physician.'.encode('utf8'), reference='P342+P311');
        current.db.precautionary_statement.insert( label=u'.In case of fire: Stop leak if safe to do so.'.encode('utf8'), reference='P370+P376');
        current.db.precautionary_statement.insert( label=u'.In case of fire: Use... for extinction.'.encode('utf8'), reference='P370+P378');
        current.db.precautionary_statement.insert( label=u'.In case of fire: Evacuate area.'.encode('utf8'), reference='P370+P380');
        current.db.precautionary_statement.insert( label=u'.In case of fire: Evacuate area. Fight fire remotely due to the risk of explosion.'.encode('utf8'), reference='P370+P380+P375');
        current.db.precautionary_statement.insert( label=u'.In case of major fire and large quantities: Evacuate area. Fight fire remotely due to the risk of explosion.'.encode('utf8'), reference='P371+P380+P375');
        current.db.precautionary_statement.insert( label=u'.Store...'.encode('utf8'), reference='P401');
        current.db.precautionary_statement.insert( label=u'.Store in a dry place.'.encode('utf8'), reference='P402');
        current.db.precautionary_statement.insert( label=u'.Store in a well-ventilated place.'.encode('utf8'), reference='P403');
        current.db.precautionary_statement.insert( label=u'.Store in a closed container.'.encode('utf8'), reference='P404');
        current.db.precautionary_statement.insert( label=u'.Store locked up.'.encode('utf8'), reference='P405');
        current.db.precautionary_statement.insert( label=u'.Store in corrosive resistant/... container with a resistant inner liner.'.encode('utf8'), reference='P406');
        current.db.precautionary_statement.insert( label=u'.Maintain air gap between stacks/pallets.'.encode('utf8'), reference='P407');
        current.db.precautionary_statement.insert( label=u'.Protect from sunlight.'.encode('utf8'), reference='P410');
        current.db.precautionary_statement.insert( label=u'.Store at temperatures not exceeding...°C/...°F.'.encode('utf8'), reference='P411');
        current.db.precautionary_statement.insert( label=u'.Do not expose ot temperatures exceeding 50°C/ 122°F.'.encode('utf8'), reference='P412');
        current.db.precautionary_statement.insert( label=u'.Store bulk masses greater than ... kg/... lbs at temperatures not exceeding ...°C/...°F.'.encode('utf8'), reference='P413');
        current.db.precautionary_statement.insert( label=u'.Store aways from other materials.'.encode('utf8'), reference='P420');
        current.db.precautionary_statement.insert( label=u'.Store contents under ...'.encode('utf8'), reference='P422');
        current.db.precautionary_statement.insert( label=u'.Store in a dry place. Store in a closed container.'.encode('utf8'), reference='P402+P404');
        current.db.precautionary_statement.insert( label=u'.Store in a well-ventilated place. Keep container tightly closed.'.encode('utf8'), reference='P403+P233');
        current.db.precautionary_statement.insert( label=u'.Store in a well-ventilated place. Keep cool.'.encode('utf8'), reference='P403+P235');
        current.db.precautionary_statement.insert( label=u'.Protect from sunlight. Store in a well-ventilated place.'.encode('utf8'), reference='P410+P403');
        current.db.precautionary_statement.insert( label=u'.Protect from sunlight. Do no expose to temperatures exceeding 50°C/ 122°F.'.encode('utf8'), reference='P410+P412');
        current.db.precautionary_statement.insert( label=u'.Store at temperatures not exceeding...°C/...°F. Keep cool.'.encode('utf8'), reference='P411+P235');
        current.db.precautionary_statement.insert( label=u'.Dispose of contents/container to...'.encode('utf8'), reference='P501');

    if current.db(current.db.risk_phrase.id > 0).count() == 0:
        mylogger.debug(message='-populating risk_phrase')
        current.db.risk_phrase.insert( label=u'.Explosive when dry'.encode('utf8'), reference='1');
        current.db.risk_phrase.insert( label=u'.Risk of explosion by shock, friction, fire or other source of ignition'.encode('utf8'), reference='2');
        current.db.risk_phrase.insert( label=u'.Extreme risk of explosion by shock, friction, fire or other sources of ignition'.encode('utf8'), reference='3');
        current.db.risk_phrase.insert( label=u'.Forms very sensitive explosive metallic compounds'.encode('utf8'), reference='4');
        current.db.risk_phrase.insert( label=u'.Heating may cause an explosion'.encode('utf8'), reference='5');
        current.db.risk_phrase.insert( label=u'.Explosive with or without contact with air'.encode('utf8'), reference='6');
        current.db.risk_phrase.insert( label=u'.May cause fire'.encode('utf8'), reference='7');
        current.db.risk_phrase.insert( label=u'.Contact with combustible material may cause fire'.encode('utf8'), reference='8');
        current.db.risk_phrase.insert( label=u'.Explosive when mixed with combustible material'.encode('utf8'), reference='9');
        current.db.risk_phrase.insert( label=u'.Flammable'.encode('utf8'), reference='10');
        current.db.risk_phrase.insert( label=u'.Highly flammable'.encode('utf8'), reference='11');
        current.db.risk_phrase.insert( label=u'.Extremely flammable'.encode('utf8'), reference='12');
        current.db.risk_phrase.insert( label=u'.Reacts violently with water'.encode('utf8'), reference='14');
        current.db.risk_phrase.insert( label=u'.Contact with water liberates extremely flammable gases'.encode('utf8'), reference='15');
        current.db.risk_phrase.insert( label=u'.Explosive when mixed with oxidising substances'.encode('utf8'), reference='16');
        current.db.risk_phrase.insert( label=u'.Spontaneously flammable in air'.encode('utf8'), reference='17');
        current.db.risk_phrase.insert( label=u'.In use, may form flammable/explosive vapour-air mixture'.encode('utf8'), reference='18');
        current.db.risk_phrase.insert( label=u'.May form explosive peroxides'.encode('utf8'), reference='19');
        current.db.risk_phrase.insert( label=u'.Harmful by inhalation'.encode('utf8'), reference='20');
        current.db.risk_phrase.insert( label=u'.Harmful in contact with skin'.encode('utf8'), reference='21');
        current.db.risk_phrase.insert( label=u'.Harmful if swallowed'.encode('utf8'), reference='22');
        current.db.risk_phrase.insert( label=u'.Toxic by inhalation'.encode('utf8'), reference='23');
        current.db.risk_phrase.insert( label=u'.Toxic in contact with skin'.encode('utf8'), reference='24');
        current.db.risk_phrase.insert( label=u'.Toxic if swallowed'.encode('utf8'), reference='25');
        current.db.risk_phrase.insert( label=u'.Very toxic by inhalation'.encode('utf8'), reference='26');
        current.db.risk_phrase.insert( label=u'.Very toxic in contact with skin'.encode('utf8'), reference='27');
        current.db.risk_phrase.insert( label=u'.Very toxic if swallowed'.encode('utf8'), reference='28');
        current.db.risk_phrase.insert( label=u'.Contact with water liberates toxic gas'.encode('utf8'), reference='29');
        current.db.risk_phrase.insert( label=u'.Can become highly flammable in use'.encode('utf8'), reference='30');
        current.db.risk_phrase.insert( label=u'.Contact with acids liberates toxic gas'.encode('utf8'), reference='31');
        current.db.risk_phrase.insert( label=u'.Contact with acids liberates very toxic gas'.encode('utf8'), reference='32');
        current.db.risk_phrase.insert( label=u'.Danger of cumulative effects'.encode('utf8'), reference='33');
        current.db.risk_phrase.insert( label=u'.Causes burns'.encode('utf8'), reference='34');
        current.db.risk_phrase.insert( label=u'.Causes severe burns'.encode('utf8'), reference='35');
        current.db.risk_phrase.insert( label=u'.Irritating to eyes'.encode('utf8'), reference='36');
        current.db.risk_phrase.insert( label=u'.Irritating to respiratory system'.encode('utf8'), reference='37');
        current.db.risk_phrase.insert( label=u'.Irritating to skin'.encode('utf8'), reference='38');
        current.db.risk_phrase.insert( label=u'.Danger of very serious irreversible effects'.encode('utf8'), reference='39');
        current.db.risk_phrase.insert( label=u'.Limited evidence of a carcinogenic effect'.encode('utf8'), reference='40');
        current.db.risk_phrase.insert( label=u'.Risk of serious damage to eyes'.encode('utf8'), reference='41');
        current.db.risk_phrase.insert( label=u'.May cause sensitisation by inhalation'.encode('utf8'), reference='42');
        current.db.risk_phrase.insert( label=u'.May cause sensitisation by skin contact'.encode('utf8'), reference='43');
        current.db.risk_phrase.insert( label=u'.Risk of explosion if heated under confinement'.encode('utf8'), reference='44');
        current.db.risk_phrase.insert( label=u'.May cause cancer'.encode('utf8'), reference='45');
        current.db.risk_phrase.insert( label=u'.May cause heritable genetic damage'.encode('utf8'), reference='46');
        current.db.risk_phrase.insert( label=u'.Danger of serious damage to health by prolonged exposure'.encode('utf8'), reference='48');
        current.db.risk_phrase.insert( label=u'.May cause cancer by inhalation'.encode('utf8'), reference='49');
        current.db.risk_phrase.insert( label=u'.Very toxic to aquatic organisms'.encode('utf8'), reference='50');
        current.db.risk_phrase.insert( label=u'.Toxic to aquatic organisms'.encode('utf8'), reference='51');
        current.db.risk_phrase.insert( label=u'.Harmful to aquatic organisms'.encode('utf8'), reference='52');
        current.db.risk_phrase.insert( label=u'.May cause long-term adverse effects in the aquatic environment'.encode('utf8'), reference='53');
        current.db.risk_phrase.insert( label=u'.Toxic to flora'.encode('utf8'), reference='54');
        current.db.risk_phrase.insert( label=u'.Toxic to fauna'.encode('utf8'), reference='55');
        current.db.risk_phrase.insert( label=u'.Toxic to soil organisms'.encode('utf8'), reference='56');
        current.db.risk_phrase.insert( label=u'.Toxic to bees'.encode('utf8'), reference='57');
        current.db.risk_phrase.insert( label=u'.May cause long-term adverse effects in the environment'.encode('utf8'), reference='58');
        current.db.risk_phrase.insert( label=u'.Dangerous for the ozone layer'.encode('utf8'), reference='59');
        current.db.risk_phrase.insert( label=u'.May impair fertility'.encode('utf8'), reference='60');
        current.db.risk_phrase.insert( label=u'.May cause harm to the unborn child'.encode('utf8'), reference='61');
        current.db.risk_phrase.insert( label=u'.Possible risk of impaired fertility'.encode('utf8'), reference='62');
        current.db.risk_phrase.insert( label=u'.Possible risk of harm to the unborn child'.encode('utf8'), reference='63');
        current.db.risk_phrase.insert( label=u'.May cause harm to breast-fed babies'.encode('utf8'), reference='64');
        current.db.risk_phrase.insert( label=u'.Harmful: may cause lung damage if swallowed'.encode('utf8'), reference='65');
        current.db.risk_phrase.insert( label=u'.Repeated exposure may cause skin dryness or cracking'.encode('utf8'), reference='66');
        current.db.risk_phrase.insert( label=u'.Vapours may cause drowsiness and dizziness'.encode('utf8'), reference='67');
        current.db.risk_phrase.insert( label=u'.Possible risk of irreversible effects'.encode('utf8'), reference='68');
        current.db.risk_phrase.insert( label=u'.Reacts violently with water, liberating extremely flammable gases'.encode('utf8'), reference='14/15');
        current.db.risk_phrase.insert( label=u'.Contact with water liberates toxic, extremely flammable gases'.encode('utf8'), reference='15/29');
        current.db.risk_phrase.insert( label=u'.Harmful by inhalation and in contact with skin'.encode('utf8'), reference='20/21');
        current.db.risk_phrase.insert( label=u'.Harmful by inhalation and if swallowed'.encode('utf8'), reference='20/22');
        current.db.risk_phrase.insert( label=u'.Harmful by inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='20/21/22');
        current.db.risk_phrase.insert( label=u'.Harmful in contact with skin and if swallowed'.encode('utf8'), reference='21/22');
        current.db.risk_phrase.insert( label=u'.Toxic by inhalation and in contact with skin'.encode('utf8'), reference='23/24');
        current.db.risk_phrase.insert( label=u'.Toxic by inhalation and if swallowed'.encode('utf8'), reference='23/25');
        current.db.risk_phrase.insert( label=u'.Toxic by inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='23/24/25');
        current.db.risk_phrase.insert( label=u'.Toxic in contact with skin and if swallowed'.encode('utf8'), reference='24/25');
        current.db.risk_phrase.insert( label=u'.Very toxic by inhalation and in contact with skin'.encode('utf8'), reference='26/27');
        current.db.risk_phrase.insert( label=u'.Very toxic by inhalation and if swallowed'.encode('utf8'), reference='26/28');
        current.db.risk_phrase.insert( label=u'.Very toxic by inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='26/27/28');
        current.db.risk_phrase.insert( label=u'.Very toxic in contact with skin and if swallowed'.encode('utf8'), reference='27/28');
        current.db.risk_phrase.insert( label=u'.Irritating to eyes and respiratory system'.encode('utf8'), reference='36/37');
        current.db.risk_phrase.insert( label=u'.Irritating to eyes and skin'.encode('utf8'), reference='36/38');
        current.db.risk_phrase.insert( label=u'.Irritating to eyes, respiratory system and skin'.encode('utf8'), reference='36/37/38');
        current.db.risk_phrase.insert( label=u'.Irritating to respiratory system and skin'.encode('utf8'), reference='37/38');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects through inhalation'.encode('utf8'), reference='39/23');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects in contact with skin'.encode('utf8'), reference='39/24');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects if swallowed'.encode('utf8'), reference='39/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects through inhalation and in contact with skin'.encode('utf8'), reference='39/23/24');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects through inhalation and if swallowed'.encode('utf8'), reference='39/23/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects in contact with skin and if swallowed'.encode('utf8'), reference='39/24/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of very serious irreversible effects through inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='39/23/24/25');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects through inhalation'.encode('utf8'), reference='39/26');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects in contact with skin'.encode('utf8'), reference='39/27');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects if swallowed'.encode('utf8'), reference='39/28');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects through inhalation and in contact with skin'.encode('utf8'), reference='39/26/27');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects through inhalation and if swallowed'.encode('utf8'), reference='39/26/28');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects in contact with skin and if swallowed'.encode('utf8'), reference='39/27/28');
        current.db.risk_phrase.insert( label=u'.Very Toxic: danger of very serious irreversible effects through inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='39/26/27/28');
        current.db.risk_phrase.insert( label=u'.May cause sensitization by inhalation and skin contact'.encode('utf8'), reference='42/43');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure through inhalation'.encode('utf8'), reference='48/20');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure in contact with skin'.encode('utf8'), reference='48/21');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure if swallowed'.encode('utf8'), reference='48/22');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure through inhalation and in contact with skin'.encode('utf8'), reference='48/20/21');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure through inhalation and if swallowed'.encode('utf8'), reference='48/20/22');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure in contact with skin and if swallowed'.encode('utf8'), reference='48/21/22');
        current.db.risk_phrase.insert( label=u'.Harmful: danger of serious damage to health by prolonged exposure through inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='48/20/21/22');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure through inhalation'.encode('utf8'), reference='48/23');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure in contact with skin'.encode('utf8'), reference='48/24');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure if swallowed'.encode('utf8'), reference='48/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure through inhalation and in contact with skin'.encode('utf8'), reference='48/23/24');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure through inhalation and if swallowed'.encode('utf8'), reference='48/23/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure in contact with skin and if swallowed'.encode('utf8'), reference='48/24/25');
        current.db.risk_phrase.insert( label=u'.Toxic: danger of serious damage to health by prolonged exposure through inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='48/23/24/25');
        current.db.risk_phrase.insert( label=u'.Very toxic to aquatic organisms, may cause long-term adverse effects in the aquatic environment'.encode('utf8'), reference='50/53');
        current.db.risk_phrase.insert( label=u'.Toxic to aquatic organisms, may cause long-term adverse effects in the aquatic environment'.encode('utf8'), reference='51/53');
        current.db.risk_phrase.insert( label=u'.Harmful to aquatic organisms, may cause long-term adverse effects in the aquatic environment'.encode('utf8'), reference='52/53');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects through inhalation'.encode('utf8'), reference='68/20');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects in contact with skin'.encode('utf8'), reference='68/21');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects if swallowed'.encode('utf8'), reference='68/22');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects through inhalation and in contact with skin'.encode('utf8'), reference='68/20/21');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects through inhalation and if swallowed'.encode('utf8'), reference='68/20/22');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects in contact with skin and if swallowed'.encode('utf8'), reference='68/21/22');
        current.db.risk_phrase.insert( label=u'.Harmful: possible risk of irreversible effects through inhalation, in contact with skin and if swallowed'.encode('utf8'), reference='68/20/21/22');

    if current.db(current.db.safety_phrase.id > 0).count() == 0:
        mylogger.debug(message='-populating safety_phrase')
        current.db.safety_phrase.insert( label=u'.Keep locked up'.encode('utf8'), reference='1');
        current.db.safety_phrase.insert( label=u'.Keep out of the reach of children'.encode('utf8'), reference='2');
        current.db.safety_phrase.insert( label=u'.Keep in a cool place'.encode('utf8'), reference='3');
        current.db.safety_phrase.insert( label=u'.Keep away from living quarters'.encode('utf8'), reference='4');
        current.db.safety_phrase.insert( label=u'.Keep contents under ... (there follows the name of a liquid)'.encode('utf8'), reference='5');
        current.db.safety_phrase.insert( label=u'.Keep under ... (inert gas to be specified by the manufacturer)'.encode('utf8'), reference='6');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed'.encode('utf8'), reference='7');
        current.db.safety_phrase.insert( label=u'.Keep container dry'.encode('utf8'), reference='8');
        current.db.safety_phrase.insert( label=u'.Keep container in a well-ventilated place'.encode('utf8'), reference='9');
        current.db.safety_phrase.insert( label=u'.Do not keep the container sealed'.encode('utf8'), reference='12');
        current.db.safety_phrase.insert( label=u'.Keep away from food, drink and animal feeding stuffs'.encode('utf8'), reference='13');
        current.db.safety_phrase.insert( label=u'.Keep away from ... (incompatible materials to be indicated by the manufacturer)'.encode('utf8'), reference='14');
        current.db.safety_phrase.insert( label=u'.Keep away from heat'.encode('utf8'), reference='15');
        current.db.safety_phrase.insert( label=u'.Keep away from sources of ignition - No smoking'.encode('utf8'), reference='16');
        current.db.safety_phrase.insert( label=u'.Keep away from combustible material'.encode('utf8'), reference='17');
        current.db.safety_phrase.insert( label=u'.Handle and open container with care'.encode('utf8'), reference='18');
        current.db.safety_phrase.insert( label=u'.When using do not eat or drink'.encode('utf8'), reference='20');
        current.db.safety_phrase.insert( label=u'.When using do not smoke'.encode('utf8'), reference='21');
        current.db.safety_phrase.insert( label=u'.Do not breathe dust'.encode('utf8'), reference='22');
        current.db.safety_phrase.insert( label=u'.Do not breathe gas/fumes/vapour/spray (appropriate wording to be specified by the manufacturer)'.encode('utf8'), reference='23');
        current.db.safety_phrase.insert( label=u'.Avoid contact with skin'.encode('utf8'), reference='24');
        current.db.safety_phrase.insert( label=u'.Avoid contact with eyes'.encode('utf8'), reference='25');
        current.db.safety_phrase.insert( label=u'.In case of contact with eyes, rinse immediately with plenty of water and seek medical advice'.encode('utf8'), reference='26');
        current.db.safety_phrase.insert( label=u'.Take off immediately all contaminated clothing'.encode('utf8'), reference='27');
        current.db.safety_phrase.insert( label=u'.After contact with skin, wash immediately with plenty of ... (to be specified by the manufacturer)'.encode('utf8'), reference='28');
        current.db.safety_phrase.insert( label=u'.Do not empty into drains'.encode('utf8'), reference='29');
        current.db.safety_phrase.insert( label=u'.Never add water to this product'.encode('utf8'), reference='30');
        current.db.safety_phrase.insert( label=u'.Take precautionary measures against static discharges'.encode('utf8'), reference='33');
        current.db.safety_phrase.insert( label=u'.This material and its container must be disposed of in a safe way'.encode('utf8'), reference='35');
        current.db.safety_phrase.insert( label=u'.Wear suitable protective clothing'.encode('utf8'), reference='36');
        current.db.safety_phrase.insert( label=u'.Wear suitable gloves'.encode('utf8'), reference='37');
        current.db.safety_phrase.insert( label=u'.In case of insufficient ventilation wear suitable respiratory equipment'.encode('utf8'), reference='38');
        current.db.safety_phrase.insert( label=u'.Wear eye/face protection'.encode('utf8'), reference='39');
        current.db.safety_phrase.insert( label=u'.To clean the floor and all objects contaminated by this material use ... (to be specified by the manufacturer)'.encode('utf8'), reference='40');
        current.db.safety_phrase.insert( label=u'.In case of fire and/or explosion do not breathe fumes'.encode('utf8'), reference='41');
        current.db.safety_phrase.insert( label=u'.During fumigation/spraying wear suitable respiratory equipment (appropriate wording to be specified by the manufacturer)'.encode('utf8'), reference='42');
        current.db.safety_phrase.insert( label=u'.In case of firese ... (indicate in the space the precise type of fire-fighting equipment. If water increases the risk add - Neverse water)'.encode('utf8'), reference='43');
        current.db.safety_phrase.insert( label=u'.In case of accident or if you feel unwell seek medical advice immediately (show the label where possible)'.encode('utf8'), reference='45');
        current.db.safety_phrase.insert( label=u'.If swallowed, seek medical advice immediately and show this container or label'.encode('utf8'), reference='46');
        current.db.safety_phrase.insert( label=u'.Keep at temperature not exceeding ... °C (to be specified by the manufacturer)'.encode('utf8'), reference='47');
        current.db.safety_phrase.insert( label=u'.Keep wet with ... (appropriate material to be specified by the manufacturer)'.encode('utf8'), reference='48');
        current.db.safety_phrase.insert( label=u'.Keep only in the original container'.encode('utf8'), reference='49');
        current.db.safety_phrase.insert( label=u'.Do not mix with ... (to be specified by the manufacturer)'.encode('utf8'), reference='50');
        current.db.safety_phrase.insert( label=u'.Use only in well-ventilated areas'.encode('utf8'), reference='51');
        current.db.safety_phrase.insert( label=u'.Not recommended for interior use on large surface areas'.encode('utf8'), reference='52');
        current.db.safety_phrase.insert( label=u'.Avoid exposure - obtain special instructions before use'.encode('utf8'), reference='53');
        current.db.safety_phrase.insert( label=u'.Dispose of this material and its container at hazardous or special waste collection point'.encode('utf8'), reference='56');
        current.db.safety_phrase.insert( label=u'.Use appropriate containment to avoid environmental contamination'.encode('utf8'), reference='57');
        current.db.safety_phrase.insert( label=u'.Refer to manufacturer/SUPPLIER for information on recovery/recycling'.encode('utf8'), reference='59');
        current.db.safety_phrase.insert( label=u'.This material and its container must be disposed of as hazardous waste'.encode('utf8'), reference='60');
        current.db.safety_phrase.insert( label=u'.Avoid release to the environment. Refer to special instructions/safety data sheet'.encode('utf8'), reference='61');
        current.db.safety_phrase.insert( label=u'.If swallowed, do not induce vomiting: seek medical advice immediately and show this container or label'.encode('utf8'), reference='62');
        current.db.safety_phrase.insert( label=u'.In case of accident by inhalation: remove casualty to fresh air and keep at rest'.encode('utf8'), reference='63');
        current.db.safety_phrase.insert( label=u'.If swallowed, rinse mouth with water (only if the PERSON is conscious)'.encode('utf8'), reference='64');
        current.db.safety_phrase.insert( label=u'.Keep locked up and out of the reach of children'.encode('utf8'), reference='1/2');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed in a cool place'.encode('utf8'), reference='3/7');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed in a cool, well-ventilated place'.encode('utf8'), reference='3/7/9');
        current.db.safety_phrase.insert( label=u'.Keep in a cool, well-ventilated place away from ... (incompatible materials to be indicated by the manufacturer)'.encode('utf8'), reference='3/9/14');
        current.db.safety_phrase.insert( label=u'.Keep only in the original container in a cool, well-ventilated place away from ... (incompatible materials to be indicated by the manufacturer)'.encode('utf8'), reference='3/9/14/49');
        current.db.safety_phrase.insert( label=u'.Keep only in the original container in a cool, well-ventilated place'.encode('utf8'), reference='3/9/49');
        current.db.safety_phrase.insert( label=u'.Keep in a cool place away from ... (incompatible materials to be indicated by the manufacturer)'.encode('utf8'), reference='3/14');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed and dry'.encode('utf8'), reference='7/8');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed and in a well-ventilated place'.encode('utf8'), reference='7/9');
        current.db.safety_phrase.insert( label=u'.Keep container tightly closed and at temperature not exceeding ... °C (to be specified by the manufacturer)'.encode('utf8'), reference='7/47');
        current.db.safety_phrase.insert( label=u'.When using do not eat, drink or smoke'.encode('utf8'), reference='20/21');
        current.db.safety_phrase.insert( label=u'.Avoid contact with skin and eyes'.encode('utf8'), reference='24/25');
        current.db.safety_phrase.insert( label=u'.After contact with skin, take off immediately all contaminated clothing, and wash immediately with plenty of ... (to be specified by the manufacturer)'.encode('utf8'), reference='27/28');
        current.db.safety_phrase.insert( label=u'.Do not empty into drains; dispose of this material and its container in a safe way'.encode('utf8'), reference='29/35');
        current.db.safety_phrase.insert( label=u'.Do not empty into drains, dispose of this material and its container at hazardous or special waste collection point'.encode('utf8'), reference='29/56');
        current.db.safety_phrase.insert( label=u'.Wear suitable protective clothing and gloves'.encode('utf8'), reference='36/37');
        current.db.safety_phrase.insert( label=u'.Wear suitable protective clothing, gloves and eye/face protection'.encode('utf8'), reference='36/37/39');
        current.db.safety_phrase.insert( label=u'.Wear suitable protective clothing and eye/face protection'.encode('utf8'), reference='36/39');
        current.db.safety_phrase.insert( label=u'.Wear suitable gloves and eye/face protection'.encode('utf8'), reference='37/39');
        current.db.safety_phrase.insert( label=u'.Keep only in the original container at temperature not exceeding ... °C (to be specified by the manufacturer)'.encode('utf8'), reference='47/49');

    if current.db(current.db.signal_word.id > 0).count() == 0:
        mylogger.debug(message='-populating signal_word'.encode('utf8'))
        current.db.signal_word.insert( label=u'warning'.encode('utf8'))
        current.db.signal_word.insert( label=u'danger'.encode('utf8'))

    if current.db(current.db.supplier.id > 0).count() == 0:
        mylogger.debug(message='-populating supplier'.encode('utf8'))
        current.db.supplier.insert( label=u'sample_supplier'.encode('utf8'))

    if current.db(current.db.symbol.id > 0).count() == 0:
        mylogger.debug(message='-populating symbol')
        current.db.symbol.insert( label=u'SGH01'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH02'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH03'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH04'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH05'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH06'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH07'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH08'.encode('utf8'));
        current.db.symbol.insert( label=u'SGH09'.encode('utf8'));

    if current.db(current.db.unit.id > 0).count() == 0:
        mylogger.debug(message='-populating unit')
        _id_l_unit = current.db.unit.insert( label=u'l', reference=None, multiplier_for_reference=1);
        current.db.unit.insert( label=u'ml'.encode('utf8'), reference=_id_l_unit, multiplier_for_reference=0.001);
        current.db.unit.insert( label=u'µl'.encode('utf8'), reference=_id_l_unit, multiplier_for_reference=1.0000000000000001e-05);

        _id_g_unit = current.db.unit.insert( label=u'g', reference=None, multiplier_for_reference=1);
        current.db.unit.insert( label=u'kg'.encode('utf8'), reference=_id_g_unit, multiplier_for_reference=1000);
        current.db.unit.insert( label=u'mg'.encode('utf8'), reference=_id_g_unit, multiplier_for_reference=0.001);
        current.db.unit.insert( label=u'µg'.encode('utf8'), reference=_id_g_unit, multiplier_for_reference=1.0000000000000001e-05);

        _id_m_unit = current.db.unit.insert( label=u'm', reference=None, multiplier_for_reference=1);
        current.db.unit.insert( label=u'dm'.encode('utf8'), reference=_id_m_unit, multiplier_for_reference=0.1);
        current.db.unit.insert( label=u'cm'.encode('utf8'), reference=_id_m_unit, multiplier_for_reference=0.01);

        current.db(current.db.unit.id==_id_l_unit).select().first().update_record(reference=_id_l_unit)
        current.db(current.db.unit.id==_id_g_unit).select().first().update_record(reference=_id_g_unit)
        current.db(current.db.unit.id==_id_m_unit).select().first().update_record(reference=_id_m_unit)

    if current.db(current.db.command_status.id > 0).count() == 0:
        mylogger.debug(message='-populating command status')
        current.db.command_status.insert( label=u'New'.encode('utf8'), state=0, rank=1);
        current.db.command_status.insert( label=u'Accepted'.encode('utf8'), state=0, rank=2);
        current.db.command_status.insert( label=u'Ordered'.encode('utf8'), state=0, rank=3);
        current.db.command_status.insert( label=u'Shipped'.encode('utf8'), state=0, rank=4);
        current.db.command_status.insert( label=u'Integrated'.encode('utf8'), state=1, rank=5);
        current.db.command_status.insert( label=u'Canceled'.encode('utf8'), state=2, rank=6);

    current.db.commit()
