#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.deprecation
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# Copyright (c) 2012 Medardo Rodriguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 15, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import types
import warnings

from functools import wraps


# TODO: Invalidate this module in favor of new 'xoutil.hints' when implemented

DEFAULT_MSG = ('{funcname} is now deprecated and it will be '
               'removed{in_version}. Use {replacement} instead.')


class DeprecationError(Exception):
    pass


# TODO: Use ``warnings.simplefilter('default', DeprecationWarning)``


def _nameof(item):
    '''Version of `xoutil.names.nameof`:func: to avoid importing it here.'''
    singletons = (None, True, False, Ellipsis, NotImplemented)
    res = next((str(s) for s in singletons if s is item), None)
    if res is None:
        res = '.'.join([item.__module__, item.__name__])
    return res


def deprecated(replacement, msg=DEFAULT_MSG, deprecated_module=None,
               removed_in_version=None, check_version=False):
    '''Small decorator for deprecated functions.

    Usage::

        @deprecate(new_function)
        def deprecated_function(...):
            ...

    :param replacement: Either a string or the object that replaces the
       deprecated.

    :param msg: A deprecation warning message template.  You should provide
       keyword arguments for the `format`:func: function.  Currently we pass
       the current keyword arguments: `replacement` (after some processing),
       `funcname` with the name of the currently deprecated object and
       `in_version` with the version this object is going to be removed if
       `removed_in_version` argument is not None.

       Defaults to: "{funcname} is now deprecated and it will be
       removed{in_version}. Use {replacement} instead."

    :param removed_in_version: The version the deprecated object is going to be
       removed.

    :param check_version: If True and `removed_in_version` is not None, then
       declarations of obseleted objects will raise a DeprecationError. This
       helps the release manager to keep the release clean.

       .. note:: Currently only works with setuptools' installed distributions.

    :param deprecated_module: If provided, the name of the module the
       deprecated object resides. Not needed if the deprecated object is a
       function or class.

    .. versionchanged:: 1.4.1 Introduces removed_in_version and check_version.

    '''

    def raise_if_deprecated(target, target_version):
        import sys
        import pkg_resources
        string_types = (str,) if sys.version_info[0] == 3 else (basestring,)
        pkg = _nameof(target)
        pkg, _obj = pkg.rsplit('.', 1)
        dist = None
        while not dist and pkg:
            try:
                dist = pkg_resources.get_distribution(pkg)
            except pkg_resources.DistributionNotFound:
                dist = None
                if '.' in pkg:
                    pkg, _obj = pkg.rsplit('.', 1)
                else:
                    pkg, _obj = None, None    # noqa
        assert dist
        if isinstance(target_version, string_types):
            target_version = pkg_resources.parse_version(target_version)
        if dist.parsed_version >= target_version:
            msg = ('A deprecated feature %r was scheduled to be '
                   'removed in version %r and it is still '
                   'alive in %r!' % (_nameof(target),
                                     str(removed_in_version),
                                     str(dist.version)))
            raise DeprecationError(msg)

    def decorator(target):
        from xoutil.eight import class_types
        if deprecated_module:
            funcname = deprecated_module + '.' + target.__name__
        else:
            funcname = target.__name__
        if isinstance(replacement, class_types + (types.FunctionType, )):
            repl_name = replacement.__module__ + '.' + replacement.__name__
        else:
            repl_name = replacement
        if removed_in_version:
            in_version = ' in version ' + removed_in_version
        else:
            in_version = ''
        if isinstance(target, class_types):
            def new(*args, **kwargs):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name,
                                         in_version=in_version),
                              stacklevel=2)
                return target.__new__(*args, **kwargs)
            # Code copied and adapted from xoutil.objects.copy_class. This is
            # done so because this module *must* not depends on any other,
            # otherwise an import cycle might be formed when deprecating a
            # class in xoutil.objects.
            import sys
            from xoutil.future.types import MemberDescriptorType
            meta = type(target)
            _py3 = sys.version_info[0] == 3
            td = target.__dict__
            iteritems = td.items if _py3 else td.iteritems
            attrs = {name: value
                     for name, value in iteritems()
                     if name not in ('__class__', '__mro__',
                                     '__name__', '__weakref__', '__dict__')
                     # Must remove member descriptors, otherwise the old's
                     # class descriptor will override those that must be
                     # created here.
                     if not isinstance(value, MemberDescriptorType)}
            attrs.update(__new__=new)
            result = meta(target.__name__, target.__bases__, attrs)
            return result
        else:
            @wraps(target)
            def inner(*args, **kw):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name,
                                         in_version=in_version),
                              stacklevel=2)
                return target(*args, **kw)
            return inner
    return decorator


