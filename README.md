# ParlPy

Package to scrape and process UK Parliamentary bills, votes and MP contact information.

Written as part of University of Bath Integrated Project module. 

---

# Usage

## Install

    pipenv install ParlPy==0.1.0

## Intended Usage

A list of bills to collect information about is generated using either the `update_all_bills_in_session` or the 
`get_changed_bills_in_session` methods of a BillsOverview object from parlpy.bills.bill_list_fetcher. The former 
simply gets a list of all bills and places them in member DataFrame `bills_overview_data`. The latter has persistence, 
so that its first run behaves like `update_all_bills_in_session`, but after this places only bills updated after it 
was last run in the DataFrame.

The BillsOverview object is then passed to todo: iterator

## Example Usage

To fetch bills updated since our scraper was last called (uses pickled variable for persistence between program runs)

    from parlpy.bills.bill_list_fetcher import BillsOverview

    test_fetcher = BillsOverview()
    test_fetcher.get_changed_bills_in_session(session_name="All")
    print(test_fetcher.bills_overview_data)

... script can stop and be rerun later, next time bills_overview_data will contain fewer items, unless 
reset_datetime_last_scraped() has been called first, which deletes the pickle file

To fetch all bills and print them:

    from parlpy.bills.bill_list_fetcher import BillsOverview
    
    test_fetcher2 = BillsOverview()
    test_fetcher2.update_all_bills_in_session()
    print(test_fetcher2.bills_overview_data)

---

# Subpackages

## parlpy.bills 
parlpy.bills for fetching bill data


### Class: BillsOverview

Constructs an object for collecting basic information on all bills in the current Parliamentary session. Its purpose is
to
* get a list of existing bills - so that we know what to scrape
* get path to further details for each bill - so that we can assemble the url to scrape further info from


Public instance variables:
* DataFrame : bills_overview_data 
  
    DF containing bill titles, their last updated time and the path to further
details on the bill
  
Public instance methods:
* None : get_changed_bills_in_session(session_name="2019-21", fetch_delay=0)
* None : reset_datetime_last_scraped()
* None : update_all_bills_in_session(session_name="2019-21", fetch_delay=0)

    Method to called to update self.bills_overview_data, fetching pages at maximum rate when fetch_delay=0

---

# Data Sources and Rationale

A list of extant bills and acts are scraped from https://bills.parliament.uk. Scraping was the only choice for
collecting this list as outlined in the bullet points below
* There is an official RSS feed, however
this only lists the 50 most recently updated bills, so we do not use this source as we would not have been able to 
collect older bills.
  
* The API at https://explore.data.parliament.uk/?endpoint=bills does not contain bills more recent 
than 2018, so we do not utilise this as it does not present new bills. 
  
* The recent API https://developer.parliament.uk/
does not provide bills.

The package however does make use of the official UK Parliamentary API for collecting division data and for collecting 
data on MP's.

## parlpy.bills.bill_list_fetcher 
`BillsOverview.get_changed_bills_in_session()` and `BillsOverview.update_all_bills_in_session()`

Both scrape data from https://bills.parliament.uk

## parlpy.bills.bill_summary_fetcher
`get_summary()`

Scrapes data from https://bills.parliament.uk

---

# Versions

## 0.1.0
* adds method to get a list only of bills updated since method was last run, uses pickled datetime so that script can
 be stopped and run as required

## 0.0.2
* gets a DataFrame containing bill titles, their last updated times and page paths (page paths to be used in
  future versions)
* page request delay configurable
