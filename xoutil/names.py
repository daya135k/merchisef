#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.names
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created 2013-04-15

'''A protocol to obtain or manage object names.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoutil import Undefined as _undef

try:
    str_base = basestring
except NameError:
    str_base = str


def _get_mappings(source):
    '''Return a sequence of mappings from `source`.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    from collections import Mapping
    if isinstance(source, Mapping):
        return (source,)
    else:
        from xoutil.inspect import get_attr_value
        l = get_attr_value(source,  'f_locals', _undef)
        g = get_attr_value(source,  'f_globals', _undef)
        if isinstance(l, Mapping) and isinstance(g, Mapping):
            return (l,) if l is g else (l, g)
        else:
            return tuple(source)


def _key_for_value(source, value, strict=True):
    '''Returns the key that has the "value" in dictionary "source".

    if strict is True, then look first for the same object::
        >>> x = {1}
        >>> y = {1}
        >>> src = {'x': x, 'y': y}
        >>> search = lambda o, strict=True: _key_for_value(src, o, strict)
        >>> search(x) == search(y)
        False
        >>> search(x, strict=False) == search(y, strict=False)
        True

    This is mainly intended to find object names in stack frame variables.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    source = _get_mappings(source)
    found, equal = _undef, None
    i, mapping_count = 0, len(source)
    while found is _undef and (i < mapping_count):
        mapping = source[i]
        keys = list(mapping)
        j, key_count = 0, len(keys)
        while found is _undef and (j < key_count):
            key = keys[j]
            item = mapping[key]
            if item is value:
                found = key
            elif item == value:
                if strict:
                    equal = key
                else:
                    found = key
            j += 1
        i += 1
    return found if found is not _undef else equal


def _get_value(source, key, default=None):
    '''Returns the value for the given `key` in `source` mappings.

    This is mainly intended to obtain object values in stack frame variables.

    Source could be a stack frame, a single dictionary, or any sequence of
    dictionaries.

    '''
    source = _get_mappings(source)
    res = _undef
    i, mapping_count = 0, len(source)
    while res is _undef and (i < mapping_count):
        mapping = source[i]
        res = mapping.get(key, _undef)
        i += 1
    return res if res is not _undef else default


def _get_best_name(names, safe=False, full=False):
    '''Get the best name in the give list of `names`.

    If `safe` is True, returned name must be a valid full identifier.

    '''
    from xoutil.validators import (is_valid_full_identifier,
                                   is_valid_public_identifier,
                                   is_valid_identifier,
                                   is_valid_slug)
    names = list(names)

    def inner(start=0):
        ok, best_idx, best_qlty = start, -1, 0
        i, count = start, len(names)
        assert start < count, 'start is "%s", max is "%s".' % (start, count)
        while i < count:
            name = names[i]
            if '%(next)s' in name:
                next = inner(i + 1)
                names[i] = name % {'next': next}
                count = i + 1
            else:
                if is_valid_slug(name):
                    qlty = 25
                if is_valid_identifier(name):
                    qlty = 75 if is_valid_public_identifier(name) else 50
                elif is_valid_full_identifier(name):
                    qlty = 100
                else:
                    qlty = -25
                if best_qlty <= qlty:
                    best_idx = i
                    best_qlty = qlty
                ok = i
                i += 1
        idx = best_idx if best_idx >= 0 else ok
        return names[idx]
    res = inner()
    if safe:
        is_valid = is_valid_full_identifier if full else is_valid_identifier
        if not is_valid(res):
            from xoutil.string import normalize_slug
            full = full and '.' in res
            if full:
                res = res.replace('.', 'dot_dot_dot')
            res = normalize_slug(res, '_')
            if full:
                res = res.replace('dot_dot_dot', '.')
    return str(res)


def module_name(item):
    '''Returns the module name where the given object is declared.

    TODO: Declare doctests.

    '''
    from xoutil.inspect import get_attr_value
    if item is None:
        res = ''
    elif isinstance(item, str_base):
        res = item
    else:
        res = get_attr_value(item, '__module__', None)
        if res is None:
            res = get_attr_value(type(item), '__module__', '')
    if res.startswith('__') or (res in ('builtins', '<module>')):
        res = ''
    return str(res)


def nameof(*args, **kwargs):
    '''Obtain the name of each one of a set of objects.

    .. versionadded:: 1.4.0

    If no object is given, None is returned; if only one object is given, a
    single string is returned; otherwise a list of strings is returned.

    The name of an object is normally the variable name in the calling stack::

        >>> class OrderedDict(dict):
        ...     pass
        >>> sorted_dict = OrderedDict
        >>> del OrderedDict
        >>> nameof(sorted_dict)
        'sorted_dict'

    If the `inner` flag is true, then the name is found by introspection
    first::

        >>> nameof(sorted_dict, inner=True)
        'OrderedDict'

    If the `typed` flag is true, returns the name of the type unless `target`
    is already a type or it has a "__name__" attribute, but the "__name__" is
    used only if `inner` is True.

        >>> sd = sorted_dict(x=1, y=2)
        >>> nameof(sd)
        'sd'

        >>> nameof(sd, typed=True)
        'sorted_dict'

        >>> nameof(sd, inner=True, typed=True)
        'OrderedDict'

    If `item` is an instance of a simple type (strings or numbers) and
    `inner` is true, then the name is the standard representation of `item`::

        >>> s = 'foobar'
        >>> nameof(s)
        's'

        >>> nameof(s, inner=True)
        'foobar'

        >>> i = 1
        >>> nameof(i)
        'i'

        >>> nameof(i, inner=True)
        '1'

        >>> nameof(i, typed=True)
        'int'

        >>> nameof(i, sd)
        ['i', 'sd']

    If `item` isn't an instance of a simple type (strings or numbers) and
    `inner` is true, then the id of the object is used::

        >>> hex(id(sd)) in nameof(sd, inner=True)
        True

    If `full` is True, then the module where the name if defined is
    prefixed. Examples::

        >>> nameof(sd, full=True)
        'xoutil.names.sd'

        >>> nameof(sd, typed=True, full=True)
        'xoutil.names.sorted_dict'

        >>> nameof(sd, inner=True, typed=True, full=True)
        'xoutil.names.OrderedDict'

    :param depth: Amount of stack levels to skip if needed.

    '''
    from numbers import Number
    from xoutil.inspect import get_attr_value, type_name
    arg_count = len(args)
    names = [[] for i in range(arg_count)]

    class vars:
        '`nonlocal` simulation'
        params = kwargs
        idx = 0

    def grant(name=None, **again):
        if name:
            names[vars.idx].append(name)
            assert len(names[vars.idx]) < 5
        if again:
            vars.params = dict(kwargs, **again)
        else:
            vars.params = kwargs
            vars.idx += 1

    def param(name, default=False):
        return vars.params.get(name, default)

    while vars.idx < arg_count:
        item = args[vars.idx]
        if param('typed') and not type_name(item):
            item = type(item)
        if param('inner'):
            res = type_name(item)
            if res:
                if param('full'):
                    head = module_name(item)
                    if head:
                        res = '.'.join((head, res))
                grant(res)
            elif isinstance(item, (str_base, Number)):
                grant(str(item))
            else:
                grant('@'.join(('%(next)s', hex(id(item)))), typed=True)
        else:
            import sys
            sf = sys._getframe(param('depth', 1))
            try:
                i, LIMIT, res = 0, 5, _undef
                while not res and sf and (i < LIMIT):
                    key = _key_for_value(sf, item)
                    if key and param('full'):
                        head = _get_value(sf, '__name__')
                        if not head:
                            head = sf.f_code.co_name
                        head = module_name(head)
                        if not head:
                            head = module_name(item) or None
                    else:
                        head = None
                    if key:
                        res = key
                    else:
                        sf = sf.f_back
                        i += 1
            finally:
                # TODO: on "del sf" Python says "SyntaxError: can not delete
                # variable 'sf' referenced in nested scope".
                sf = None
            if res:
                grant('.'.join((head, res)) if head else res)
            else:
                res = type_name(item)
                if res:
                    grant(res)
                else:
                    grant(None, inner=True)
    for i in range(arg_count):
        names[i] = _get_best_name(names[i], safe=param('safe'))
    if arg_count == 0:
        return None
    elif arg_count == 1:
        return names[0]
    else:
        return names


def identifier_from(*args):
    '''Build an valid identifier from the name extracted from an object.

    .. versionadded:: 1.5.5

    First, check if argument is a type and then returns the name of the type
    prefixed with `_` if valid; otherwise calls `nameof` function repeatedly
    until a valid identifier is found using the following order logic:
    ``inner=True``, without arguments looking-up a variable in the calling
    stack, and ``typed=True``.  Returns None if no valid value is found.

    Examples::

        >>> identifier_from({})
        'dict'

    '''
    if len(args) == 1:
        from xoutil.validators.identifiers import is_valid_identifier as valid
        from xoutil.inspect import get_attr_value
        res = None
        if isinstance(args[0], type):
            aux = get_attr_value(args[0], '__name__', None)
            if valid(aux):
                res = str('_%s' % aux)
        if res is None:
            tests = ({'inner': True}, {}, {'typed': True})
            names = (nameof(args[0], depth=2, **test) for test in tests)
            res = next((name for name in names if valid(name)), None)
        return res
    else:
        msg = 'identifier_from() takes exactly 1 argument (%s given)'
        raise TypeError(msg % len(args))


class namelist(list):
    '''Similar to list, but only intended for storing object names.

    Constructors:

    * namelist() -> new empty list
    * namelist(collection) -> new list initialized from collection's items
    * namelist(item, ...) -> new list initialized from severals items

    Instances can be used as decorators to store names of module items
    (functions or classes)::

        >>> __all__ = namelist()
        >>> @__all__
        ... def foobar(*args, **kwargs):
        ...     'Automatically added to this module "__all__" names.'

        >>> 'foobar' in __all__
        True

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(namelist, self).__init__(nameof(arg, depth=2) for arg in args)

    def __add__(self, other):
        other = [nameof(item, depth=2) for item in other]
        return super(namelist, self).__add__(other)

    __iadd__ = __add__

    def __contains__(self, item):
        return super(namelist, self).__contains__(nameof(item, inner=True))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(namelist, self).append(nameof(value, depth=2))
        return value    # What allow to use its instances as a decorator

    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (nameof(item, depth=2) for item in items)
        return super(namelist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(namelist, self).index(nameof(value, depth=2), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(namelist, self).insert(index, nameof(value, depth=2))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, nameof(value, depth=2))


class strlist(list):
    '''Similar to list, but only intended for storing ``str`` instances.

    Constructors:
        * strlist() -> new empty list
        * strlist(collection) -> new list initialized from collection's items
        * strlist(item, ...) -> new list initialized from severals items

    Last versions of Python 2.x has a feature to use unicode as standard
    strings, but some object names can be only ``str``. To be compatible with
    Python 3.x in an easy way, use this list.
    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(strlist, self).__init__(str(arg) for arg in args)

    def __add__(self, other):
        other = [str(item) for item in other]
        return super(strlist, self).__add__(other)

    __iadd__ = __add__

    def __contains__(self, item):
        return super(strlist, self).__contains__(str(item))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(strlist, self).append(str(value))
        return value    # What allow to use its instances as a decorator

    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (str(item) for item in items)
        return super(strlist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(strlist, self).index(str(value), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(strlist, self).insert(index, str(value))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, str(value))
