#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.uuidutil
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 17, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)


__docstring_format__ = 'rst'
__author__ = 'manu'


def uuid():
    '''
    Return a "Global Unique ID" as a string.
    '''
    from uuid import uuid1
    return '%s' % uuid1()
