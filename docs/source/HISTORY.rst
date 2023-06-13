Changelog
=========

Reversed chronological order.


1.1 series
----------

2012-07-03. Release 1.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Created the whole documentation Sphinx directory.

- Removed xoutil.future since it was not properly tested.

- Removed xoutil.annotate, since it's not portable across Python's VMs.

- Introduced module :mod:`xoutil.collections`

- Deprecated modules :mod:`xoutil.default_dict`, :mod:`xoutil.opendict` in
  favor of :mod:`xoutil.collections`.

- Backported :func:`xoutil.functools.lru_cache` from Python 3.2.

- Deprecated module :mod:`xoutil.memoize` in favor of
  :func:`xoutil.functools.lru_cache`.


1.0 series
----------


2012-06-15. Release 1.0.30
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces a new module :py:mod:`xoutil.proxy`.

- Starts working on the sphinx documentation so that we move to 1.1 release we
  a decent documentation.

2012-06-01. Release 1.0.29.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces `xoutil.iterators.slides` and `xoutil.aop.basic.contextualized`

2012-05-28. Release 1.0.28.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixes normalize path and other details
- Makes validate_attrs to work with mappings as well as objects
- Improves complementors to use classes as a special case of sources
- Simplifies importing of legacy modules
- PEP8

2012-05-22. Release 1.0.27.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Removes bugs that were not checked (tested) in the previous release.

2012-05-21. Release 1.0.26.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Changes in AOP classic. Now you have to rename after, before and around methods
  to _after, _before and _around.

  It is expected that the signature of those methods change in the future.

- Introducing a default argument for :func:`xoutil.objects.get_first_of`.

- Other minor additions in the code. Refactoring and the like.

2012-04-30. Release 1.0.25.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Extends the classical AOP approach to modules. Implements an extended version
  with hooks.

- 1.0.25.1: Makes classical/extended AOP more reliable to TypeError's in getattr.
  xoonko, may raise TypeError's for TranslatableFields.

2012-04-27. Release 1.0.24.

- Introduces a classical AOP implementation: xoutil.aop.classical.

2012-04-10. Release 1.0.23.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces decorators: xoutil.decorators.instantiate and xoutil.aop.complementor

2012-04-05. Release 1.0.22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Allows annotation's expressions to use defined local variables.  Before this
  release the following code raised an error::

        >>> from xoutil.annotate import annotate
        >>> x1 = 1
        >>> @annotation('(a: x1)')
        ... def dummy():
        ...     pass
        Traceback (most recent call last):
           ...
        NameError: global name 'x1' is not defined

- Fixes decorators to allow args-less decorators


2012-04-03. Release 1.0.21
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Includes a new module :mod:`xoutil.annotate` that provides a way to place
  Python annotations in forward-compatible way.
