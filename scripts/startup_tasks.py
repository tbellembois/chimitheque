# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id
# -*- coding: utf-8 -*-
import chimitheque_commons as cc

print('[ STARTUP TASKS ]')

print('-populating database')
cc.startup_populate_database()

print('-updating product references')
cc.startup_clean_product_missing_references()
print('-updating CMR')
cc.startup_update_cmr()
print('-updating entities')
cc.startup_update_entity()
print('-updating store locations (full paths)')
cc.startup_update_store_location()
print('-updating units')
cc.startup_update_unit()
print('-updating storages')
cc.startup_update_storage()
print('-updating product empirical formulas')
cc.startup_update_product_empirical_formula()
print('-updating product classes of compounds')
cc.startup_update_product_class_of_compounds()
print('-updating user permissions')
cc.startup_update_user_permissions()

print('-cleaning sessions')
cc.clean_session()
