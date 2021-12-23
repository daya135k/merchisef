#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop
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
# Created on Mar 23, 2012

'''
Very simple AOP implementation allowing method replacing in objects with change
function, reset an object to its original state and user a special super
function inner new functions used to inject the new behavior.

Aspect-oriented programming (AOP) increase modularity by allowing the separation
of cross-cutting concerns.

An aspect can alter the behavior of the base code (the non-aspect part of a
program) by applying advice (additional behavior) at various join-points (points
in a program) specified in a quantification or query called a point-cut (that
detects whether a given join point matches).

An aspect can also make structural changes to other classes, like adding members
or parents.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from contextlib import contextmanager

__docstring_format__ = 'rst'
__author__ = 'Medardo Rodriguez'


def inject_methods(target, *sources, **named_functions):
    'Injects/replaces the sources for the given target.'
    cls = target if isinstance(target, type) else target.__class__
    _merchise_extended = cls.__dict__.get('_merchise_extended', {'depth': 0}).copy()
    _merchise_extended['depth'] += 1
    attrs = {b'__doc__': cls.__doc__, b'__module__': b'merchise.builtin',
             '_merchise_extended': _merchise_extended}
    attrs.update(named_functions)
    attrs.update({f.__name__: f for f in sources})
    extended_class = type(cls.__name__, (cls, ), attrs)
    if not isinstance(target, type):
        try:
            target.__class__ = extended_class
        except:
            class wrapper(target.__class__):
                pass
            target = wrapper(target)
            target.__class__ = extended_class
        result = target
    else:
        result = extended_class
    return result


@contextmanager
def weaved(target, *sources, **named_functions):
    '''
    Returns a context manager that weaves :param:`target` with all the
    :param:`sources` and the :param:`named_functions` weaved into it. This
    method yields the weaved object into the context manager, so you have
    access to it. Upon exiting the context manager, the :param:`target` is
    reset to it's previous state (if possible).
    
    For example, in the following code::

        >>> class Test(object):
        ...    def f(self, n):
        ...        return n
        
        >>> test = Test()


    You may want to record each call to ``f`` on the ``test`` object::

        >>> def f(self, n):
        ...     print('Log this')
        ...     return super(_ec, self).f(n) # Notice below the assignment to _ec

        >>> with weaved(test, f) as test:
        ...    _ec = test.__class__ # Needed
        ...    test.f(10)
        Log this
        10
        
    But once you leave the context, ``test`` will stop logging::
    
        >>> test.f(10)
        10
        
    You may nest several calls to this:
        
        >>> def f2(self, n):
        ...    print('Done it')
        ...    return super(_ec2, self).f(n)
        
        >>> with weaved(test, f) as test:
        ...    _ec = test.__class__
        ...    with weaved(test, f=f2) as test:
        ...        _ec2 = test.__class__
        ...        test.f(10)
        ...    test.f(12)
        Done it
        Log this
        10
        Log this
        12
        
        >>> test.f(10)
        10
        
    '''
    try:
        result = inject_methods(target, *sources, **named_functions)
        yield result
    finally:
        if result is target:
            cls = target.__class__
            res = 0
            depth = 0
            while depth == 0 and cls.__dict__.get('_merchise_extended'):
                depth = cls.__dict__.get('_merchise_extended', {}).get('depth', 0)
                cls = cls.__base__
                res += 1
            if res > 0:
                target.__class__ = cls


#@contextmanager
#def weaved_with_super(target, *sources, **named_functions):
#    from itertools import chain
#    weaves = {}
#    for name, func in chain(((f.__name__, f) for f in sources), named_functions.items()):
#        _super = func
#        def inner(*args, **kw):
#            return func(*args, **kw)
#    