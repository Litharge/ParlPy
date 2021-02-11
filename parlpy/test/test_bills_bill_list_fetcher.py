import pandas as pd

import parlpy.bills.bill_list_fetcher

test_fetcher = parlpy.bills.bill_list_fetcher.BillsOverview()

test_fetcher.update_all_bills_in_session()

# display all columns of dataframe
pd.set_option("display.max_columns", len(test_fetcher.bills_overview_data.columns))

print(test_fetcher.bills_overview_data)

print(test_fetcher.bills_overview_data[test_fetcher.bills_overview_data.bill_title == "Fire Safety Bill"])
