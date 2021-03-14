import unittest

from parlpy.bills.bill_votes_fetcher import fetch_votes

class TestVotes(unittest.TestCase):
    def test_votes_for_single_bill(self):
        r = fetch_votes('financial services')

        print(r.json())