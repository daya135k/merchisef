#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.meta
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-25

'''Implements the metaclass() function using the Py3k syntax.

'''

from . import _py3
from ._meta import Mixin    # noqa

if _py3:
    from ._meta3 import metaclass
else:
    from ._meta2 import metaclass


metaclass.__doc__ = '''Define the metaclass of a class.

    .. versionadded:: 1.7.0  It's available as
       `xoutil.objects.metaclass`:func: since 1.4.1.  That alias is now
       deprecated and will be removed in 1.8.

    This function allows to define the metaclass of a class equally in Python
    2 and 3.

    Usage::

     >>> class Meta(type):
     ...   pass

     >>> class Foobar(metaclass(Meta)):
     ...   pass

     >>> class Spam(metaclass(Meta), dict):
     ...   pass

     >>> type(Spam) is Meta
     True

     >>> Spam.__bases__ == (dict, )
     True

    .. versionadded:: 1.5.5 The `kwargs` keywords arguments with support for
       ``__prepare__``.

    Metaclasses are allowed to have a ``__prepare__`` classmethod to return
    the namespace into which the body of the class should be evaluated.  See
    :pep:`3115`.

    .. warning:: The :pep:`3115` is not possible to implement in Python 2.7.

       Despite our best efforts to have a truly compatible way of creating
       meta classes in both Python 2.7 and 3.0+, there is an inescapable
       difference in Python 2.7.  The :pep:`3115` states that ``__prepare__``
       should be called before evaluating the body of the class.  This is not
       possible in Python 2.7, since ``__new__`` already receives the
       attributes collected in the body of the class.  So it's always too late
       to call ``__prepare__`` at this point and the Python 2.7 interpreter
       does not call it.

       Our approach for Python 2.7 is calling it inside the ``__new__`` of a
       "side" metaclass that is used for the base class returned.  This means
       that ``__prepare__`` is called **only** for classes that use the
       `metaclass`:func: directly.  In the following hierarchy::

         class Meta(type):
              @classmethod
              def __prepare__(cls, name, bases, **kwargs):
                  from xoutil.future.collections import OrderedDict
                  return OrderedDict()

         class Foo(metaclass(Meta)):
              pass

         class Bar(Foo):
              pass

       when creating the class ``Bar`` the ``__prepare__()`` class method is
       not called in Python 2.7!

    .. seealso:: `xoutil.future.types.prepare_class`:func: and
       `xoutil.future.types.new_class`:func:.

    .. warning::

       You should always place your metaclass declaration *first* in the list
       of bases. Doing otherwise triggers *twice* the metaclass' constructors
       in Python 3.1 or less.

       If your metaclass has some non-idempotent side-effect (such as
       registration of classes), then this would lead to unwanted double
       registration of the class::

        >>> class BaseMeta(type):
        ...     classes = []
        ...     def __new__(cls, name, bases, attrs):
        ...         res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
        ...         cls.classes.append(res)   # <-- side effect
        ...         return res

        >>> class Base(metaclass(BaseMeta)):
        ...     pass

        >>> class SubType(BaseMeta):
        ...     pass

        >>> class Egg(metaclass(SubType), Base):   # <-- metaclass first
        ...     pass

        >>> Egg.__base__ is Base   # <-- but the base is Base
        True

        >>> len(BaseMeta.classes) == 2
        True

        >>> class Spam(Base, metaclass(SubType)):
        ...     'Like "Egg" but it will be registered twice in Python 2.x.'

       In this case the registration of Spam ocurred twice::

        >>> BaseMeta.classes  # doctest: +SKIP
        [<class Base>, <class Egg>, <class Spam>, <class Spam>]

       Bases, however, are just fine::

        >>> Spam.__bases__ == (Base, )
        True

    .. versionadded:: 1.7.1 Now are accepted atypical meta-classes, for
       example functions or any callable with the same arguments as those that
       type accepts (class name, tuple of base classes, attributes mapping).

'''

metaclass.__module__ = __name__
