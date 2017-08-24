# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_logger import chimitheque_logger

mylogger = chimitheque_logger()


class UNIT(object):

    def __init__(self, *args, **kwargs):

        self.__id = kwargs.get('id')
        self.__label = kwargs.get('label')
        self.__reference = kwargs.get('reference')
        self.__multiplier_for_reference = kwargs.get('multiplier_for_reference')

    def __repr__(self):
        return '<unit:%s:%s>' % (self.__id, self.__label)

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return self.__id == other.__id

    def __lt__(self, other):
        if self is None or other is None:
            return False
        else:
            return self.__id < other.__id

    @property
    def id(self):
        return self.__id

    @property
    def label(self):
        return self.__label

    @property
    def reference(self):
        return self.__reference()

    @property
    def multiplier_for_reference(self):
        return self.__multiplier_for_reference
