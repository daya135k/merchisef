#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.symbols
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-11-18

'''Fixed special logical values like Unset, Ignored, Required, etc...

All values only could be `True` or `False` but are intended in places where
`None` is expected to be a valid value or for special Boolean formats.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from .eight.meta import metaclass

from xoutil.tasking import local


class _local(local):
    def __init__(self):
        super(_local, self).__init__()
        # `weakref.WeakValueDictionary` must be used, but forbidden with slots
        self.instances = {str(v): v for v in (False, True)}

    def nameof(self, s):
        '''Get the name of a symbol instance (`s`).'''
        from xoutil.eight import iteritems
        items = iteritems(self.instances)
        return next((name for name, value in items if value is s), None)

    def __call__(self, name, value):
        '''Get or create a new symbol instance.

        :param name: String representing the internal name.  `symbol`
               instances are unique (singletons) in the context of this
               argument.  ``#`` and spaces are invalid characters to allow
               comments.

        :param value: Any value compatible with Python `bool` (Always is
               converted to this type before using it).  Default is `False`.

        This method is only intended to be called from `__new__` special
        method implementations.

        '''
        cls = boolean if value is False or value is True else symbol
        return cls(name, value)


_symbol = _local()

del local


class MetaSymbol(type):
    '''Meta-class for symbol types.'''
    def __new__(cls, name, bases, ns):
        if name in {'symbol', 'boolean'} and ns['__module__'] == __name__:
            return super(MetaSymbol, cls).__new__(cls, name, bases, ns)
        else:
            msg = 'only classes declared in "{}" module are allowed'
            raise TypeError(msg.format(__name__))

    def __instancecheck__(self, instance):
        '''Override for isinstance(instance, self).'''
        if instance is False or instance is True:
            return True
        else:
            return super(MetaSymbol, self).__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        '''Override for issubclass(subclass, self).'''
        if subclass is bool:
            return True
        else:
            return super(MetaSymbol, self).__subclasscheck__(subclass)

    def parse(self, name):
        '''Returns instance from a string.

        Standard Python Boolean values are parsed too.

        '''
        if '#' in name:    # Remove comment
            name = name.split('#')[0].strip()
        res = _symbol.instances.get(name, None)
        if res is not None:
            if isinstance(res, self):
                return res
            else:
                msg = 'invalid parsed value "{}" of type "{}"; must be "{}"'
                rtn, sn = type(res).__name__, self.__name__
                raise TypeError(msg.format(res, rtn, sn))
        else:
            msg = 'name "{}" is not defined'
            raise NameError(msg.format(name))


class symbol(metaclass(MetaSymbol), int):
    '''Instances are custom symbols.

    See :meth:`~MetaSymbol.__getitem__` operator for information on
    constructor arguments.

    For example::

      >>> ONE2MANY = symbol('ONE2MANY')
      >>> ONE_TO_MANY = symbol('ONE2MANY')

      >>> ONE_TO_MANY ONE2MANY
      True

    '''
    __slots__ = ()

    def __new__(cls, name, value=None):
        '''Get or create a new symbol instance.

        :param name: String representing the internal name.  `Symbol`:class:
               instances are unique (singletons) in the context of this
               argument.  ``#`` and spaces are invalid characters to allow
               comments.

        :param value: Any value compatible with Python `bool` or `int` types.
               `None` is used as a special value to create a value using the
               name hash.

        '''
        from .eight import intern as unique
        name = unique(name)
        if name:
            instances = _symbol.instances
            res = instances.get(name)
            if res is None:    # Create the new instance
                if value is None:
                    value = hash(name)
                valid = {symbol: lambda v: isinstance(v, int),
                         boolean: lambda v: v is False or v is True}
                if not valid[cls](value):
                    msg = ('instancing "{}" with name "{}" and incorrect '
                           'value "{}" of type "{}"')
                    cn, vt = cls.__name__, type(value).__name__
                    raise TypeError(msg.format(cn, name, value, vt))
                res = super(symbol, cls).__new__(cls, value)
                instances[name] = res
            elif res != value:    # Check existing instance
                msg = 'value "{}" mismatch for existing instance: "%s"'
                raise ValueError(msg.format(value, name))
            return res
        else:
            raise ValueError('name must be a valid non empty string')

    def __init__(self, *args, **kwds):
        pass

    def __repr__(self):
        return _symbol.nameof(self)

    __str__ = __repr__


class boolean(symbol):
    '''Instances are custom logical values (`True` or `False`).

    See :meth:`~MetaSymbol.__getitem__` operator for information on
    constructor arguments.

    For example::

      >>> true = boolean('true', True)
      >>> false = boolean('false')
      >>> none = boolean('false')
      >>> unset = boolean('unset')

      >>> class X(object):
      ...      attr = None

      >>> getattr(X(), 'attr') is not None
      False

      >>> getattr(X(), 'attr', false) is not false
      True

      >>> none is false
      True

      >>> false == False
      True

      >>> false == unset
      True

      >>> false is unset
      False

      >>> true == True
      True

    '''
    __slots__ = ()

    def __new__(cls, name, value=False):
        '''Get or create a new symbol instance.

        See `~Symbol.__new__`:meth: for information about parameters.
        '''
        return super(boolean, cls).__new__(cls, name, bool(value))


del metaclass
