import unittest
from unittest.mock import patch

from dagan.__main__ import main


class MockedExecution(unittest.TestCase):
    @patch('dagan.upv.menu_bot.MenuBot.current_date')
    def test_change_date(self, mock_today):
        mock_today.side_effect = lambda: '28/12/2017'
        main()


if __name__ == '__main__':
    unittest.main()
