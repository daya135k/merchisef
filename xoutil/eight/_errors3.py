#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._errors2
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-06

'''Exceptions handling, specific only for Python 2.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from . import _py3
assert _py3, 'This module should be loaded only in Py3K'


def throw(self, *args, **kwds):
    from ._errors import get_args
    tb, cause = get_args(*args, **kwds)
    if tb:
        self = self.with_traceback(tb)
    if cause:
        raise self from cause
    else:
        raise self
