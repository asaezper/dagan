import unittest
from unittest.mock import patch

from dagan.__main__ import main
from dagan.data import public_parameters


class MockedExecution(unittest.TestCase):
    @patch('dagan.upv.menu_bot.MenuBot.current_date')
    def test_change_date(self, mock_today):
        mock_today.side_effect = lambda: '28/12/2017'
        public_parameters.THREAD_TIMER_SECONDS = 30
        public_parameters.SUBS_WEEKDAY_LIST = range(7)
        public_parameters.SUBS_HOUR_INTERVAL = [21, 22]
        main()


if __name__ == '__main__':
    unittest.main()
