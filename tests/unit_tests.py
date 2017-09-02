"""
Unit tests for parse_log_file.py and run_report.py

Author: Thomas Johns @t0mj
"""
import mock
import pandas as pd
import unittest

from run_report import ReportRunner
from parse_log_file import parse_line
from mock import MagicMock

# Sample raw data and msgpack dataframe
LOG_DATA = ['10.0.32.179 - - [31/Oct/1994:14:03:20 +0000] "GET /system/get.php?token=l_CHgTmLxX HTTP/1.0" 404 484',
            '10.0.146.5 - - [31/Oct/1994:14:03:21 +0000] "POST /kernel/list.php HTTP/1.1" 204 1851',
            '10.0.136.237 - - [31/Oct/1994:14:03:16 +0000] "HEAD /system/request.php HTTP/1.0" 403 1093']

LOG_MSG = b'\x84\xa3typ\xadblock_manager\xa5klass\xa9DataFrame\xa4axes\x92\x86\xa3typ\xa5index\xa5klass\xa5Index\xa4name\xc0\xa5dtype\xa6object\xa4data\x98\xa2ip\xa7user_id\xa8datetime\xaerequest_method\xa8resource\xa8protocol\xa6status\xabreturn_size\xa8compress\xc0\x86\xa3typ\xabrange_index\xa5klass\xaaRangeIndex\xa4name\xc0\xa5start\x00\xa4stop\x03\xa4step\x01\xa6blocks\x92\x86\xa4locs\x86\xa3typ\xa7ndarray\xa5shape\x91\x02\xa4ndim\x01\xa5dtype\xa5int64\xa4data\xd8\x00\x06\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\xa8compress\xc0\xa6values\xc70\x00\x94\x01\x00\x00\x00\x00\x00\x00\xcc\x00\x00\x00\x00\x00\x00\x00\x93\x01\x00\x00\x00\x00\x00\x00\xe4\x01\x00\x00\x00\x00\x00\x00;\x07\x00\x00\x00\x00\x00\x00E\x04\x00\x00\x00\x00\x00\x00\xa5shape\x92\x02\x03\xa5dtype\xa5int64\xa5klass\xa8IntBlock\xa8compress\xc0\x86\xa4locs\x86\xa3typ\xa7ndarray\xa5shape\x91\x06\xa4ndim\x01\xa5dtype\xa5int64\xa4data\xc70\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\xa8compress\xc0\xa6values\xdc\x00\x12\xab10.0.32.179\xaa10.0.146.5\xac10.0.136.237\xa1-\xa1-\xa1-\xba31/Oct/1994:14:03:20 +0000\xba31/Oct/1994:14:03:21 +0000\xba31/Oct/1994:14:03:16 +0000\xa3GET\xa4POST\xa4HEAD\xd9 /system/get.php?token=l_CHgTmLxX\xb0/kernel/list.php\xb3/system/request.php\xa8HTTP/1.0\xa8HTTP/1.1\xa8HTTP/1.0\xa5shape\x92\x06\x03\xa5dtype\xa6object\xa5klass\xabObjectBlock\xa8compress\xc0'


class TestParseLogFile(unittest.TestCase):
    def test_parse_line(self):
        result = []
        for line in LOG_DATA:
            result.append(parse_line(line))

        expected_output = [('10.0.32.179', '-', '-', '31/Oct/1994:14:03:20 +0000', 'GET',
                            '/system/get.php?token=l_CHgTmLxX', 'HTTP/1.0', '404', '484'),
                           ('10.0.146.5', '-', '-', '31/Oct/1994:14:03:21 +0000', 'POST',
                            '/kernel/list.php', 'HTTP/1.1', '204', '1851'),
                           ('10.0.136.237', '-', '-', '31/Oct/1994:14:03:16 +0000', 'HEAD',
                            '/system/request.php', 'HTTP/1.0', '403', '1093')]
        self.assertEqual(result, expected_output)


class TestReportRunner(unittest.TestCase):

    @mock.patch.object(ReportRunner, 'get_df', MagicMock())
    def setUp(self):
        self.runner = ReportRunner()
        # create test dataframe
        self.runner.df = pd.read_msgpack(LOG_MSG)

    def test_top_10_requests(self):
        self.runner.top_10_requests()
        expected_requests = ['system/request.php', 'kernel/list.php', 'system/get.php']
        for request in expected_requests:
            self.assertIn(request, self.runner.output[2])

    def test_successful_requests(self):
        self.runner.successful_requests()
        self.assertIn('33.33%', self.runner.output[1])

    def test_unsuccessful_requests(self):
        self.runner.unsuccessful_requests()
        self.assertIn('66.67%', self.runner.output[1])


if __name__ == '__main__':
    unittest.main()
