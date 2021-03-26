"""
Contains function to iterate over BillsOverview object, make API calls on each and yield a BillDetails object each time

Classes (public):
    BillDetails

Functions (public):
    get_bill_details

"""
import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.summary_fetcher as sf
import parlpy.utils.dates as session_dates
import parlpy.bills.bill_votes_fetcher as bvf

import datetime
from typing import List, Iterable

import pandas as pd


# class with member variables to hold information on a single bill/act
class BillDetails():
    """
    Class representing a single bill/act
    """
    def __init__(self,
                 b: pd.DataFrame,
                 summary: str,
                 divisions_list: List[bvf.DivisionInformation],
    ):
        base_url = "https://bills.parliament.uk"

        self.title_stripped = b.bill_title_stripped
        self.title_postfix = b.postfix
        self.sessions = b.session
        self.url = base_url + b.bill_detail_path
        self.last_updated = b.last_updated
        self.summary = summary
        self.divisions_list = divisions_list


# get the earliest and latest dates that the bill may have had divisions, latest is None if the session is ongoing
def get_start_and_end_dates(b):
    earliest_session = b.session[0]
    latest_session = b.session[-1]

    earliest_start_date = datetime.date.fromisoformat(
        session_dates.parliamentary_session_start_dates[earliest_session])

    try:
        latest_end_date = datetime.date.fromisoformat(
            session_dates.parliamentary_session_end_dates[latest_session])
    except TypeError:
        latest_end_date = None

    return earliest_start_date, latest_end_date


# yield a BillDetails object
def get_bill_details(overview: blf.BillsOverview, verbose=False) -> Iterable[BillDetails]:
    """
    Function to yield details on a list of bills

    :param overview: BillsOverview object containing bills to get details on
    :param debug: whether to print debug info (verbose)
    :return: yield a BillDetails object containing details on the bill
    """
    for b in overview.bills_overview_data.itertuples():
        # use the bill name and narrow results using the start and end dates to get a list of divisions results object
        title_stripped = b.bill_title_stripped
        earliest_start_date, latest_end_date = get_start_and_end_dates(b)
        divisions_data_list = bvf.get_divisions_information(title_stripped, earliest_start_date, latest_end_date)

        # get the details path and use it to get summary for the bill
        detail_path = b.bill_detail_path
        summary = sf.get_summary(detail_path)

        bill_details = BillDetails(b, summary, divisions_data_list)

        if verbose:
            print(f"{'=' * 10}")
            print("bill overview tuple")
            print(b)
            print(f"Title stripped: {bill_details.title_stripped}")
            print(f"Title postfix: {bill_details.title_postfix}")
            print(f"Last updated: {bill_details.last_updated}")
            print(f"Bill summary: {bill_details.summary}")
            print(f"Sessions: {bill_details.sessions}")
            print(f"Number of divisions: {len(bill_details.divisions_list)}")
            print(f"{'=' * 10}")

        yield bill_details
