import unittest
import datetime

from parlpy.bills.bill_votes_fetcher import fetch_votes



class TestVotes(unittest.TestCase):
    def test_votes_for_single_bill(self):
        mock_start_time = datetime.date(2019,12,9)
        mock_end_time = None

        r = fetch_votes('financial services', mock_start_time, mock_end_time)

        print(r.json())