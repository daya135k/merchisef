#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._mixin
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-03

'''Private module for all mix-ins definitions.

This module is private because is used for two client modules for the `mixin`
concept.  See `Mixin`:class: for more information.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


MIXIN_NAME = '__mixin__'
MIXIN_SLOTS = ('bases', 'metas', 'attrs')


class Mixin(object):
    '''Base-class to several mix-in kinds.

    - Syntax unification for meta-classes between Python 2 and 3.  See
      `xoutil.eight.meta.metaclass`:func: for more information.  For example::

        >>> from xoutil.eight.abc import ABCMeta
        >>> from xoutil.eight.meta import metaclass
        >>> class Foobar(metaclass(ABCMeta)):
        ...     pass
        >>> (Foobar.__bases__ == (object, ), type(Foobar) is ABCMeta)
        (True, True)

    - Helper base classes that when used as a base force a meta-class but
      nothing else (the new class don't have helper-class in its bases).  See
      `xoutil.eight.mixins.helper_class`:func: for more information.  A good
      example is our example of `xoutil.eight.abc.ABC`, if used as a base,
      `ABCMeta` is imposed::

        >>> from xoutil.eight.abc import ABC, ABCMeta
        >>> class Foobar(ABC):
        ...     pass
        >>> (Foobar.__bases__ == (object, ), type(Foobar) is ABCMeta)
        (True, True)

    - Class templates that can be used later to weave main classes composed
      for those mix-ins.  For example::

        >>> from xoutil.eight.abc import ABCMeta
        >>> from xoutil.eight.mixins import mixin
        >>> class Foo(object):
        ...     pass
        >>> class Bar(dict):
        ...     pass
        >>> class EggMeta(type):
        ...     pass
        >>> Test = mixin(Foo, Bar, meta=(EggMeta, ABCMeta), name='Test')

    - Weaver a main-class using several parts.  For example::

        >>> class Foobar(list, mixin(Test)):
        ...     pass

    '''
    __slots__ = ()

    @classmethod
    def formalize_args(cls, args, kwargs):
        pass

    @staticmethod
    def extract_bases(bases, kwargs):
        '''In a meta-mixin, splits real-bases from mixins.

        Return a tuple with the bases and a list with the mixins.

        '''
        from xoutil.inspect import _static_getmro as getmro
        res, mixins = [], []
        for b in bases:
            if b.__bases__ == (Mixin, ):
                mixins.append(b)
            elif Mixin not in getmro(b):
                res.append(b)
            else:
                msg = '`{}` inherits directly from `Mixin` class.'
                raise TypeError(msg.format(b.__name__))
        if mixins:
            return res
        else:
            raise TypeError('Unexpected meta-mixin without any `Mixin` base.')
