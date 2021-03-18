import unittest

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi

class TestDetails(unittest.TestCase):
    # a much shorter test, but does not test divisions capabilities
    def test_iterator_on_2004_05_session(self):
        test_fetcher = blf.BillsOverview()
        test_fetcher.update_all_bills_in_session(session_name="2004-05")

        for s in bdi.get_bill_details(test_fetcher):
            summary, bill_divisions_list = s[0], s[1]
            print(f"summary {summary}")
            for d in bill_divisions_list:
                print(f"division name {d.division_name}")
                print(f"division stage {d.division_stage}")
                print(f"ayes {d.ayes}")
                print(f"noes {d.noes}")

    # longer test - may want to run specific tests
    def test_iterator_on_2015_16(self):
        test_fetcher = blf.BillsOverview()
        test_fetcher.update_all_bills_in_session(session_name="2015-16")

        for s in bdi.get_bill_details(test_fetcher):
            summary, bill_divisions_list = s[0], s[1]
            print(f"summary {summary}")
            for d in bill_divisions_list:
                print(f"division name {d.division_name}")
                print(f"division stage {d.division_stage}")
                print(f"ayes {d.ayes}")
                print(f"noes {d.noes}")

    # longer test - may want to run specific tests
    def test_iterator_on_2019_21(self):
        test_fetcher = blf.BillsOverview()
        test_fetcher.update_all_bills_in_session(session_name="2019-21")

        for s in bdi.get_bill_details(test_fetcher):
            summary, bill_divisions_list = s[0], s[1]
            print(f"summary {summary}")
            for d in bill_divisions_list:
                print(f"division name {d.division_name}")
                print(f"division stage {d.division_stage}")
                print(f"ayes {d.ayes}")
                print(f"noes {d.noes}")