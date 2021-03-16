import unittest

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi

class TestDetails(unittest.TestCase):
    def test_iterator_on_2004_05_session(self):
        test_fetcher = blf.BillsOverview()
        test_fetcher.update_all_bills_in_session(session_name="2004-05")

        for s in bdi.get_bill_details(test_fetcher):
            print(s)