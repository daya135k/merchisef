# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.validators.identifiers
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# Created on Nov 11, 2011

'''
Regular expressions and validation functions for several identifiers.
'''


from __future__ import (division as _py3_division, print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from re import compile as _regex_compile


__all__ = (b'is_valid_identifier' , b'is_valid_full_identifier', b'is_valid_slug')



_IDENTIFIER_REGEX = _regex_compile('(?i)^[_a-z][\w]*$')

def is_valid_identifier(name):
    return isinstance(name, basestring) and (_IDENTIFIER_REGEX.match(name) is not None)



_FULL_IDENTIFIER_REGEX = _regex_compile('(?i)^[_a-z][\w]*([.][_a-z][\w]*)*$')

def is_valid_full_identifier(name):
    return isinstance(name, basestring) and (_FULL_IDENTIFIER_REGEX.match(name) is not None)



_SLUG_REGEX = _regex_compile('(?i)^[\w]+([-][\w]+)*$')

def is_valid_slug(slug):
    return isinstance(slug, basestring) and (_SLUG_REGEX.match(slug) is not None)
