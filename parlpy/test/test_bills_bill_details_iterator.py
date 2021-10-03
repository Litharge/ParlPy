import unittest
import datetime

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi


def print_all_info_using_iterator(fetcher):
    for s in bdi.get_bill_details(fetcher, verbose=True):
        for d in s.divisions_list:
            print(f"division name: {d.division_name}")
            print(f"division stage: {d.division_stage}")
            print(f"ayes: {d.ayes}")
            print(f"noes: {d.noes}")


def get_last_bill_details(fetcher) -> BillDetails:
    last_item = None
    for s in bdi.get_bill_details(fetcher, verbose=False):
        last_item = s

    return last_item


class TestDetails(unittest.TestCase):
    # a much shorter test, but does not test divisions capabilities
    def test_print_iterator_on_2004_05_session(self):
        fetcher_2004_05 = blf.BillsOverview()
        fetcher_2004_05.update_all_bills_in_session(session_name="2004-05")

        print_all_info_using_iterator(fetcher_2004_05)

    # longer test - may want to run specific tests
    # todo: this will need updating when the 2019- session comes to an end
    def test_print_iterator_on_2019_21(self):
        fetcher_2019_21 = blf.BillsOverview()

        mock_7_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        fetcher_2019_21.mock_datetime_last_scraped(mock_7_days_ago)
        fetcher_2019_21.get_changed_bills_in_session(session_name="2019-21")

        print_all_info_using_iterator(fetcher_2019_21)

    def test_correct_bill_stripped_title_obtained(self):
        fetcher_2019_21 = blf.BillsOverview()

        mock_datetime = datetime.datetime(2021, 9, 16, 18)
        fetcher_2019_21.mock_datetime_last_scraped(mock_datetime)
        fetcher_2019_21.get_changed_bills_in_session(session_name="2019-21")

        last_bill = get_last_bill_details(fetcher_2019_21)

        self.assertTrue(last_bill.title_stripped == "Telecommunications (Security)")

