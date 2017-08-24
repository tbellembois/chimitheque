# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_ide_autocomplete import *

from c_unit import UNIT
from chimitheque_logger import chimitheque_logger
from gluon import current

mylogger = chimitheque_logger()


class UNIT_MAPPER(object):

    def __init__(self):
        pass

    def __unit_from_row(self, unit_row):
        return UNIT(id=unit_row['id'],
                    label=unit_row['label'],
                    reference=lambda: self.find(unit_row['reference']),
                    multiplier_for_reference=unit_row['multiplier_for_reference'])

    def find(self, unit_id):
        return self.__unit_from_row(current.db(current.db.unit.id == unit_id).select().first())

    def find_references(self):
        return [ self.__unit_from_row(_unit) for _unit in current.db(current.db.unit.id.belongs(
                                                                                                [ _u.reference for _u  in current.db(current.db.unit).select(current.db.unit.reference,
                                                                                                                                     groupby=current.db.unit.reference) ]
                                                                                                )).select() ]