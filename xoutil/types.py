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

from xoutil.modules import copy_members as _copy_python_module_members

_pm = _copy_python_module_members()
GeneratorType = _pm.GeneratorType

del _pm, _copy_python_module_members

from xoutil.compat import xrange_
from xoutil.compat import pypy as _pypy
from xoutil._values import UnsetType, Unset, Ignored as ignored
from xoutil.deprecation import deprecated

from xoutil.collections import mro_dict as _mro_dict
mro_dict = deprecated(_mro_dict)(_mro_dict)

#: The type of methods that are builtin in Python.
#:
#: This is roughly the type of the ``object.__getattribute__`` method.
WrapperDescriptorType = SlotWrapperType = type(object.__getattribute__)


#: A compatible Py2 and Py3k DictProxyType, since it does not exists in Py3k.
DictProxyType = type(object.__dict__)


from xoutil.names import strlist as strs
__all__ = strs('UnsetType', 'Unset', 'ignored', 'DictProxyType',
               'SlotWrapperType', 'is_iterable', 'is_collection',
               'is_string_like', 'is_scalar', 'is_staticmethod',
               'is_classmethod', 'is_instancemethod', 'is_slotwrapper',
               'is_module', 'Required')
del strs


if _pypy:
    class _foo(object):
        __slots__ = 'bar'
    MemberDescriptorType = type(_foo.bar)
    del _foo


def is_iterable(maybe):
    '''Returns True if `maybe` is an iterable object (e.g. implements the
    `__iter__` method):

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
    '''Returns True if `maybe` is a string, an int, or some other scalar type
    (i.e not an iterable.)

    '''
    return is_string_like(maybe) or not is_iterable(maybe)


def is_staticmethod(desc, name=Unset):
    '''Returns true if a `method` is a static method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    from xoutil.collections import mro_dict
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, staticmethod)


def is_classmethod(desc, name=Unset):
    '''Returns true if a `method` is a class method.

    :param desc: This may be the method descriptor or the class that holds the
                 method, in the second case you must provide the `name` of the
                 method.

                 .. note::

                    Notice that in the first case what is needed is the
                    **method descriptor**, i.e, taken from the class'
                    `__dict__` attribute. If instead you pass something like
                    ``cls.methodname``, this method will return False whilst
                    :func:`is_instancemethod` will return True.

    :param name: The name of the method, if the first argument is the class.

    '''
    from xoutil.collections import mro_dict
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, classmethod)


def is_instancemethod(desc, name=Unset):
    '''Returns true if a given `method` is neither a static method nor a class
    method.

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    from types import FunctionType
    from xoutil.collections import mro_dict
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, FunctionType)


def is_slotwrapper(desc, name=Unset):
    '''Returns True if a given `method` is a slot wrapper (i.e. a method that
    is builtin in the `object` base class).

    This function takes the same arguments as :func:`is_classmethod`.

    '''
    from xoutil.collections import mro_dict
    if name:
        desc = mro_dict(desc).get(name, None)
    return isinstance(desc, SlotWrapperType)


def is_module(maybe):
    '''Returns True if `maybe` is a module.'''
    from types import ModuleType
    return isinstance(maybe, ModuleType)


class Required(object):
    '''A type for required fields in scenarios where a default is not
    possible.

    '''
    def __init__(self, *args, **kwargs):
        pass
