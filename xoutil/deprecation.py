#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.deprecation
#----------------------------------------------------------------------
# Copyright (c) 2012, 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 15, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import types
import warnings

from functools import wraps
from xoutil.compat import class_types as _class_types

__docstring_format__ = 'rst'
__author__ = 'manu'


DEFAULT_MSG = ('{funcname} is now deprecated and it will be removed. ' +
              'Use {replacement} instead.')

# XXX: Don't make deprecated depends upon anything more than compat and
# decorator.py. Since this is meant to be used by all others xoutil modules.
def deprecated(replacement, msg=DEFAULT_MSG, deprecated_module=None):
    '''Small decorator for deprecated functions.

    Usage::

        @deprecate(new_function)
        def deprecated_function(...):
            ...

    .. note::

       There's a package `zope.deferredimport` that has a `deprecated` function
       that injects same implementations of some object into a module, with
       a deprecation warning.

       The main difference is that we don't require the same implementation
       and/or interface. We may deprecate a feature to be removed by another
       that has not the same interface.

       For instance :class:`xoutil.memoize.simple_memoize` decorator is
       deprecated in favor of :func:`xoutil.functools.lru_cache` but they
       don't share the same interface.

       However `zope.deferredimport` allows also for deferred imports (without
       deprecation), and are very useful if you need to keep names for other
       stuff around without loading them until they are used.
    '''
    def decorator(target):
        if deprecated_module:
            funcname = deprecated_module + '.' + target.__name__
        else:
            funcname = target.__name__
        if isinstance(replacement, _class_types + (types.FunctionType, )):
            repl_name = replacement.__module__ + '.' + replacement.__name__
        else:
            repl_name = replacement
        if isinstance(target, _class_types):
            def new(*args, **kwargs):
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name),
                              stacklevel=2)
                return target.__new__(*args, **kwargs)
            # Code copied and adapted from xoutil.objects.copy_class. This is
            # done so because this module *must* not depends on any other,
            # otherwise an import cycle might be formed when deprecating a
            # class in xoutil.objects.
            from xoutil.compat import iteritems_
            from xoutil.types import MemberDescriptorType
            meta = type(target)
            attrs = {name: value
                     for name, value in iteritems_(target.__dict__)
                     if name not in ('__class__', '__mro__', '__name__', '__weakref__', '__dict__')
                     # Must remove member descriptors, otherwise the old's class
                     # descriptor will override those that must be created here.
                     if not isinstance(value, MemberDescriptorType)}
            attrs.update(__new__=new)
            result = meta(target.__name__, target.__bases__, attrs)
            return result
        else:
            @wraps(target)
            def inner(*args, **kw):
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name),
                              stacklevel=2)
                return target(*args, **kw)
            return inner
    return decorator


def inject_deprecated(funcnames, source, target=None):
    '''
    Takes a sequence of function names `funcnames` which reside in the `source`
    module and injects them into `target` marked as deprecated. If `target` is
    None then we inject the functions into the locals of the calling code. It's
    expected it's a module.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.
    '''
    if not target:
        import sys
        frame = sys._getframe(1)
        try:
            target_locals = frame.f_locals
        finally:
            # As recommended to avoid memory leaks
            del frame
    else:
        pass
    for targetname in funcnames:
        unset = object()
        target = getattr(source, targetname, unset)
        if target is not unset:
            if isinstance(target, (types.FunctionType, types.LambdaType) + _class_types):
                replacement = source.__name__ + '.' + targetname
                module_name = target_locals.get('__name__', None)
                target_locals[targetname] = deprecated(replacement,
                                                       DEFAULT_MSG,
                                                       module_name)(target)
            else:
                target_locals[targetname] = target
        else:
            warnings.warn('{targetname} was expected to be in {source}'.
                          format(targetname=targetname,
                                 source=source.__name__), stacklevel=2)
