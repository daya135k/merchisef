#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.fp.prove
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2016-08-31

'''Prove validity of values.

There are a family of checker functions:

- `validate`:func: raises an exception on failure, this is useful to call
  functions that use "special" false values to signal a failure.

- `affirm`:func: returns a false value on failure, this is useful to call
  functions that could raise an exception to signal a failure.

- `safe`:func: creates a decorator to convert a function to use either the
  `validate`:func: or the `affirm`:func: protocol.

A `Coercer`:class: is a concept that combine two elements: validity check and
value moulding.  Most times only the first part is needed because the original
value is in the correct shape if valid.

It's usual to declare functions or methods with generic prototypes::

  def func(*args, **kwds):
      ...

.. versionadded:: 1.7.2

.. versionchanged:: 1.8.0 Migrated from 'xoutil.params'

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def validate(function, *args, **kwds):
    '''Call a `function` inner a safety wrapper raising an exception if fail.

    Fails could be signaled with special false values such as:

    - Any `~xoutil.fp.monads.option.Wrong`:class: instance; or

    - Any false value provable as instance of
      `~xoutil.symbols.boolean`:class:, that doesn't include values as ``0``,
      ``[]``, or ``None``.

    '''
    from xoutil import Ignored
    from xoutil.symbols import boolean
    from xoutil.future.string import small
    from xoutil.eight import type_name
    from xoutil.eight.exceptions import throw
    from xoutil.fp.monads.option import Just, Wrong
    from xoutil.fp.params import singleton
    res = function(*args, **kwds)
    if isinstance(res, boolean):
        if res:
            aux = singleton(*args, **kwds)
            if aux is not Ignored:
                res = aux
        else:
            msg = '{}() validates as false'.format(small(function))
            raise TypeError(msg)
    elif isinstance(res, Wrong):
        inner = res.inner
        if isinstance(inner, BaseException):
            throw(inner)
        else:
            msg = '{}() validates as a wrong value'.format(small(function))
            if inner is not None or not isinstance(inner, boolean):
                v, t = small(inner), type_name(inner)
                msg += ' {} of type "{}"'.format(v, t)
            raise TypeError(msg)
    elif isinstance(res, Just):
        res = res.inner
    return res


def affirm(function, *args, **kwds):
    '''Call a `function` inner a safety wrapper returning false if fail.

    This converts any function in a predicate.  A predicate can be thought as
    an operator or function that returns a value that is either true or false.
    Predicates are sometimes used to indicate set membership: sometimes it is
    inconvenient or impossible to describe a set by listing all of its
    elements.  Thus, a predicate ``P(x)`` will be true or false, depending on
    whether x belongs to a set.

    If `function` validates its arguments, return a valid true value, could be
    Always returns an instance of `~xoutil.fp.monads.option.Maybe`:class: or a
    Boolean value.

    '''
    from xoutil.symbols import boolean
    from xoutil.fp.monads.option import Maybe, Just, Wrong
    try:
        res = function(*args, **kwds)
        if isinstance(res, (boolean, Maybe)):
            if isinstance(res, Just) and res.inner:
                return res.inner
            elif isinstance(res, boolean) and len(args) == 1 and not kwds and args[0]:
                return args
            return res
        elif res:
            return res
        else:
            return Just(res)
    except BaseException as error:
        if isinstance(error, ValueError) and len(args) == 1 and not kwds:
            return Wrong(args[0])
        else:
            return Wrong(error)


def safe(checker):
    '''Create a decorator to execute a function inner a safety wrapper.

    :param checker: Could be any function safe wrapper, but it's intended
           mainly for `affirm`:func: or `validate`:func:.

    In the following example, the semantics of this function can be seen.  The
    definition::

        >>> @safe(validate)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(5)
        5

    It is equivalent to::

        >>> def test(x):
        ...     return 1 <= x <= 10

        >>> validate(test, 5)
        5

    In other hand::

        >>> @safe(validate)
        ... def test(x):
        ...     return 1 <= x <= 10

        >>> test(15)
        5

    '''
    def wrapper(func):
        from xoutil.future.string import small, safe_str

        def inner(*args, **kwds):
            return checker(func, *args, **kwds)

        try:
            inner.__name__ = func.__name__
            inner.__doc__ = func.__doc__
        except BaseException:
            inner.__name__ = safe_str(small(func))
        return inner
    return wrapper


class Coercer(object):
    '''Wrapper for value-coercing definitions.

    A coercer combine check for validity and value mould (casting).  Could be
    defined from a type (or tuple of types), a callable or a list containing
    two parts with both concepts.

    To signal that value as invalid, a coercer must return the special value
    `_wrong`.  Types work as in `isinstance`:func: standard function; callable
    functions mould a parameter value into a definitive form.

    To use normal functions as a callable coercer, use `SafeCheck`:class: or
    `LogicalCheck`:class` to wrap them.

    When using a list to combine explicitly the two concepts, result of the
    check part is considered Boolean (True or False), and the second part
    alwasy return a moulded value.

    When use a coercer, several definitions will be tried until one succeed.

    '''
    __slots__ = ('inner',)

    def __new__(cls, *args):
        from xoutil.eight import class_types, callable, type_name
        if cls is Coercer:    # Parse the right sub-type
            count = len(args)
            if count == 0:
                msg = '{}() takes at least 1 argument (0 given)'
                raise TypeError(msg.format(cls.__name__))
            elif count == 1:
                arg = args[0]
                if isinstance(arg, cls):
                    return arg
                elif isinstance(arg, class_types + (tuple,)):
                    return TypeCheck(arg)
                elif isinstance(arg, list):
                    return CheckAndCast(*arg)
                elif callable(arg):
                    return LogicalCheck(arg)
                else:
                    msg = "{}() can't parse a definition of type: {}"
                    raise TypeError(msg.format(cls.__name__, type_name(arg)))
            else:
                return MultiCheck(*args)
        else:
            return super(Coercer, cls).__new__(cls)

    def __init__(self, *args):
        pass

    def __repr__(self):
        return str(self)


class TypeCheck(Coercer):
    '''Check if value is instance of given types.'''
    __slots__ = ()

    def __new__(cls, *args):
        from xoutil.eight import class_types as _types, type_name
        from xoutil.fp.params import check_count
        check_count(len(args) + 1, 2, caller=cls.__name__)
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        if all(isinstance(arg, _types) for arg in args):
            self = super(TypeCheck, cls).__new__(cls)
            self.inner = args
            return self
        else:
            wrong = (arg for arg in args if not isinstance(arg, _types))
            wnames = ', or '.join(type_name(w) for w in wrong)
            msg = '`TypeCheck` allows only valid types, not: ({})'
            raise TypeError(msg.format(wnames))

    def __call__(self, value):
        from xoutil.fp.monads.option import Just, Wrong
        ok = isinstance(value, self.inner)
        return (value if value else Just(value)) if ok else Wrong(value)

    def __str__(self):
        return self._str()

    def __crop__(self):
        from xoutil.future.string import DEFAULT_MAX_WIDTH
        return self._str(DEFAULT_MAX_WIDTH)

    def _str(self, max_width=None):
        '''Calculate both string versions (small and normal).'''
        from xoutil import Undefined
        from xoutil.eight import type_name
        from xoutil.future.string import ELLIPSIS
        if max_width is None:
            max_width = 1024    # a big number for this
        start, end = '{}('.format(type_name(self)), ')'
        borders_len = len(start) + len(end)
        sep = ', '
        res = ''
        items = iter(self.inner)
        ok = True
        while ok:
            item = next(items, Undefined)
            if item is not Undefined:
                if res:
                    res += sep
                aux = item.__name__
                if len(res) + len(aux) + borders_len <= max_width:
                    res += aux
                else:
                    res += ELLIPSIS
                    ok = False
            else:
                ok = False
        return '{}{}{}'.format(start, res, end)


class NoneOrTypeCheck(TypeCheck):
    '''Check if value is None or instance of given types.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.monads.option import Wrong
        if value is None:
            _types = self.inner
            i, res = 0, None
            while res is None and i < len(_types):
                try:
                    res = _types[i]()
                except BaseException:
                    pass
                i += 1
            return res if res is not None else Wrong(None)
        else:
            return super(NoneOrTypeCheck, self).__call__(value)

    def __str__(self):
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class TypeCast(TypeCheck):
    '''Cast a value to a correct type.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.monads.option import Just
        res = super(TypeCast, self).__call__(value)
        if not res:
            _types = self.inner
            i = 0
            while not res and i < len(_types):
                try:
                    res = _types[i](value)
                    if not res:
                        res = Just(res)
                except BaseException:
                    pass
                i += 1
        return res

    def __str__(self):
        # FIX: change this
        aux = super(NoneOrTypeCheck, self).__str__()
        return 'none-or-{}'.format(aux)


class CheckAndCast(Coercer):
    '''Check if value, if valid cast it.

    Result value must be valid also.
    '''
    __slots__ = ()

    def __new__(cls, check, cast):
        from xoutil.eight import callable, type_name
        check = Coercer(check)
        if callable(cast):
            self = super(CheckAndCast, cls).__new__(cls)
            self.inner = (check, SafeCheck(cast))
            return self
        else:
            msg = '{}() expects a callable for cast, "{}" given'
            raise TypeError(msg.format(type_name(self), type_name(cast)))

    def __call__(self, value):
        from xoutil.fp.monads.option import Wrong
        check, cast = self.inner
        aux = check(value)
        if aux:
            res = cast(value)
            if check(res):
                return res
        else:
            res = aux
        if isinstance(res, Wrong):
            return res
        else:
            return Wrong(value)

    def __str__(self):
        from xoutil.future.string import crop
        check, cast = self.inner
        fmt = '({}(…) if {}(…) else _wrong)'
        return fmt.format(crop(cast), check)


class FunctionalCheck(Coercer):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __new__(cls, check):
        from xoutil.eight import callable, type_name
        # TODO: Change next, don't use isinstance
        if isinstance(check, Coercer):
            return check
        elif callable(check):
            self = super(FunctionalCheck, cls).__new__(cls)
            self.inner = check
            return self
        else:
            msg = 'a functional check expects a callable but "{}" is given'
            raise TypeError(msg.format(type_name(check)))

    def __str__(self):
        from xoutil.eight import type_name
        from xoutil.future.string import crop
        suffix = 'check'
        kind = type_name(self).lower()
        if kind.endswith(suffix):
            kind = kind[:-len(suffix)]
        inner = crop(self.inner)
        return '{}({})()'.format(kind, inner)


class LogicalCheck(FunctionalCheck):
    '''Check if value is valid with a callable function.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.monads.option import Just, Wrong
        try:
            res = self.inner(value)
            if res:
                if isinstance(res, Just):
                    return res
                elif res is True:
                    return Just(value)
                else:
                    return res
            elif isinstance(res, Wrong):
                return res
            elif res is False or res is None:    # XXX: None?
                return Wrong(value)
            else:
                return Wrong(res)
        except BaseException as error:
            return Wrong(error)


class SafeCheck(FunctionalCheck):
    '''Return a wrong value only if function produce an exception.'''
    __slots__ = ()

    def __call__(self, value):
        from xoutil.fp.monads.option import Wrong
        try:
            return self.inner(value)
        except BaseException as error:
            return Wrong(error)


class MultiCheck(Coercer):
    '''Return a wrong value only when all inner coercers fails.

    Haskell: guards (pp. 132)

    '''
    __slots__ = ()

    def __new__(cls, *args):
        inner = tuple(Coercer(arg) for arg in args)
        self = super(MultiCheck, cls).__new__(cls)
        self.inner = inner
        return self

    def __call__(self, value):
        from xoutil.fp.monads.option import Just, Wrong, none
        coercers = self.inner
        i, res = 0, none
        while isinstance(res, Wrong) and i < len(coercers):
            res = coercers[i](value)
            i += 1
        return res.inner if isinstance(res, Just) and res.inner else res

    def __str__(self):
        aux = ' OR '.join(str(c) for c in self.inner)
        return 'combo({})'.format(aux)
