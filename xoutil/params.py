#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.params
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created 2015-07-13

r'''Function argument manager.

This module must avoid dependencies on modules that aren't basic enough that
could be the use of this one itself.

It's usual to declare functions or methods with generic prototypes::

  def func(*args, **kwargs):
      ...

Actual parameters must be identified in a smart way.  This module provide a
tool to solve argument identification from scheme definition::

  scheme, row = ParamScheme, ParamSchemeRow
  sample_scheme = scheme(
      row('stream', 0, -1, 'output', default=sys.stdout, coerce=file_coerce),
      row('indent', 0, 1, default=1, coerce=positive_int),
      row('width', 0, 1, 2, 'max_width', default=79, coerce=positive_int),
      row('newline', default='\n', coerce=string_types))

A scheme-row can be used in an independent way using a `ParamManager`:class:
instance.

.. versionadded:: 1.7.0

.. versionchanged:: 1.7.2 Migrated to a completely new shape forgetting
       initially created `ParamConformer` class.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.deprecation import deprecated


@deprecated('xoutil.fp.params.issue_9137')
def issue_9137(args, max_args=None, caller=None):
    '''Parse positional arguments for methods fixing issue 9137.

    There are methods that expect 'self' as valid keyword argument, this is
    not possible if this name is used formally::

      def update(self, *args, **kwds):
          ...

    To do that, declare them as ``method_name(*args, **kwds)``, and inner it
    use this function::

      def update(*args, **kwds):
          self, args = issue_9137(args, max_args=1, caller='update')

    :param max_args: A positive integer or ``None``; expected at most this
           count of positional arguments.

    :param caller: Used for error reporting.

    :returns: (self, rest of checked positional arguments)

    '''
    from xoutil.fp.params import issue_9137
    deprecated_args = [] if max_args is None else ['max_args']
    if caller is not None:
        deprecated_args.append('caller')
    if deprecated_args:
        import warnings
        msg = ('issue_9137() {} parameters are not used any more, see '
               'new function "xoutil.fp.params.issue_9137" for more '
               'information.')
        warnings.warn(msg.format(deprecated_args))
    return issue_9137(args)


@deprecated('xoutil.fp.params.check_default')
def pos_default(args, caller=None, base_count=0):
    '''Return a list with the default value given as a positional argument.

    If no value is given, return an empty list.

    For example::

      def get(self, key, *args):
          'A default value can be given as a positional argument'
          if key in self:
              return self[key]
          else:
              res = pos_default(args)
              if res:
                  return res[0]
              else:
                  raise KeyError(key)

    An exception is raised if more than one positional argument is given.
    CALLER and BASE_COUNT optional arguments are used to complement message in
    this case.

    '''
    from xoutil.fp.params import check_default, Undefined
    return () if check_default()(*args) is Undefined else args


class ParamManager(object):
    '''Function parameters parser.

    For example::

      def wraps(*args, **kwargs):
          pm = ParamManager(args, kwargs)
          name = pm(0, 1, 'name', coerce=str)
          wrapped = pm(0, 1, 'wrapped', coerce=valid(callable))
          ...

    See `ParamSchemeRow`:class: and `ParamScheme`:class: classes to
    pre-define and validate schemes for extracting parameter values in a
    consistent way.

    '''

    def __init__(self, args, kwds):
        '''Created with actual parameters of a client function.'''
        self.args = args
        self.kwds = kwds
        self.consumed = set()    # consumed identifiers

    def __call__(self, *ids, **options):
        '''Get a parameter value.

        :param ids: parameter identifiers.

        :param options: keyword argument options.

        Options could be:

        - 'default': value used if the parameter is absent;

        - 'coerce': check if a value is valid or not and convert to its
          definitive value; see `xoutil.fp.prove.Coercer`:class: for more
          information.

        '''
        from xoutil.fp.option import Just, Wrong, none
        # TODO: Change this
        from xoutil.fp.prove.semantic import predicate as Coercer
        args, kwds = self.args, self.kwds
        i, res = 0, none
        while isinstance(res, Wrong) and i < len(ids):
            key = ids[i]
            if key in self.consumed:
                pass
            elif isinstance(key, int):
                try:
                    res = args[key]
                except IndexError:
                    pass
            elif key in kwds:
                res = kwds[key]
            if not isinstance(res, Wrong) and 'coerce' in options:
                aux = Coercer(options['coerce'])(res)
                res = aux.inner if isinstance(aux, Just) else aux
            if not isinstance(res, Wrong):
                self.consumed.add(key)
                if isinstance(key, int) and key < 0:
                    # consume both, negative and adjusted value
                    key = len(args) + key
                    self.consumed.add(key)
            else:
                i += 1
        if isinstance(res, Wrong):
            if 'default' in options:
                return options['default']
            elif isinstance(res.inner, BaseException):
                from xoutil.eight.exceptions import throw
                throw(res.inner)
            else:
                raise TypeError('value for "{}" is not found'.format(ids))
        else:
            return res.inner if isinstance(res, Just) else res

    def remainder(self):
        '''Return not consumed values in a mapping.'''
        from xoutil.eight import range
        passed = set(range(len(self.args))) | set(self.kwds)
        ids = passed - self.consumed
        args, kwds = self.args, self.kwds
        return {k: args[k] if isinstance(k, int) else kwds[k] for k in ids}


class ParamSchemeRow(object):
    '''Scheme row for a  `ParamManager`:class: instance call.

    This class validates identifiers and options at this level; these
    checks are not done in a call to get a parameter value.

    Normally this class is used as part of a full `ParamScheme`:class:
    composition.

    Additionally to the options can be passed to
    `ParamManager.__call__`:meth:', this class can be instanced with:

    - 'key': an identifier to be used when the parameter is only positional or
      when none of the possible keyword aliases must be used as the
      primary-key.

    '''
    __slots__ = ('ids', 'options', '_key')

    def __init__(self, *ids, **options):
        from collections import Counter
        from xoutil.eight import iteritems, string_types as strs
        from xoutil.eight.string import safe_isidentifier as iskey
        from xoutil.eight import type_name
        from xoutil.fp.option import none
        # TODO: Change this
        from xoutil.fp.prove.semantic import predicate as Coercer
        aux = {k: c for k, c in iteritems(Counter(ids)) if c > 1}
        if aux:
            parts = ['{!r} ({})'.format(k, aux[k]) for k in aux]
            msg = '{}() repeated identifiers: {}'
            raise TypeError(msg.format(type_name(self), ', '.join(parts)))
        else:
            def ok(k):
                return (isinstance(k, strs) and iskey(k) or
                        isinstance(k, int))

            bad = [k for k in ids if not ok(k)]
            if bad:
                msg = ('{}() identifiers with wrong type (only int and str '
                       'allowed): {}')
                raise TypeError(msg.format(type_name(self), bad))
        key = options.pop('key', none)
        if not (key is none or iskey(key)):
            msg = ('"key" option must be an identifier, "{}" of type "{}" '
                   'given')
            raise TypeError(msg.format(key), type_name(key))
        if 'default' in options:
            aux = {'default': options.pop('default')}
        else:
            aux = {}
        if 'coerce' in options:
            aux['coerce'] = Coercer(options.pop('coerce'))
        if options:
            msg = '{}(): received invalid keyword parameters: {}'
            raise TypeError(msg.format(type_name(self), set(options)))
        self.ids = ids
        self.options = aux
        self._key = key

    def __str__(self):
        from xoutil.eight import iteritems
        parts = [repr(k) for k in self.ids]
        for key, value in iteritems(self.options):
            parts.append('{}={!r}'.format(key, value))
        aux = ', '.join(parts)
        return 'ParamSchemeRow({})'.format(aux)
    __repr__ = __str__

    def __call__(self, *args, **kwds):
        '''Execute a scheme-row using as argument a `ParamManager` instance.

        The concept of `ParamManager`:class: instance argument is a little
        tricky: when a variable number of arguments is used, if only one
        positional and is already an instance of `ParamManager`:class:, it is
        directly used; if two, the first is a `tuple` and the second is a
        `dict`, these are considered the constructor arguments of the new
        instance; otherwise all arguments are used to build the new instance.

        '''
        count = len(args)
        if count == 1 and not kwds and isinstance(args[0], ParamManager):
            manager = args[0]
        else:
            if count == 2 and not kwds:
                a, k = args
                if isinstance(a, tuple) and isinstance(k, dict):
                    args, kwds = a, k
            manager = ParamManager(args, kwds)
        return manager(*self.ids, **self.options)

    @property
    def default(self):
        '''Returned value if parameter value is absent.

        If not defined, special value ``none`` is returned.

        '''
        from xoutil.fp.option import none
        return self.options.get('default', none)

    @property
    def key(self):
        '''The primary key for this scheme-row definition.

        This concept is a little tricky (the first string identifier if some
        is given, if not then the first integer).  This definition is useful,
        for example, to return remainder not consumed values after a scheme
        process is completed (see `ParamManager.remainder`:meth: for more
        information).

        '''
        # TODO: calculate the key value in the constructor
        from xoutil.eight import string_types as strs
        from xoutil.fp.option import none
        res = self._key
        if res is none:
            res = next((k for k in self.ids if isinstance(k, strs)), None)
            if res is None:
                res = self.ids[0]
            self._key = res
        return res


class ParamScheme(object):
    '''Full scheme for a  `ParamManager`:class: instance call.

    This class receives a set of `ParamSchemeRow`:class: instances and
    validate them as a whole.

    '''
    __slots__ = ('rows', 'cache')

    def __init__(self, *rows):
        from xoutil.eight import string_types as strs, type_name
        from xoutil.fp.params import check_count
        check_count(len(rows) + 1, 2, caller=type_name(self))
        used = set()
        for idx, row in enumerate(rows):
            if isinstance(row, ParamSchemeRow):
                this = {k for k in row.ids if isinstance(k, strs)}
                aux = used & this
                if not aux:
                    used |= this
                else:
                    msg = ('{}() repeated keyword identifiers "{}" in '
                           'row {}').format(type_name(self), aux, idx)
                    raise ValueError(msg)
        self.rows = rows
        self.cache = None

    def __str__(self):
        from xoutil.eight import type_name
        aux = ',\n\i'.join(str(row) for row in self)
        return '{}({})'.format(type_name(self), aux)

    def __repr__(self):
        from xoutil.eight import type_name
        return '{}({} rows)'.format(type_name(self), len(self))

    def __len__(self):
        '''The defined scheme-rows number.'''
        return len(self.rows)

    def __getitem__(self, idx):
        '''Obtain the scheme-row by a given index.'''
        from xoutil.eight import string_types
        if isinstance(idx, string_types):
            cache = self._getcache()
            return cache[idx]
        else:
            return self.rows[idx]

    def __iter__(self):
        '''Iterate over all defined scheme-rows.'''
        return iter(self.rows)

    def __call__(self, args, kwds, strict=False):
        '''Get a mapping with all resulting values.

        If special value 'none' is used as 'default' option in a scheme-row,
        corresponding value isn't returned in the mapping if the parameter
        value is missing.

        '''
        from xoutil.eight import type_name

        def ok(v):
            from xoutil.fp.option import Wrong
            return not isinstance(v, Wrong)

        pm = ParamManager(args, kwds)
        aux = ((row.key, row(pm)) for row in self)
        res = {key: value for key, value in aux if ok(value)}
        rem = pm.remainder()
        if strict:
            if rem:
                msg = ('after a full `{}` process, there are still remainder '
                       'parameters: {}')
                raise TypeError(msg.format(type_name(self), set(rem)))
        else:
            res.update(rem)
        return res

    def keys(self):
        '''Partial compatibility with mappings.'''
        from xoutil.eight import iterkeys
        return iterkeys(self._getcache())

    def items(self):
        '''Partial compatibility with mappings.'''
        from xoutil.eight import iteritems
        return iteritems(self._getcache())

    @property
    def defaults(self):
        '''Return a mapping with all valid default values.'''
        def ok(v):
            from xoutil.fp.option import Wrong
            return not isinstance(v, Wrong)

        aux = ((row.key, row.default) for row in self)
        return {k: d for k, d in aux if ok(d)}

    def _getcache(self):
        if not self.cache:
            self.cache = {row.key: row for row in self}
        return self.cache


if __name__ == '__main__':
    print('Testing module `xoutil.params`')

    import sys
    from xoutil.eight import string_types
    from xoutil.cl import (file_coerce as is_file,
                           positive_int_coerce as positive_int)

    scheme, row = ParamScheme, ParamSchemeRow

    sample_scheme = scheme(
        row('stream', 0, -1, 'output', default=sys.stdout, coerce=is_file),
        row('indent', 0, 1, default=1, coerce=positive_int),
        row('width', 0, 1, 2, 'max_width', default=79, coerce=positive_int),
        row('newline', default='\n', coerce=string_types))

    def test(*args, **kwargs):
        from xoutil.eight import type_name
        print('-'*80)
        print(">>>", args, "--", kwargs)
        try:
            print('...', sample_scheme.get(args, kwargs))
        except BaseException as error:
            print("???", '{}:'.format(type_name(error)), error)

    test(4, 80)
    test(2, '80')
    test(4)
    test(80, indent=4, extra="I'm OK!")
    test(width=80)
    test(sys.stderr, 4, 80)
    test(4, sys.stderr, newline='\n\r')
    test(sys.stderr, 4, output=sys.stderr)
    test(sys.stderr, 4, 80, output=sys.stderr)
    test(4, -79)
