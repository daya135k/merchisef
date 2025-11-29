#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.decorator.development
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-01-08

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

import warnings

from xoutil.compat import class_types as _class_types
from xoutil.objects import full_nameof

from .meta import decorator as _decorator

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Tue Jan  8 09:14:05 2013"


@_decorator
def unstable(target, msg=None):
    '''Declares that a method, class or interface is unstable.

    This has the side-effect of issuing a warning the first time the `target`
    is invoked.

    The `msg` parameter, if given, should be string that contains, at most, two
    positional replacement fields ({0} and {1}). The first replacement field
    will be the type of `target` (interface, class or function) and the second
    matches `target's` full name.

    '''
    print(target)
    if msg is None:
        msg = ('The {0} `{1}` is declared unstable. '
               'It may change in the future or be removed.')
    try:
        from zope.interface import Interface
    except ImportError:
        from xoutil import Ignored as Interface
    if isinstance(target, type(Interface)):
        objtype = 'interface'
    elif isinstance(target, _class_types):
        objtype = 'class'
    else:
        objtype = 'function or method'
    message = msg.format(objtype, full_nameof(target))
    if isinstance(target, _class_types) or issubclass(type(target),
                                                      type(Interface)):
        class meta(type(target)):
            pass
        def new(*args, **kwargs):
            warnings.warn(message, stacklevel=2)
            return target.__new__(*args, **kwargs)
        klass = meta(target.__name__, (target,), {'__new__': new})
        return klass
    else:
        def _unstable(*args, **kwargs):
            message = msg.format(objtype, full_nameof(target))
            warnings.warn(message, stacklevel=2)
            return target(*args, **kwargs)
        return _unstable
