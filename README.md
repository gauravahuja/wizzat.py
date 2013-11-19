pyutil
======
Python Utilities includes an assortment of decorators, utility methods, and utility classes:
- The _decorators_ module primarily contains memoization, benchmarking, coroutine, and tail call recursion.
- The _queuefile_ module contains a thread and process safe file writer.
- The _util_ module contains utility functions.
- The _dateutil_ module contains date utils for working on top of python-dateutil and pytz.
- The _pghelper_ module contains utilities for working with raw psycopg2 connections, a light weight ORM, and a light weight named connection manager.
- The _formattedtable_ module contains a wrapper on top of texttable for ensuring items are formatted before being printed
- The _serialization_ module contains methods for space and time efficient serialization of integer sets and lists.
- The _testutil_ module contains several decorators for manipulating tests as well as mixins for getting various test behavior.
- The _mathutil_ module contains various math utilites as well as logarithmic percentile approximation and running average.
- The _runner_ module contains a base class that handles much of the common boilerplate in setting up runners.

The most interesting functions are likely:
- decorators.memoize()
- dateutil.\*
- util.\*
- mathutil.Percentile

Documentation is maintained on individual functions

The official repository is http://www.github.com/pyutil
