#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Python Software Foundation
# All rights reserved.
#
# Most of the contents of this file were extracted from the source code of
# CPython 3.6.
#

'''Backports and enhancements to the contextlib module.

Utilities for with-statement contexts.  See `343`:pep:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import contextlib as _stdlib    # noqa
from contextlib import *    # noqa

__all__ = [n for n in getattr(_stdlib, '__all__', []) if n != 'nested']


try:
    ContextDecorator    # noqa
except NameError:
    from contextlib2 import ContextDecorator    # noqa
    __all__.append('ContextDecorator')

try:
    ExitStack    # noqa
except NameError:
    from contextlib2 import ExitStack    # noqa
    __all__.append('ExitStack')


try:
    redirect_stdout    # noqa
except NameError:
    from contextlib2 import redirect_stdout    # noqa
    __all__.append('redirect_stdout')


try:
    redirect_stderr    # noqa
except NameError:
    from contextlib2 import redirect_stderr    # noqa
    __all__.append('redirect_stderr')


try:
    suppress    # noqa
except NameError:
    from contextlib2 import suppress    # noqa
    __all__.append('suppress')


try:
    del nested    # noqa
except NameError:
    pass
