import unittest

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi

def print_all_info_using_iterator(fetcher):
    for s in bdi.get_bill_details(fetcher, debug=True):
        for d in s.divisions_list:
            print(f"division name: {d.division_name}")
            print(f"division stage: {d.division_stage}")
            print(f"ayes: {d.ayes}")
            print(f"noes: {d.noes}")

class TestDetails(unittest.TestCase):
    # a much shorter test, but does not test divisions capabilities
    def test_iterator_on_2004_05_session(self):
        fetcher_2004_05 = blf.BillsOverview()
        fetcher_2004_05.update_all_bills_in_session(session_name="2004-05")

        print_all_info_using_iterator(fetcher_2004_05)

    # longer test - may want to run specific tests
    def test_iterator_on_2019_21(self):
        fetcher_2019_21 = blf.BillsOverview()
        fetcher_2019_21.update_all_bills_in_session(session_name="2019-21")

        print_all_info_using_iterator(fetcher_2019_21)
