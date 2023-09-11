# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.data
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2009-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Some useful Data Structures and data-related algorithms and functions.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_absimports)


def sync(source, target, keys=None):
    '''Copies attributes, or (key, value) items, from `source` to `target`.

    :param source: The object or mapping to extract source items.

    :param target: The object or mapping to settle destination items.

    Names starting with an '_' will not be copied unless `full` is True.

    When `target` is not a dictionary (other Python objects):

        - Only valid identifiers will be copied.

        - If `full` is False only public values (which name does not starts
          with '_') will be copied.

    Assumed introspections:

        - `source` is considered a dictionary when it has a method called
          ``iteritem`` or ``items``.

        - `target` is considered a dictionary when: ``isinstance(target,
          collections.Mapping)`` is True.

    '''

def smart_copy(source, target, full=False):
    '''Copies attributes (or keys) from `source` to `target`.

    Names starting with an '_' will not be copied unless `full` is True.

    When `target` is not a dictionary (other Python objects):

        - Only valid identifiers will be copied.

        - If `full` is False only public values (which name does not starts
          with '_') will be copied.

    Assumed introspections:

        - `source` is considered a dictionary when it has a method called
          ``iteritem`` or ``items``.

        - `target` is considered a dictionary when: ``isinstance(target,
          collections.Mapping)`` is True.

    '''
    from collections import Mapping
    from xoutil.validators.identifiers import is_valid_identifier
    if callable(getattr(source, 'iteritems', None)):
        items = source.iteritems()
    elif callable(getattr(source, 'items', None)):
        items = source.items()
    else:
        items = ((name, getattr(source, name)) for name in dir(source))
    if isinstance(target, Mapping):
        def setvalue(key, value):
            target[key] = value
    else:
        def setvalue(key, value):
            if is_valid_identifier(key) and (full or not key.startswith('_')):
                setattr(target, key, value)
    for key, value in items:
        setvalue(key, value)


# TODO: Cuando se pone el deprecated como esto tiene un __new__ se entra en un
# ciclo infinito

#@deprecated('collections.namedtuple')
class MappedTuple(tuple):
    '''An implementation of a named tuple.

    Deprecated since the introduction of namedtuple in Python 2.6

    '''
    def __new__(cls, key_attr='key', sequence=()):
        import warnings
        warnings.warn('MappedTuple is deprecated, you should use '
                      'collections.namedtuple', stacklevel=1)
        self = super(MappedTuple, cls).__new__(cls, sequence)
        self.mapping = {getattr(item, key_attr): i
                          for i, item in enumerate(sequence)}
        return self

    def __getitem__(self, key):
        from numbers import Integral
        if not isinstance(key, Integral):
            key = self.mapping[key]
        return super(MappedTuple, self).__getitem__(key)

    def get(self, key, default=None):
        from numbers import Integral
        if not isinstance(key, Integral):
            key = self.mapping.get(key, None)
        if (key is not None) and (key >= 0) and (key < len(self)):
            return super(MappedTuple, self).__getitem__(key)
        else:
            return default


class SmartDict(dict):
    '''A "smart" dictionary that can receive a wide variety of arguments.

    Creates a dictionary from a set of iterable arguments and keyword values
    (kwargs). Each arg can be:

        - another dictionary.

        - an iterable of (key, value) pairs.

        - any object implementing "keys()" and "__getitem__(key)" methods.

    '''

    def __init__(self, *args, **kwargs):
        super(SmartDict, self).__init__()
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        '''Update this dict from a set of iterables `args` and keyword values
        `kwargs`.
        '''
        from types import GeneratorType
        from collections import Mapping
        from xoutil.types import is_iterable
        for arg in args:
            if isinstance(arg, Mapping):
                self._update(arg.items())
            elif isinstance(arg, (tuple, list)):
                self._update(arg)
            elif isinstance(arg, GeneratorType):
                self._update(arg)
            elif hasattr(arg, 'keys') and hasattr(arg, '__getitem__'):
                from xoutil.iterators import fake_dict_iteritems
                self._update(fake_dict_iteritems(arg))
            elif is_iterable(arg):
                self._update(iter(arg))
            else:
                msg = ('cannot convert dictionary update sequence element '
                       '"%s" to a (key, value) pair iterator') % arg
                raise TypeError(msg)
        if kwargs:
            self.update(kwargs)

    def _update(self, items):
        '''For legacy compatibility.'''
        super(SmartDict, self).update(items)


