# ParlPy

Package to scrape and process UK Parliamentary bills, votes and MP contact information.

Written as part of University of Bath Integrated Project module. 

---

# Usage

## Install

    pipenv install ParlPy==1.1.0

## Intended Usage

A list of bills to collect information about is generated using either the `update_all_bills_in_session` or the 
`get_changed_bills_in_session` methods of a BillsOverview object from parlpy.bills.bill_list_fetcher. The former 
simply gets a list of all bills and places them in member DataFrame `bills_overview_data`. The latter has persistence, 
so that its first run behaves like `update_all_bills_in_session`, but after this places only bills updated after it 
was last run in the DataFrame.

The BillsOverview object is then passed to todo: iterator

## Intended Example Usage
    
    import parlpy.bills.bill_list_fetcher as blf
    import parlpy.bills.bill_details_iterator as bdi

    test_fetcher = blf.BillsOverview()
    test_fetcher.get_changed_bills_in_session()

    for s in bdi.get_bill_details(test_fetcher):
        summary, bill_divisions_list = s[0], s[1]
        print(f"summary {summary}")
        for d in bill_divisions_list:
            print(f"division name {d.division_name}")
            print(f"division stage {d.division_stage}")
            print(f"ayes {d.ayes}")
            print(f"noes {d.noes}")
    
    # ...
    # repeat

The above gets summary and a list of DivisionDetail objects for each bill. BillsOverview has persistence, storing the
last time `get_changed_bills_in_session` was called using a pickle variable. So eg the script can be run, the values
stored in a DB, then run again later to get info on bills that the parliamentary website says have updated.

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

# 1.1.0
* add function to get parties and their corresponding ids

## 1.0.1
* improve accuracy of associating divisions with bills

## 1.0.0
* add iterator functionality to get details on bills provided by a BillsOverview object

## 0.1.0
* adds method to get a list only of bills updated since method was last run, uses pickled datetime so that script can
 be stopped and run as required

## 0.0.2
* gets a DataFrame containing bill titles, their last updated times and page paths (page paths to be used in
  future versions)
* page request delay configurable
