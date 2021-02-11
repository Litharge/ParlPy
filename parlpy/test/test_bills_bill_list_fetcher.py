import parlpy.bills.bill_list_fetcher

test_fetcher = parlpy.bills.bill_list_fetcher.BillsOverview()

test_fetcher.update_all_bills_in_session()

print(test_fetcher.bills_overview_data)

print(test_fetcher.bills_overview_data[test_fetcher.bills_overview_data.bill_title == "Fire Safety Bill"])
