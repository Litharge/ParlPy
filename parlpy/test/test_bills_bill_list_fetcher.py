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
        test_fetcher = BillsOverview(debug=False)
        #test_fetcher.update_all_bills_in_session()

        self.test_fetcher = test_fetcher

        pd.set_option("display.max_columns", len(self.test_fetcher.bills_overview_data.columns))

        #print(self.test_fetcher.bills_overview_data)

    def test_update_only_needed(self):
        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)

        time.sleep(5)

        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)

    """
    # test types of dataframe
    def test_dataframe_types(self):
        self.assertIsInstance(self.test_fetcher.bills_overview_data, pd.DataFrame)

        print(self.test_fetcher.bills_overview_data.dtypes)

        # strings are stored as objects in dataframes
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_title.dtype == object)
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_detail_path.dtype == object)

        # check that last_updated is stored as datetime64[ns]
        self.assertTrue(self.test_fetcher.bills_overview_data.last_updated.dtype == np.dtype('datetime64[ns]'))
    """


    """
    # test dataframe update procedure:
    # * times (first scrape should be older than second scrape)
    # * todo: number of bills updated (first scrape should have more bills updated than second scrape)
    # * todo: number of pages visited during scrape (first should visit more pages than second)
    def test_update_procedure(self):
        first_update_time = self.test_fetcher.last_updated

        self.test_fetcher.update_all_bills_in_session()
        second_update_time = self.test_fetcher.last_updated

        delta = second_update_time - first_update_time
        self.assertTrue(delta.total_seconds() > 0)

        print(self.test_fetcher.bills_overview_data)
    """

    # todo: create hand made bills html data to check that update is working



if __name__ == '__main__':
    unittest.main()