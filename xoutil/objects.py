#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.objutil
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Feb 17, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


from functools import partial
import types

from xoutil.types import Unset, is_collection

__docstring_format__ = 'rst'
__author__ = 'manu'



'''
Several utilities for objects in general.
'''

# These two functions can be use to always return True or False
_true = lambda * args, **kwargs: True
_false = lambda * args, **kwargs: False



def xdir(obj, attr_filter=_true, value_filter=_true):
    '''
    Return all (attr, value) pairs from "obj" that attr_filter(attr) and
    value_filter(value) are both True.
    '''
    attrs = (attr for attr in dir(obj) if attr_filter(attr))
    return ((a, v) for a, v in ((a, getattr(obj, a)) for a in attrs) if value_filter(v))


def validate_attrs(source, target, force_equals=(), force_differents=()):
    '''
    Makes a 'comparison' of `source` and `target` by its attributes.
    
    This function returns True if and only if both of this tests pass:
    
    - All attributes in `force_equals` are equal in `source` and `target`
    - All attributes in `force_differents` are different in `source` and `target`
    
    For instance::
    
        >>> class Person(object):
        ...    def __init__(self, **kwargs):
        ...        for which in kwargs:
        ...            setattr(self, which, kwargs[which])
        
        >>> source = Person(**{b'name': 'Manuel', b'age': 33, b'sex': 'male'})
        >>> target = Person(**{b'name': 'Manuel', b'age': 4, b'sex': 'male'})
        
        >>> validate_attrs(source, target, force_equals=(b'sex',), force_differents=(b'age',))
        True
        
        >>> validate_attrs(source, target, force_equals=(b'age',))
        False
        
    If both `force_equals` and `force_differents` are empty it will return 
    True::
        
        >>> validate_attrs(source, target)
        True
    '''
    from operator import eq, ne
    res = True
    tests = ((ne, force_equals), (eq, force_differents))
    j = 0
    while res and  (j < len(tests)):
        fail, attrs = tests[j]
        i = 0
        while res and  (i < len(attrs)):
            attr = attrs[i]
            if fail(getattr(source, attr), getattr(target, attr)):
                res = False
            else:
                i += 1
        j += 1
    return res


def get_first_of(source, *keys):
    '''
    Return the first occurrence of any of the specified keys in source.
    if source is a tuple, a list, a set, or a generator; then the keys are searched in all items inside.
    If you need to use default values, pass a tuple with the last argument using a dictionary with them.
    
    Examples:
    
    - To search some keys (whatever is found first) from a dict::
  
        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "no", "foo", "spam")
        'bar'
        
    - If a key/attr is not found, None is returned::
    
        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "eggs") is None
        True
  
    - Objects may be sources as well::
    
        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar'
        >>> inst.eggs = 'spam'
        >>> get_first_of(inst, 'no', 'eggs', 'foo')
        'spam'
        
        >>> get_first_of(inst, 'invalid') is None
        True
        
    - You may pass several sources in a list, tuple or generator, and `get_first`
      will try each object at a time until it finds any of the key on a object; 
      so any object that has one of the keys will "win"::
    
        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'
        >>> get_first_of((somedict, inst), 'eggs')
        'spam'
        
        >>> get_first_of((somedict, inst), 'foo')
        'bar'
        
        >>> get_first_of((inst, somedict), 'foo')
        'bar2'
        
        >>> get_first_of((inst, somedict), 'foobar') is None
        True
    '''

    def inner(source):
        from collections import Mapping
        get = source.get if isinstance(source, Mapping) else partial(getattr, source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if is_collection(source):
        from itertools import imap, takewhile
        res = Unset
        for item in takewhile(lambda item: (res is Unset), imap(inner, source)):
            if item is not Unset:
                res = item
    else:
        res = inner(source)
    return res if res is not Unset else None


def smart_getattr(name, *sources, **kw):
    '''
    Gets an attr by name for the first source that has it.
    
        >>> somedict = {'foo': 'bar', 'spam': 'eggs'}
        >>> class Some(object): pass
        >>> inst = Some()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'
        
        >>> smart_getattr('foo', somedict, inst)
        'bar'
        
        >>> smart_getattr('foo', inst, somedict)
        'bar2'
        
        >>> smart_getattr('fail', somedict, inst) is Unset
        True
        
    [2012-01-10] Added a keyword argument `default`::
    
        >>> smart_getattr('fail', somedict, inst, default=0)
        0
    '''
    default = kw.setdefault('default', Unset)
    return get_first_of(sources, name) or default


def get_and_del_attr(obj, name, default=None):
    '''
    Looks for an attribute in the :param:`obj` and returns its value and removes
    the attribute. If the attribute is not found, :param:`default` is returned
    instead.
    '''
    res = getattr(obj, name, Unset)
    if res is Unset:
        res = default
    else:
        try:
            delattr(obj, name)
        except AttributeError:
            try:
                delattr(obj.__class__, name)
            except AttributeError:
                pass
    return res


def setdefaultattr(obj, name, value):
    '''
    Sets the attribute name to value if it is not set::
    
        >>> class Someclass(object): pass
        >>> inst = Someclass()
        >>> setdefaultattr(inst, 'foo', 'bar')
        'bar'
        
        >>> inst.foo
        'bar'
        
        >>> inst.spam = 'egg'
        >>> setdefaultattr(inst, 'spam', 'with ham')
        'egg'
    '''
    res = getattr(obj, name, Unset)
    if res is Unset:
        setattr(obj, name, value)
        res = value
    return res


def nameof(target):
    '''
    Gets the name of an object: 
    
    - The name of a string is the same string::
    
        >>> nameof('manuel')
        'manuel'
        
    - The name of an object with a ``__name__`` attribute is its value::
    
        >>> nameof(type)
        'type'
        
        >>> class Someclass: pass
        >>> nameof(Someclass)
        'Someclass'
        
    - The name of any other object is the ``__name__`` of the its type::
    
        >>> nameof([1, 2])
        'list'
        
        >>> nameof((1, 2))
        'tuple'
        
        >>> nameof({})
        'dict'
    
    '''
    if isinstance(target, basestring):
        return target
    else:
        if not hasattr(target, '__name__'):
            target = type(target)
        return target.__name__