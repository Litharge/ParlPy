# ParlPy

Package to scrape and process UK Parliamentary bills, votes and MP contact information.

Written as part of University of Bath Integrated Project module. 

---

# Usage

## Install

    pipenv install ParlPy

## Example Usage

To fetch all bills in session and print them:

    from parlpy.bills.bill_list_fetcher import BillsOverview
    
    test_fetcher = BillsOverview()
    test_fetcher.update_all_bills_in_session()
    print(test_fetcher.bills_overview_data)

---

# Subpackages

## parlpy.bills 
parlpy.bills for fetching bill data


### Class: BillsOverview

Constructs an object for collecting basic information on all bills in the current Parliamentary session


Public instance variables:
* DataFrame : bills_overview_data 
  
    DF containing bill titles, their last updated time and the path to further
details on the bill
  
Public instance methods:
* None : update_all_bills_in_session(fetch_delay=0)

    Method to called to update self.bills_overview_data, fetching pages at maximum rate when fetch_delay=0

---

# Data Sources

## BillsOverview()

Fetches data from https://bills.parliament.uk

---

# Versions

## 0.0.2
* gets a DataFrame containing bill titles, their last updated times and page paths (page paths to be used in
  future versions)
* page request delay configurable