class SortedSmartDict(SmartDict):
    '''A dictionary that keeps its keys in the order in which they're inserted.

    Creating or updating a sorted dict with more than one kwargs is
    counterproductive because the order of this kind of argument is not kept
    by python, any way you can use it once a time like in ``d.update(x=1)``.

    .. warning:: Currently this uses :class:`SmartDict` as base, it's has
                 being proposed that we should use the
                 ``collections.OrderedDict`` from the standard library.

                 But since the :meth:`SmartDict.update` is not equivalent to
                 the ``update`` of dictionaries, and this module has no
                 tests, we're defering such a change for a release post
                 |release|.

    '''
    # TODO: Deprecate this by "collections.OrderedDict" in python2.7

    def __new__(cls, *args, **kwargs):
        self = super(SortedSmartDict, cls).__new__(cls, *args, **kwargs)
        self._keys = []
        return self

    def __repr__(self):
        if not hasattr(self, '_recursion'):
            self._recursion = True
            res = '{%s}' % ', '.join(['%r: %r' % (k, v)
                                        for k, v in self.iteritems()])
            del self._recursion
            return res
        else:
            return '<Recursion on SortedDict with id=%s>' % id(self)

    def __getitem__(self, key):
        _get = super(SortedSmartDict, self).__getitem__
        if isinstance(key, slice):
            keys = self._keys.__getitem__(key)
            return map(_get, keys)
        else:
            return _get(key)

    def __setitem__(self, key, value):
        _set = super(SortedSmartDict, self).__setitem__
        if isinstance(key, slice):
            keys = self._keys.__getitem__(key)
            values = tuple(value)
            if len(keys) == len(values):
                self._update(zip(keys, values))
            else:
                msg = ('trying to replace a slice of "%s" items with "%s" '
                       'values.') % (len(keys), len(values))
                raise ValueError(msg)
        else:
            if key not in self:
                self._keys.append(key)
            _set(key, value)

    def __delitem__(self, key):
        _del = super(SortedSmartDict, self).__delitem__
        if isinstance(key, slice):
            keys = self._keys.__getitem__(key)
            self._keys.__delitem__(key)
        else:
            keys = (key,)
            self._keys.remove(key)
        for key in keys:
            _del(key)

    def __iter__(self):
        return iter(self._keys)

    def items(self):
        return self.items()

    def iteritems(self):
        for key in self._keys:
            yield key, self[key]

    def keys(self):
        return self._keys[:]

    def iterkeys(self):
        return iter(self._keys)

    def values(self):
        return map(super(SortedSmartDict, self).__getitem__, self._keys)

    def itervalues(self):
        for key in self._keys:
            yield self[key]

    def pop(self, key, *args):
        remove = key in self
        result = super(SortedSmartDict, self).pop(key, *args)
        if remove:
            self._keys.remove(key)
        return result

    def popitem(self):
        if len(self._keys) == 0:    # ;)
            return super(SortedSmartDict, self).popitem()
        else:
            key = self._keys[-1]
            return key, self.pop(key)

    def setdefault(self, key, default):
        if key not in self:
            self._keys.append(key)
        return super(SortedSmartDict, self).setdefault(key, default)

    def value_for_index(self, index):
        '''Returns the value of the item at the given zero-based index.'''
        return self[self._keys[index]]

    def insert(self, index, key, value):
        '''Inserts (key, value) pair before the item with the given index.'''
        if key in self:
            n = self._keys.index(key)
            del self._keys[n]
            if n < index:
                index -= 1
        self._keys.insert(index, key)
        super(SortedSmartDict, self).__setitem__(key, value)

    def copy(self):
        '''Returns a copy of this object.'''
        return type(self)(self)

    def clear(self):
        super(SortedSmartDict, self).clear()
        self._keys = []

    def _update(self, items):
        for key, value in items:
            self[key] = value


class IntSet(object):
    '''Like a Python 'set' but only accepting integers saving a lot of space.

    Constructor is smart, you can give:
     * integers
     * any iterable of integers
     * strings using the pattern ''. For example:
       - '1..5, 6, 10-20'

    Not yet implemented.
    '''

    def __init__(self, *args):
        '''
        Not yet implemented.
        '''
        # TODO: Implement this
        raise NotImplementedError
