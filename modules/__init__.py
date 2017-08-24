from gluon.settings import settings
import ConfigParser
import os
import os.path
import re
import csv
from gluon import current

#
# configuration
#
this_file_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(this_file_dir, '../configuration.cfg')
config = ConfigParser.RawConfigParser()
config.read(config_file_path)

settings['CMR'] = {
'45': 'C1A',
'49': 'C1A',
'40': 'C2',
'46': 'M1A',
'68': 'M2',
'60': 'R1A',
'61': 'R1A',
'62': 'R2',
'63': 'R2',
'H350': 'C1A',
'H350i': 'C1A',
'H351': 'C2',
'H340': 'M1A',
'H341': 'M2',
'H360': 'R1A',
'H360F': 'R1A',
'H360D': 'R1A',
'H360Fd': 'R1A',
'H360Fd': 'R1A',
'H360Df': 'R1A',
'H361': 'R2',
'H361f': 'R2', 
'H361d': 'R2',
'H361fd': 'R2',
'H362': 'L'
}

settings['atom_array'] = {
    'H': 'hydrogen',
    'He': 'helium',
    'Li': 'lithium',
    'Be': 'berylium',
    'B': 'boron',
    'C': 'carbon',
    'N': 'nitrogen',
    'O': 'oxygen',
    'F': 'fluorine',
    'Ne': 'neon',
    'Na': 'sodium',
    'Mg': 'magnesium',
    'Al': 'aluminium',
    'Si': 'silicon',
    'P': 'phosphorus',
    'S': 'sulfure',
    'Cl': 'chlorine',
    'Ar': 'argon',
    'K': 'potassium',
    'Ca': 'calcium',
    'Sc': 'scandium',
    'Ti': 'titanium',
    'V': 'vanadium',
    'Cr': 'chromium',
    'Mn': 'manganese',
    'Fe': 'iron',
    'Co': 'cobalt',
    'Ni': 'nickel',
    'Cu': 'copper',
    'Zn': 'zinc',
    'Ga': 'gallium',
    'Ge': 'germanium',
    'As': 'arsenic',
    'Se': 'sefeniuo',
    'Br': 'bromine',
    'Kr': 'krypton',
    'Rb': 'rubidium',
    'Sr': 'strontium',
    'Y': 'yltrium',
    'Zr': 'zirconium',
    'Nb': 'niobium',
    'Mo': 'molybdenum',
    'Tc': 'technetium',
    'Ru': 'ruthenium',
    'Rh': 'rhodium',
    'Pd': 'palladium',
    'Ag': 'silver',
    'Cd': 'cadmium',
    'In': 'indium',
    'Sn': 'tin',
    'Sb': 'antimony',
    'Te': 'tellurium',
    'I': 'iodine',
    'Xe': 'xenon',
    'Cs': 'caesium',
    'Ba': 'barium',
    'Hf': 'hafnium',
    'Ta': 'tantalum',
    'W': 'tungsten',
    'Re': 'rhenium',
    'Os': 'osmium',
    'Ir': 'iridium',
    'Pt': 'platinium',
    'Au': 'gold',
    'Hg': 'mercury',
    'Tl': 'thallium',
    'Pb': 'lead',
    'Bi': 'bismuth',
    'Po': 'polonium',
    'At': 'astatine',
    'Rn': 'radon',
    'Fr': 'francium',
    'Ra': 'radium',
    'Rf': 'rutherfordium',
    'Db': 'dubnium',
    'Sg': 'seaborgium',
    'Bh': 'bohrium',
    'Hs': 'hassium',
    'Mt': 'meitnerium',
    'Ds': 'darmstadtium',
    'Rg': 'roentgenium',
    'Cn': 'copemicium',
    'La': 'lanthanum',
    'Ce': 'cerium',
    'Pr': 'praseodymium',
    'Nd': 'neodymium',
    'Pm': 'promethium',
    'Sm': 'samarium',
    'Eu': 'europium',
    'Gd': 'gadolinium',
    'Tb': 'terbium',
    'Dy': 'dysprosium',
    'Ho': 'holmium',
    'Er': 'erbium',
    'Tm': 'thulium',
    'Yb': 'ytterbium',
    'Lu': 'lutetium',
    'Ac': 'actinium',
    'Th': 'thorium',
    'Pa': 'protactinium',
    'U': 'uranium',
    'Np': 'neptunium',
    'Pu': 'plutonium',
    'Am': 'americium',
    'Cm': 'curium',
    'Bk': 'berkelium',
    'Cf': 'californium',
    'Es': 'einsteinium',
    'Fm': 'fermium',
    'Md': 'mendelevium',
    'No': 'nobelium',
    'Lr': 'lawrencium',
    'D': 'deuterium'}

