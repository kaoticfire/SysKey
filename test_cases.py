from datetime import datetime
from unittest import TestCase, main

from main import check_disconnects, convert_time, log_level, time_in_range


class MyTestCase(TestCase):
    def test_convert_time(self):
        self.assertEqual(convert_time(1440), '00:24')

    def test_time_in_range(self):
        self.assertEqual(time_in_range(datetime.now(),
                                       datetime.strptime('18:00', '%H:%M'),
                                       datetime.strptime('06:00', '%H:%M')),
                         True)

    def test_log_level(self):
        self.assertEqual(log_level(), 'SysKey')

    def test_check_disconnects(self):
        self.assertEqual(check_disconnects(), True)


if __name__ == '__main__':
    main()