def inject_deprecated(funcnames, source, target=None):
    '''Takes a sequence of function names `funcnames` which reside in the
    `source` module and injects them into `target` marked as deprecated. If
    `target` is None then we inject the functions into the locals of the
    calling code. It's expected it's a module.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.
    '''
    from xoutil.eight import class_types
    if not target:
        import sys
        frame = sys._getframe(1)
        try:
            target_locals = frame.f_locals
        finally:
            # As recommended to avoid memory leaks
            del frame
    else:
        # FIX: @manu, there is a consistency error here, 'target_locals' is
        # never assigned
        pass
    for targetname in funcnames:
        unset = object()
        target = getattr(source, targetname, unset)
        if target is not unset:
            testclasses = (types.FunctionType, types.LambdaType) + class_types
            if isinstance(target, testclasses):
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


def import_deprecated(module, *names, **aliases):
    '''Import functions deprecating them in the target module.

    The target module is the caller of this function (only intended to be
    called in the global part of a module).

    :param module: The module from which functions will be imported.  Could be
           a string, or an imported module.

    :param names: The names of the functions to import.

    :param aliases: Keys are the new names, values the old names.

    :returns: The target module.

    For example::

      >>> from xoutil.deprecation import import_deprecated
      >>> import math
      >>> this = import_deprecated(math, 'sin', new_cos='cos')
      >>> sin is this.sin
      True
      >>> sin is not math.sin
      True

    Next examples are all ``True``, but them print the deprecation warning
    when executed::

      >>> sin(math.pi/2) == math.sin(math.pi/2) == 1.0
      >>> new_cos(2*math.pi)

    If no identifier is given, it is assumed equivalent as ``from module
    import *``.

    The statement ``import_deprecated('math', 'sin', new_cos='cos')`` has the
    same semantics as ``from math import sin, cos as new_cos``, but
    deprecating current module symbols.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.

    .. note:: 'inject_deprecated' could be deprecated now in favor of this
              function.

    '''
    from xoutil.future.types import class_types, func_types
    from xoutil.modules import force_module
    src = force_module(module)
    dst = force_module(2)
    src_name = src.__name__
    dst_name = dst.__name__
    dst = force_module(2)
    if not names and not aliases:
        # from module import *
        names = getattr(src, '__all__', None)
        if not names:
            names = (n for n in dir(src) if not n.startswith('_'))
    for name in names:
        if name not in aliases:
            aliases[name] = name
        else:
            msg = 'import_deprecated(): invalid repeated argument "{}"'
            raise ValueError(msg.format(name))
    unset = object()
    test_classes = class_types + func_types
    for alias in aliases:
        name = aliases[alias]
        target = getattr(src, name, unset)
        if target is not unset:
            if isinstance(target, test_classes):
                replacement = src_name + '.' + name
                deprecator = deprecated(replacement, DEFAULT_MSG, dst_name)
                target = deprecator(target)
            setattr(dst, alias, target)
        else:
            msg = "cannot import '{}' from '{}'"
            raise ImportError(msg.format(name, src_name))
    return dst
