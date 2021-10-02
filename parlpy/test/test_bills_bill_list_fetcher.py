import datetime
import time

import pandas as pd
import numpy as np

from parlpy.bills.bill_list_fetcher import BillsOverview

import unittest


class TestOverview(unittest.TestCase):
    # create BillsOverview object ready for tests
    # also print result
    def setUp(self):
        self.test_fetcher = BillsOverview(debug=False)

        pd.set_option("display.max_columns", len(self.test_fetcher.bills_overview_data.columns))

    # check that the first call to get_changed_bills_in_session puts more or equal items into bill_overview_data
    # than the second
    def test_update_only_needed(self):
        self.test_fetcher.reset_datetime_last_scraped()

        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")
        df_row_count_1 = len(self.test_fetcher.bills_overview_data.index)

        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")
        df_row_count_2 = len(self.test_fetcher.bills_overview_data.index)

        self.assertTrue(df_row_count_1 >= df_row_count_2)

    # test types of dataframe
    def atest_dataframe_types(self):
        self.test_fetcher.update_all_bills_in_session()
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")

        self.assertIsInstance(self.test_fetcher.bills_overview_data, pd.DataFrame)

        print(self.test_fetcher.bills_overview_data.dtypes)

        # strings are stored as objects in dataframes
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_title_stripped.dtype == object)
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_detail_path.dtype == object)

        # check that last_updated is stored as datetime64[ns]
        self.assertTrue(self.test_fetcher.bills_overview_data.last_updated.dtype == np.dtype('datetime64[ns]'))

    def test_mock_datetime_last_scraped_prevents_all(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime_now = datetime.datetime.now()
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime_now)

        self.test_fetcher.get_changed_bills_in_session(session_name="All", debug=True)

        df_row_count = len(self.test_fetcher.bills_overview_data.index)
        self.assertTrue(df_row_count == 0)

    def test_mock_datetime_last_scraped_prevents_some(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime_year_ago = datetime.datetime.now() - datetime.timedelta(30)
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime_year_ago)

        self.test_fetcher.get_changed_bills_in_session(session_name="All", debug=True)

        df_row_count = len(self.test_fetcher.bills_overview_data.index)
        self.assertTrue(df_row_count != 0)

    # check that (using a mock datetime last scraped) that the oldest bill is correct (can not check newest - this is
    # not fixed)
    def test_correct_bills_scraped(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime = datetime.datetime(2021, 9, 16, 18)
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime)

        self.test_fetcher.get_changed_bills_in_session(session_name="2019-21")

        self.assertTrue(self.test_fetcher.bills_overview_data.iloc[-1]["bill_title_stripped"] == "Telecommunications (Security)")

    def test_correct_house_commons(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime = datetime.datetime(2021, 9, 16, 18)
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime)

        self.test_fetcher.get_changed_bills_in_session(session_name="2021-22")

        self.assertTrue(
            self.test_fetcher.bills_overview_data.iloc[-1]["originating_house"] == BillsOverview.OriginatingHouse.HOUSE_OF_COMMONS)

    def test_correct_house_lords(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime = datetime.datetime(2021, 9, 15, 13)
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime)

        self.test_fetcher.get_changed_bills_in_session(session_name="2021-22")

        self.assertTrue(
            self.test_fetcher.bills_overview_data.iloc[-1]["originating_house"] == BillsOverview.OriginatingHouse.HOUSE_OF_LORDS)


if __name__ == '__main__':
    unittest.main()