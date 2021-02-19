import pandas as pd
import datetime
import numpy as np

from parlpy.bills.bill_list_fetcher import BillsOverview

import unittest


class TestOverview(unittest.TestCase):
    # create BillsOverview object ready for tests
    # also print result
    def setUp(self):
        test_fetcher = BillsOverview(debug=True)
        test_fetcher.update_all_bills_in_session()

        self.test_fetcher = test_fetcher

        pd.set_option("display.max_columns", len(self.test_fetcher.bills_overview_data.columns))

        print(self.test_fetcher.bills_overview_data)

        print(self.test_fetcher.bills_overview_data[
                  self.test_fetcher.bills_overview_data.bill_title == "Fire Safety Bill"
                  ])

    # test types of dataframe
    def test_dataframe_types(self):
        self.assertIsInstance(self.test_fetcher.bills_overview_data, pd.DataFrame)

        print(self.test_fetcher.bills_overview_data.dtypes)

        # strings are stored as objects in dataframes
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_title.dtype == object)
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_detail_path.dtype == object)

        # check that last_updated is stored as datetime64[ns]
        self.assertTrue(self.test_fetcher.bills_overview_data.last_updated.dtype == np.dtype('datetime64[ns]'))


if __name__ == '__main__':
    unittest.main()