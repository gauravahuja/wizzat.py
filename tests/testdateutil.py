from pyutil.testutil import *
from pyutil.dateutil import *
import unittest, datetime, time

class TestDateUtil(unittest.TestCase):
    def test_epoch_handling(self):
        self.assertEqual(from_epoch(1378741939), datetime.datetime(2013, 9, 9, 15, 52, 19))
        self.assertEqual(to_epoch(datetime.datetime(2013, 9, 9, 15, 52, 19)), 1378741939)

    def test_now_can_be_set_and_reset(self):
        t1 = now()
        time.sleep(0.1)
        t2 = now()
        self.assertNotEqual(t1, t2)

        set_now(now())
        t1 = now()
        time.sleep(0.1)
        t2 = now()
        self.assertEqual(t1, t2)

        t3 = now()
        reset_now()
        t1 = now()
        time.sleep(0.1)
        t2 = now()
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_coerce_date(self):
        self.assertEqual(coerce_date(1378741939), datetime.datetime(2013, 9, 9, 15, 52, 19))
        self.assertEqual(coerce_date(datetime.datetime(2013, 9, 9, 15, 52, 19)), datetime.datetime(2013, 9, 9, 15, 52, 19))

        # String formatting not accepted yet
        #self.assertEqual(coerce_date("2013-09-09 15:52:19"), datetime.datetime(2013, 9, 9, 15, 52, 19))

    def test_to_second(self):
        set_now(datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(now(), datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(to_second(now()), datetime.datetime(2013, 9, 9, 15, 52, 19, 0))

    def test_to_minute(self):
        set_now(datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(now(), datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(to_minute(now()), datetime.datetime(2013, 9, 9, 15, 52, 0, 0))

    def test_to_hour(self):
        set_now(datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(now(), datetime.datetime(2013, 9, 9, 15, 52, 19, 43435))
        self.assertEqual(to_hour(now()), datetime.datetime(2013, 9, 9, 15, 0, 0, 0))

    @skip_unfinished
    def test_to_day(self):
        pass

    @skip_unfinished
    def test_to_week(self):
        pass

    @skip_unfinished
    def test_to_month(self):
        pass

    @skip_unfinished
    def test_to_quarter(self):
        pass

    @skip_unfinished
    def test_to_year(self):
        pass
