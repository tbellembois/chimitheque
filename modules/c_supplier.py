# coding: utf-8
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
# -*- coding: utf-8 -*-
from chimitheque_logger import chimitheque_logger

mylogger = chimitheque_logger()


class SUPPLIER(object):

    def __init__(self, *args, **kwargs):

        self.__id = kwargs.get('id')
        self.__label = kwargs.get('label')

    def __repr__(self):
        return '<SUPPLIER:%s:%s>' % (self.id, self.label)

    @property
    def id(self):
        return self.__id

    @property
    def label(self):
        return self.__label
