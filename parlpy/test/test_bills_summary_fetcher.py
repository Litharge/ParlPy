"""
Alex Dawkins (alexander.dawkins@gmail.com) 2021
"""
# todo: make actual unit tests

from parlpy.bills.bill_list_fetcher import BillsOverview
import parlpy.bills.summary_fetcher as sf
import pandas as pd

overview = BillsOverview()
overview.update_all_bills_in_session()
path = overview.bills_overview_data.iloc[0]['bill_detail_path']

print(f"\n\nTest get_summary {' ' * 5 + '=' * 200}")
print(sf.get_summary(path))
print(f"\n\nTest append_summary {' ' * 2 + '=' * 200}")
print(sf.append_summary(overview.bills_overview_data.iloc[0]))
print(f"\n\nTest append_summaries {'=' * 200}")
print(sf.append_summaries(overview))