settings['app_version'] = config.get('global', 'version')
settings['release_date'] = config.get('global', 'releasedate')
settings['organization'] = config.get('global', 'organization')
settings['organization_url'] = config.get('global', 'organization_url')
settings['lab_url'] = config.get('global', 'lab_url')
settings['application_url'] = config.get('global', 'applicationurl')
settings['chimitheque_repository'] = config.get('global', 'chimitheque_repository')
settings['language'] = config.get('global', 'language')
settings['hmac_key'] = config.get('global', 'hmac_key')
settings['session_time'] = config.get('global', 'session_time')
settings['disable_version_check'] = config.get('global', 'disable_version_check').lower() == 'true'

settings['db_connection'] = config.get('database', 'connection')
settings['db_fake_migrate'] = config.get('database', 'fake_migrate').lower() == 'true'

settings['mail_server'] = config.get('mail', 'server')
settings['mail_sender'] = config.get('mail', 'sender')
settings['mail_login'] = config.get('mail', 'login')
settings['mail_tls'] = config.get('mail', 'tls').lower() == 'true'

settings['error_mail_enable'] = config.get('error', 'enable').lower() == 'true'
settings['error_mail_recipient'] = config.get('error', 'recipient')

settings['ldap_enable'] = config.get('ldap', 'enable').lower() == 'true'
settings['ldap_hostname'] = config.get('ldap', 'hostname')
settings['ldap_userdn'] = config.get('ldap', 'userdn')
settings['ldap_password'] = config.get('ldap', 'password')
settings['ldap_base'] = config.get('ldap', 'base')
settings['ldap_scope'] = config.get('ldap', 'scope')
settings['ldap_att_firstname'] = config.get('ldap', 'att_firstname')
settings['ldap_att_lastname'] = config.get('ldap', 'att_lastname')
settings['ldap_att_username'] = config.get('ldap', 'att_username')
settings['ldap_att_email'] = config.get('ldap', 'att_email')

settings['cas_enable'] = config.get('cas', 'enable').lower() == 'true'
settings['cas_provider'] = config.get('cas', 'provider')

settings['disabled_permissions'] = { 'select_pc': True,
                                     'read_pc': True,
                                     'select_rpc': False,
                                     'select_ent': True,
                                     'read_ent': True,
                                     'select_coc': True,
                                     'read_coc': True,
                                     'select_sup': True,
                                     'read_sup': True,
                                     'select_sl': False,
                                     'select_archive': False,
                                     'update_archive': False,
                                     'create_archive': False,
                                     'select_message': False,
                                     'read_message': False,
                                     'update_message': False,
                                     'delete_message': False
                                      }

settings['permission_dependencies'] = {
                                        "delete_pc": ["create_pc"],
                                        "create_pc": ["update_pc"],

                                        "delete_rpc": ["create_rpc", "delete_pc"],
                                        "create_rpc": ["update_rpc", "create_pc"],
                                        "update_rpc": ["read_rpc", "update_pc"],

                                        "delete_sc": ["read_archive", "create_sc"],
                                        "create_sc": ["update_sc"],
                                        "update_sc": ["read_sc"],
                                        "read_sc": ["select_sc", "read_sl"],
                                        "select_sc": ["select_user"],

                                        "delete_archive": ["read_archive"],
                                        "read_archive": ["read_sc"],

                                        "delete_sl": ["create_sl"],
                                        "create_sl": ["update_sl"],
                                        "update_sl": ["read_sl"],

                                        "delete_ent": ["create_ent", "delete_user"],
                                        "create_ent": ["update_ent", "create_user"],

                                        "delete_user": ["create_user"],
                                        "create_user": ["update_user"],
                                        "update_user": ["read_user"],
                                        "read_user": ["select_user"],

                                        "delete_coc": ["create_coc"],
                                        "create_coc": ["update_coc"],

                                        "delete_sup": ["create_sup"],
                                        "create_sup": ["update_sup"],

                                        "delete_com": ["create_com"],
                                        "create_com": ["update_com"],
                                        "update_com": ["read_com"],
                                        "read_com": ["select_com"],

    };
