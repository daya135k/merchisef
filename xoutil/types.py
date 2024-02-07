# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.types
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2010-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


'''
This modules mirrors all the functions (and, in general, objects) from the
standard library module ``types``; but it also includes several new types and
type-related functions.
'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import types as _legacy
from types import *

from xoutil.compat import xrange_
from xoutil.string import names as _names

__all__ = _names('Unset', 'is_iterable', 'is_collection', 'is_scalar',
                 'is_string_like')

class _UnsetType(type):
    'The type of the :obj:`Unset` value.'
    def __nonzero__(self):
        return False

    def __repr__(self):
        return self.__name__
    __str__ = __repr__


class classobject(object):
    def __new__(cls, *args, **kwargs):
        raise TypeError("cannot create '{0}' instances".format(cls.__name__))


class Unset(classobject):
    '''To be used as default value to be sure none is returned in scenarios
    where `None` could be a valid value.

    For example::

        >>> getattr('', '__doc__', Unset) is Unset
        False

    '''
    __metaclass__ = _UnsetType


class ignored(classobject):
    '''To be used in arguments that are currently ignored cause they are being
    deprecated. The only valid reason to use `ignored` is to signal ignored
    arguments in method's/function's signature.

    '''
    __metaclass__ = _UnsetType


def is_iterable(maybe):
    '''
    Returns True if `maybe` an iterable object (e.g. implements the `__iter__`
    method:)

    ::

        >>> is_iterable('all strings are iterable')
        True

        # Numbers are not
        >>> is_iterable(1)
        False

        >>> is_iterable(xrange_(1))
        True

        >>> is_iterable({})
        True

        >>> is_iterable(tuple())
        True

        >>> is_iterable(set())
        True
    '''
    try:
        iter(maybe)
    except:
        return False
    else:
        return True


def is_collection(maybe):
    '''
    Test `maybe` to see if it is a tuple, a list, a set or a generator
    function.
    It returns False for dictionaries and strings::

        >>> is_collection('all strings are iterable')
        False

        # Numbers are not
        >>> is_collection(1)
        False

        >>> is_collection(xrange_(1))
        True

        >>> is_collection({})
        False

        >>> is_collection(tuple())
        True

        >>> is_collection(set())
        True

        >>> is_collection(a for a in xrange_(100))
        True
    '''
    return isinstance(maybe, (tuple, xrange_, list, set, frozenset,
                              GeneratorType))


def is_string_like(maybe):
    '''Returns True if `maybe` acts like a string'''
    try:
        maybe + ""
    except TypeError:
        return False
    else:
        return True


def is_scalar(maybe):
    '''
    Returns True if `maybe` is a string, an int, or some other scalar type (i.e
    not an iterable.)
    '''
    return is_string_like(maybe) or not is_iterable(maybe)
