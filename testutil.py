import unittest, difflib, texttable, functools, os
from pghelper import ConnMgr, fetch_results
from util import assert_online, OfflineError
from dateutil import reset_now
from formattedtable import *

__all__ = [
    'AssertSQLMixin',
    'TestCase',
    'OfflineError',
    'skip_offline',
    'skip_unfinished',
    'skip_performance',
]

def skip_offline(func):
    """
    This decorator is meant for tests.  It will catch OfflineError and issue a skipTest for you.
    """
    @functools.wraps(func)
    def wrapper(self):
        try:
            assert_online()
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

###

class AssertSQLMixin(object):
    """
    Mixin for assertSqlResults
    """
    def setup_connections(self):
        self.mgr = ConnMgr.default_from_info(**self.db_info)
        self.conn = self.mgr.getconn("conn")

    def teardown_connections(self):
        # First tear down all the other connection pools
        while ConnMgr.all_mgrs:
            mgr = ConnMgr.all_mgrs.pop()
            if mgr != self.mgr:
                mgr.rollback()
                mgr.closeall()

        # Now tear ours down and put it back
        if self.mgr:
            self.mgr.rollback()
            ConnMgr.all_mgrs.append(self.mgr)

    def assertSqlResults(self, conn, sql, *rows):
        header, rows = rows[0], rows[1:]
        results = fetch_results(conn, sql)

        expected = tableize_grid(header, rows)
        actual   = tableize_obj_list(header, results)

        diff = list(difflib.unified_diff(expected.split('\n'), actual.split('\n')))
        if diff:
            raise AssertionError("Assert failed for sql\n{sql}\n\n{diff}".format(
                sql = sql,
                diff = '\n'.join(diff),
            ))

class TestCase(AssertSQLMixin, unittest.TestCase):
    """
    This is a default test case which takes advantage of AssertSQL and setting up connections.

    db_info should be overridden with appropriate database connection information.
    """
    # This can be (and perhaps should be?) overridden in subclasses
    setup_database = False
    db_info = {
        'host'     : 'localhost',
        'port'     : 5432,
        'user'     : 'pyutil',
        'password' : 'pyutil',
        'database' : 'pyutil_testdb',
        'minconn'  : 0,
        'maxconn'  : 2,
    }

    def setUp(self):
        super(TestCase, self).setUp()
        reset_now()
        self.mgr  = None
        self.conn = None

        if self.setup_database:
            self.setup_connections()

    def tearDown(self):
        super(TestCase, self).tearDown()
        self.teardown_connections()
