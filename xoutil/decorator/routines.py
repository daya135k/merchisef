# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator.routines
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-07-21

'''Helpers for co-routines-like patterns.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from .meta import decorator


_predicates = {}


@decorator
def predicate(target, name=None):
    '''Register a predicate for :func:`bounded`.

    A predicate tests a `boundary condition`:term: each time the generator
    passed decorate by `bounded`:func: yields a value.  The decorated function
    in `bounded`:func: is called the bounded generator, and the object
    returned by `bounded`:func: is called the bounded function.

    `target` must a callable that accepts a single positional argument (the
    value passed to its corresponding keyword argument in `bounded`:func:) and
    returns a generator object (:pep:`342`) with the following restrictions
    (collectively called the "predicate protocol"):

    - The predicate is not allowed to stop (raise StopIteration) before
      yielding True (ie. signaling that its boundary condition has been meet),
      or before it's been closed via its ``close()`` method.

    - The predicate will be issued a ``next()`` immediately followed by a
      ``send((args, kwargs))`` when the bounded function is invoked with
      positional arguments ``args`` and keywords-arguments ``kwargs``.  The
      value return by the first ``next()`` is ignored, whereas the value
      returned by the following ``send()`` may be True to signal the up-front
      termination of the bounded function.

    - The predicate will be issued a ``send(value)`` for each value yielded by
      the bounded generator.  Then the predicate must yield back True only
      when the boundary condition has been meet.

      .. note:: Only the value ``True`` signals that the boundary condition
         has been meet and thus the bounded function must return.  Any other
         values indicate that the

    - The predicate will be called its ``close()`` method upon termination.
      Termination happens whenever the bounded function raises StopIteration,
      any of the predicates yield True or an error occurs inside the function
      or predicates.

    See the `timed`:func: predicate for an example.

    '''
    if not name:
        from xoutil.names import nameof
        name = nameof(target, inner=True, depth=2)
    res = _predicates.setdefault(name, target)
    if res is not target:
        raise ValueError('A predicate with the name "%s" has already been'
                         ' registered')
    return target


@predicate
def timed(maxtime):
    '''A soft-timing boundary for :func:`bounded`.

    The bounded generator will be allowed to yields values until the `maxtime`
    timeframe has ellapsed.

    Usage::

         @bounded(timed=timedelta(seconds=60))
         def do_something_in_about_60s():
             while True:
                 yield

    Notice that this is a very soft limit.  We can't actually guarrant any
    enforcement of the time limit.  If the bounded generator takes too much
    time or never yields this predicated can't do much.  This usually helps
    with batch processing that must not exceed (by too much) a given amount of
    time.

    The timer starts just after the ``next()`` function has been called for
    the predicate initialization.  So if the `maxtime` given is too short this
    predicated might halt the execution of the bounded function without
    allowing any processing at all.

    '''
    from datetime import datetime, timedelta
    if isinstance(maxtime, timedelta):
        boundary = maxtime
    else:
        boundary = timedelta(seconds=maxtime)
    start = datetime.now()
    yield False  # XXX: Deal with next-send calling scheme for predicates.
    while datetime.now() - start < boundary:
        yield False
    yield True   # Inform the boundary condition, or we're not compliant with
                 # the predicate protocol.


@predicate
def atmost(cycles):
    '''A predicate that becomes True after a given amount of cycles.'''
    passed = 0
    yield False
    while passed < cycles:
        yield False
        passed += 1
    yield True


@predicate
def pred(func):
    '''Predicate to allow less speciallized callables to engage in the predicate
    protocol.

    Example::

      >>> @bounded(pred=lambda x: True if isinstance(x, int) and x > 10 else False)
      ... def fibonacci():
      ...     a, b = 1, 1
      ...     while True:
      ...        yield a
      ...        a, b = b, a + b

      >>> fibonacci()
      13

    '''
    data = yield False
    while not func(data):
        data = yield False
    yield True


class _higherpred(object):
    def __init__(self, *preds, **namedpreds):
        if not preds and not namedpreds:
            raise TypeError('At least a predicated must be set')
        from types import GeneratorType
        self.preds = predgens = [
            pred if isinstance(pred, GeneratorType) else pred()
            for pred in preds
        ]
        if not all(isinstance(pred, GeneratorType) for pred in predgens):
            raise TypeError('There are invalid (not a generator) unnamed '
                            'predicates.')
        try:
            predgens.extend(
                _predicates[name](val) for name, val in namedpreds.items()
            )
        except KeyError:
            msg = 'unregistered predicated in %r' % namedpreds.keys()
            raise TypeError(msg)


class _whenall(_higherpred):
    def __iter__(self):
        preds = list(self.preds)
        for pred in preds:
            next(pred)
        while preds:  # When we are out of preds it means all have yielded
                      # True
            data = yield False
            i = 0
            while preds and i < len(preds):
                pred = preds[i]
                try:
                    res = pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                except GeneratorExit:
                    i = len(preds)  # fake stop
                else:
                    if res is True:
                        del preds[i]
                    else:
                        i += 1
        yield True
        for pred in self.preds:
            pred.close()


def whenall(*preds, **namedpreds):
    '''An AND-like boundary condition.

    This is a high level predicate.  It takes several predicates and yields
    True only when all the subordinate predicates have yielded True.

    This predicate will raise RuntimeError if any of its subordinate violate
    the predicate protocol.

    This predicate ensures that once a subordinate predicate yields True it
    won't be sent anymore data and its ``close()`` method will be called when
    all the other predicates reach their boundary condition.

    '''
    pred = _whenall(*preds, **namedpreds)
    return iter(pred)


class _whenany(_higherpred):
    def __iter__(self):
        preds = self.preds
        for pred in preds:
            next(pred)
        stop = False
        while not stop:
            data = yield stop
            i, top = 0, len(preds)
            while not stop and i < top:
                pred = preds[i]
                try:
                    stop = stop or pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                except GeneratorExit:
                    stop = True
                else:
                    i += 1
        yield stop
        for pred in preds:
            pred.close()


def whenany(*preds, **namedpreds):
    '''An OR-like boundary condition.

    This is a high level predicate.  It takes several predicates and returns a
    single predicate that behaves like the logical OR, i.e, will yield True
    when **any** of its subordinate predicates yields True.

    This predicate will raise RuntimeError if any of its subordinate violate
    the predicate protocol.

    This is actually the default behavior of `bounded`:func:.  In fact,
    `bounded`:func: calls `whenany`:func: to heavely simplify its
    implementation.

    '''
    pred = _whenany(*preds, **namedpreds)
    return iter(pred)


def bounded(*preds, **namedpreds):
    '''Run a generator in a bounded context.

    The generator yields a unit of work one at a time and the bounded
    decorator may call its ``close()`` method if any of the predicates
    indicated a boundary condition.

    It is advisable not to use too many predicates specially not mixing
    time-related predicated with others.

    The order in which the predicates will be executed is not guarranted.

    If any predicate raises an exception upon initialization, it is propagated
    unchanged and the bounded generator won't stand a chance.  See
    `predicate`:func: for more details about how to write predicates.

    The bounded function returned by this decorator will return the last data
    yielded by the wrapped function, if any was produced.

    .. warning::

       Since `bounded`:func: will consume (and not re-yield) data from the
       wrapped function, you can't nest several calls to `bounded`:func:.

    Each `pred` (unnamed predicate) is simply a generator-iterator that
    complies with the predicate protocol described in `predicate`:func: or a
    callable that evaluates to a predicate.

    Each `namedpred` (nammed predicate) must have been properly registered
    with :func:`predicate`.

    This way you may choose to use named or unnamed as you please.  The
    following signature are equivalent: ``bounded(atmost=8)`` and
    ``bounded(atmost(8))``.

    '''
    pred = whenany(*preds, **namedpreds)

    def bounder(func):
        from functools import wraps

        @wraps(func)
        def target(*args, **kwargs):
            from xoutil import Undefined
            generator = func(*args, **kwargs)
            next(pred)
            stop, data = pred.send((args, kwargs)), Undefined
            try:
                while not stop:
                    try:
                        data = next(generator)
                    except (GeneratorExit, StopIteration):
                        stop = True
                    else:
                        stop = pred.send(data)
            finally:
                generator.close()
                pred.close()
            if data is not Undefined:
                return data
        return target
    return bounder
