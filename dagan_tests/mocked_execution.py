import unittest
from unittest.mock import patch

from dagan.__main__ import main
from dagan.data import public_parameters, private_parameters
from dagan_tests.resources_test import resource_test_path, test_upv

THREAD_TIMER_SECONDS = 30
SUBS_WEEKDAY_LIST = range(7)
SUBS_HOUR_INTERVAL = [0, 24]
DATE_TO_SIMULATE = '15/01/2018'


class MockedExecution(unittest.TestCase):
    def setUp(self):
        self.saved_reports = {}

    @patch('dagan.upv.info_manager.InfoManager.request_info')
    @patch('dagan.upv.info_manager.InfoManager.request_token')
    def test_execute(self, request_token, request_info):
        request_token.side_effect = lambda: test_upv.TOKEN
        request_info.side_effect = lambda: test_upv.INFO_JSON

        # private_parameters.BOT_TOKEN = ''
        private_parameters.DB_URL = 'sqlite:///' + resource_test_path('dagan_test.db')
        public_parameters.THREAD_TIMER_SECONDS = THREAD_TIMER_SECONDS
        public_parameters.SUBS_WEEKDAY_LIST = SUBS_WEEKDAY_LIST
        public_parameters.SUBS_HOUR_INTERVAL = SUBS_HOUR_INTERVAL
        main()

    @patch('dagan.upv.info_manager.InfoManager.current_date')
    def test_change_date(self, mock_today):
        mock_today.side_effect = lambda: DATE_TO_SIMULATE
        main()


if __name__ == '__main__':
    unittest.main()
