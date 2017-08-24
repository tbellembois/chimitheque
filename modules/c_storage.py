# -*- coding: utf-8 -*-
# Copyright 2011 - Thomas Bellembois thomas.bellembois@ens-lyon.fr
# Cecill licence, see LICENSE
# $Id:
from chimitheque_logger import chimitheque_logger

my_logger = chimitheque_logger()


class STORAGE(object):

    def __init__(self, **kwargs):

        self.__id = kwargs.get('id')
        self.__volume_weight = kwargs.get('volume_weight')
        self.__unit = kwargs.get('unit')  # lambda that return a unit type
        self.__nb_items = kwargs.get('nb_items')
        self.__creation_datetime = kwargs.get('creation_datetime')  # datetime.datetime type
        self.__entry_datetime = kwargs.get('entry_datetime')  # datetime.datetime type
        self.__exit_datetime = kwargs.get('exit_datetime')  # datetime.datetime type
        self.__expiration_datetime = kwargs.get('expiration_datetime')  # datetime.datetime type
        self.__opening_datetime = kwargs.get('opening_datetime')  # datetime.datetime type
        self.__comment = kwargs.get('comment')
        self.__barecode = kwargs.get('barecode')
        self.__reference = kwargs.get('reference')
        self.__batch_number = kwargs.get('batch_number')
        self.__archive = kwargs.get('archive')
        self.__to_destroy = kwargs.get('to_destroy')
        self.__product = kwargs.get('product') if 'product' in kwargs else None  # lambda that return a product or None
        self.__person = kwargs.get('person') if 'person' in kwargs else None  # lambda that return a PERSON or None
        self.__store_location = kwargs.get('store_location') if 'store_location' in kwargs else None  # lambda that return a STORE_LOCATION or None
        self.__supplier = kwargs.get('supplier') if 'supplier' in kwargs else None  # lambda that return a SUPPLIER or None
        # storage history
        self.__modification_datetime = kwargs.get('modification_datetime')  # datetime.datetime type

        self.__has_borrowing = kwargs.get('has_borrowing') if 'has_borrowing' in kwargs else False
        self.__retrieve_borrower = kwargs.get('retrieve_borrower') if 'retrieve_borrower' in kwargs else None  # lambda that return a PERSON
        self.__retrieve_borrow_datetime = kwargs.get('retrieve_borrow_datetime') if 'retrieve_borrow_datetime' in kwargs else None
        self.__retrieve_borrow_comment = kwargs.get('retrieve_borrow_comment') if 'retrieve_borrow_comment' in kwargs else None
        self.__has_history = kwargs.get('has_history') if 'has_history' in kwargs else False # lambda that return a boolean

    def __repr__(self):
        return '<STORAGE:%s:%s:%s:%s>' % (self.id, self.barecode, self.volume_weight, self.unit)

    #
    # attributes
    #
    @property
    def id(self):
        return self.__id

    @property
    def volume_weight(self):
        return self.__volume_weight

    @property
    def unit(self):
        return self.__unit()

    @property
    def nb_items(self):
        return self.__nb_items

    @property
    def creation_datetime(self):
        return self.__creation_datetime

    @property
    def modification_datetime(self):
        return self.__modification_datetime

    @property
    def entry_datetime(self):
        return self.__entry_datetime

    @property
    def exit_datetime(self):
        return self.__exit_datetime

    @exit_datetime.setter
    def exit_datetime(self, value):
        self.__exit_datetime = value

    @property
    def expiration_datetime(self):
        return self.__expiration_datetime

    @property
    def opening_datetime(self):
        return self.__opening_datetime

    @property
    def comment(self):
        return self.__comment

    @property
    def barecode(self):
        return self.__barecode

    @property
    def reference(self):
        return self.__reference

    @property
    def batch_number(self):
        return self.__batch_number

    @property
    def archive(self):
        return self.__archive

    @archive.setter
    def archive(self, value):
        self.__archive = value

    @property
    def to_destroy(self):
        return self.__to_destroy

    @to_destroy.setter
    def to_destroy(self, value):
        self.__to_destroy = value

    @property
    def product(self):
        try:
            return self.__product()
        except TypeError:
            return self.__product

    @property
    def person(self):
        try:
            return self.__person()
        except TypeError:
            return self.__person

    @property
    def store_location(self):
        try:
            return self.__store_location()
        except TypeError:
            return self.__store_location

    @property
    def supplier(self):
        try:
            return self.__supplier()
        except TypeError:
            return self.__supplier

    #
    # methods
    #
    def has_borrowing(self):
        return self.__has_borrowing()

    def retrieve_borrower(self):
        return self.__retrieve_borrower()

    def retrieve_borrow_datetime(self):
        return self.__retrieve_borrow_datetime()

    def retrieve_borrow_comment(self):
        return self.__retrieve_borrow_comment()

    def has_history(self):
        return self.__has_history()
