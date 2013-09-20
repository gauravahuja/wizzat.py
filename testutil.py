import unittest, difflib, texttable, functools, os
from pghelper import fetch_results

__all__ = [
    'AssertSQLMixin',
    'OfflineError',
    'skip_offline',
    'skip_unfinished',
    'skip_performance',
]

class OfflineError(Exception): pass

def skip_offline(func):
    """
    This decorator is meant for tests.  It will catch OfflineError and issue a skipTest for you.
    """
    @functools.wraps(func)
    def wrapper(self):
        try:
            retval = func(self)
        except OfflineError:
            self.skipTest("----- OFFLINE TEST -----")

        return retval
    return wrapper

def skip_performance(func):
    """
    This decorator is meant for tests.  It checks for $ENV{PERFORMANCE_TEST} and will issue skipTest without it.
    """
    @functools.wraps(func)
    def wrapper(self):
        if not os.environ.get('PERFORMANCE_TEST', False):
            self.skipTest("----- PERFORMANCE TEST -----")
        else:
            return func(self)

    return wrapper

def skip_unfinished(func):
    """
    This decorator is meant for tests.  It automatically issues a skipTest.
    """

    @functools.wraps(func)
    def wrapper(self):
        self.skipTest("----- UNFINISHED TEST -----")
    return wrapper


class AssertSQLMixin(object):
    """
    Mixin for assertSqlResults
    """
    def assertSqlResults(self, conn, sql, *rows):
        header, rows = rows[0], rows[1:]
        results = fetch_results(conn, sql)

        expected = tableize_grid(header, rows)
        actual   = tableize_obj_list(header, results)

        diff = difflib.unified_diff(expected, actual)
        if diff:
            raise AssertionError("Assert failed for sql\n{sql}\n\n{diff}".format(
                sql = sql,
                diff = diff,
            ))
