# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.data
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2009-2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Some useful Data Structures and data-related algorithms and functions.

.. deprecated:: 1.4.0 This module is completely deprecated since 1.4.0. Most of
   its contents are already deprecated.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_absimports)

import xoutil.collections
from xoutil.deprecation import deprecated

@deprecated('xoutil.objects.smart_copy')
def smart_copy(source, target, full=False):
    '''Copies attributes (or keys) from `source` to `target`.

    .. deprecated:: 1.4.0 Use :func:`xoutil.objects.smart_copy`.

    Using the new function this one is roughly equivalent to::

       from xoutil.objects import smart_copy
       smart_copy(source, target, defaults=full)

    '''
    from xoutil.objects import smart_copy as _smart_copy
    return _smart_copy(source, target, defaults=full)

def adapt_exception(value, **kwargs):
    '''Like PEP-246, Object Adaptation, with ``adapt(value, Exception,
    None)``.

    If the value is not an exception is expected to be a tuple/list which
    contains an Exception type as its first item.

    '''
    isi, issc, ebc = isinstance, issubclass, Exception
    if isi(value, ebc) or isi(value, type) and issc(value, ebc):
        return value
    elif isi(value, (tuple, list)) and len(value) > 0 and issc(value[0], ebc):
        from xoutil.compat import str_base
        iss = lambda s: isinstance(s, str_base)
        ecls = value[0]
        args = ((x.format(**kwargs) if iss(x) else x) for x in value[1:])
        return ecls(*args)
    else:
        return None


@deprecated(xoutil.collections.SmartDict)
class SmartDict(xoutil.collections.SmartDict):
    '''A smart dict that extends the `update` method to accept several args.

    .. deprecated:: 1.4.0 Moved to :class:`xoutil.collections.SmartDict`.

    '''

@deprecated(xoutil.collections.OrderedSmartDict)
class SortedSmartDict(xoutil.collections.OrderedSmartDict):
    '''An ordered SmartDict.

    .. deprecated:: 1.4.0 Moved to
       :class:`xoutil.collections.OrderedSmartDict`.

    '''
