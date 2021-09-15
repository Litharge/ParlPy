"""
Contains class that specifies how basic data on bills is collected and represented

Classes (public):
    BillsOverview
"""
from urllib.request import urlopen
import urllib.parse
from collections import OrderedDict
import re
import time
import datetime
import pickle
import os

import pandas as pd
import numpy

from bs4 import BeautifulSoup

import gcsfs


class BillsOverview():
    """Class representing basic bill data, mainly to do with the existence of bills so we know what API calls to make

    This class is used to find the existence of bills, it is not data that is intended to be used standalone, an object
    of this type can then be passed to parlpy.bills.bill_details_iterator_get_bill_details to get the details on a
    bill

    Attributes (public)
    ----------
    bills_overview_data : dataframe
        data on bills when one of the public methods has run
    run_on_app_engine : bool
        determines what type of pickle to use, if true the gcsfs
    project_name : str
        what google cloud project name to use
    debug : bool
        whether to print debug info

    Methods (public)
    ----------
    update_all_bills_in_session(session_name="2019-21", fetch_delay=0,)
        insert into bills_overview_data all bills with their basic info for a given session
    get_changed_bills_in_session(session_name="2019-21", fetch_delay=0)
        insert into bills_overview_data only bills updated since datetime_last_scraped.p, then updates/creates pickle
    reset_datetime_last_scraped()
        reset datetime_last_scraped.p pickle
    mock_datetime_last_scraped(mock_datetime: datetime.datetime)
        set datetime_last_scraped.p pickle
    """
    def __init__(self, run_on_app_engine=False, project_name=None, debug=False):
        # whether to use gcsfs
        self.run_on_app_engine = run_on_app_engine

        # what project to use
        self.project_name = project_name

        # whether to print output as it is collected
        self.debug = debug

        self.bills_overview_data = pd.DataFrame([], columns=["bill_title_stripped", "postfix", "last_updated", "bill_detail_path", "session"])

        # debugging vars
        self.pages_updated_this_update = 0
        self.listed_bills_counter = 0

        self.__bills_overview_scheme = "https"
        self.__bills_overview_netloc = "bills.parliament.uk"

        self.__bills_overview_session = {
            "All": "0",
            "2019-21": "35",
            "2019-19": "34", # a jump here for unknown reason
            "2017-19": "30",
            "2016-17": "29",
            "2015-16": "28",
            "2014-15": "27",
            "2013-14": "26",
            "2012-13": "25",
            "2010-12": "24",
            "2009-10": "23",
            "2008-09": "22",
            "2007-08": "21",
            "2006-07": "20",
            "2005-06": "19",
            "2004-05": "18"
        }

        # todo: determine these codes automatically
        self.__bills_overview_sort_order = {
            "Title (A-Z)": "0",
            "Title (Z-A)": "1",
            "Updated (oldest first)": "2",
            "Updated (newest first)": "3"
        }

    # get the total number of pages of bills for the selected session
    # there are many other possible methods of doing this - uncertain which is most robust
    def __determine_number_pages_for_session(self, session):
        page_query_string = urllib.parse.urlencode(
            OrderedDict(
                Session=session
            )
        )

        url = urllib.parse.urlunparse((
            self.__bills_overview_scheme, self.__bills_overview_netloc, "", "", page_query_string, ""
        ))

        html_data = urlopen(url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')
        page_selection_elements = data_bs.find_all("a", href=re.compile("page=*"))

        max_page = 1 # there is always at least one page for a valid session
        for pt in page_selection_elements:
            page = int(pt["href"].split('page=')[1])

            if page > max_page:
                max_page = page

        if self.debug:
            print("max page = {}".format(max_page))

        return max_page


    def __get_title_stripped_and_postfix_list_from_card_tags(self, card_tags):
        # list containing 2-tuples of form
        # if title is "xyz Bill" then the first element of tuple is "xyz" and second element of tuple is "Bill"
        # if title is "xyz Act 20ab" then the first element of tuple is "xyz" and second element of tuple is "Act 20ab"
        # note that bill/act xyz may have title like:
        # * "abc act 19uw (def) bill 20ab"
        # * "abc act 19uw (def) act 20ab"
        titles_stripped = []
        postfixes = []
        for o in card_tags:
            title = o.find(class_="primary-info").text
            # remove trailing "[HL]" if present
            title_hl_removed = title.rsplit(" [HL]", 1)[0]

            # split using the last occurrence of "Act" in the title
            # this works for legislation with title "xyz Act 19/20ab" or "def Act 19/20gh ... Act 19/20ab"
            if "Act" in title_hl_removed and "Bill" not in title_hl_removed:
                title_stripped = title_hl_removed.rsplit(" Act", 1)[0]
                # get the "Act 20/19ab" part
                postfix = title_hl_removed.split(title_stripped, 1)[1]
                postfix = postfix[1:]

            # split using the last occurrence of "Bill" in the title
            # this works for legislation with title "xyz Bill" or "def Act 19/20gh ... Bill"
            elif "Bill" in title_hl_removed:
                title_stripped = title_hl_removed.rsplit(" Bill", 1)[0]
                postfix = "Bill"

            # special case for all caps
            elif "ACT" in title_hl_removed:
                title_stripped = title_hl_removed.rsplit(" ACT", 1)[0]
                # get the "Act 20/19ab" part
                postfix = title_hl_removed.split(title_stripped, 1)[1]
                postfix = postfix[1:]

            # special case for all caps
            elif "BILL" in title_hl_removed:
                title_stripped = title_hl_removed.rsplit(" BILL", 1)[0]
                postfix = "BILL"

            else:
                title_stripped = None
                postfix = None

            if title_stripped is not None:
                titles_stripped.append(title_stripped)
                postfixes.append(postfix)

        return titles_stripped, postfixes


    def __get_updated_dates_list_from_card_tags(self, card_tags):
        updated_dates = []
        for o in card_tags:
            updated_date = o.find(class_="indicators-left")
            updated_date = updated_date.text.split("updated: ")[1]
            updated_date = updated_date.splitlines()[0]
            updated_date = updated_date.rsplit(" ", 1)[0]

            updated_date_datetime = datetime.datetime.strptime(updated_date, '%d %B %Y at %H:%M')

            updated_dates.append(updated_date_datetime)

        return updated_dates


    def __get_bill_data_path_list_from_card_tags(self, card_tags):
        bill_details_paths = []
        for o in card_tags:
            bill_detail_path_tag = o.find(class_="overlay-link")
            bill_data_path = bill_detail_path_tag["href"]

            bill_details_paths.append(bill_data_path)

        return bill_details_paths

    def __get_bill_sessions_list_from_card_tags(self, card_tags):
        bill_sessions = []
        for o in card_tags:
            # get text of form "Session 20xx-yy, 20ww-zz..."
            sessions = o.find(class_="secondary-info")
            sessions_text = sessions.text
            # put into list with members of form 20aa-bb
            sessions_text = sessions_text.split(" ", maxsplit=1)[1]
            sessions_list = sessions_text.split(", ")
            bill_sessions.append(sessions_list)

        return bill_sessions

    def put_bill_info_in_list_into_bills_overview_data(self, bill_tuple_list):
        if len(bill_tuple_list) > 0:
            bill_tuple_arr = numpy.array(bill_tuple_list, dtype=object)

            page_df = pd.DataFrame(bill_tuple_arr, columns=["bill_title_stripped", "postfix", "last_updated", "bill_detail_path", "session"])

            new_indices = [x for x in
                           range(len(self.bills_overview_data.index), len(self.bills_overview_data.index) + len(page_df))]
            page_df.index = new_indices

            self.bills_overview_data = pd.concat([self.bills_overview_data, page_df])

            if self.debug:
                print("last item on page: {}".format(page_df.iloc[-1]))

    # puts the partial dataframe containing titles, their last updated dates and bill details paths into dataframe
    # member variable bills_overview_data
    # if check_last_updated, only add up to the point that the bill's updated date is newer than our scraper last
    # updated
    def __add_page_data_to_bills_overview_data(
            self,
            titles_stripped,
            postfixes,
            updated_dates,
            bill_details_paths,
            bill_sessions,
            check_last_updated=True):
        bill_tuple_list = []

        if self.run_on_app_engine:
            fs = gcsfs.GCSFileSystem(project=self.project_name)
            try:
                with fs.open(f"{self.project_name}.appspot.com" + "/" + "datetime_last_scraped.p", "rb") as handle:
                    loaded_datetime_last_scraped = pickle.load(handle)
            except (FileNotFoundError) as e:
                # this is the case if the pickle file has been manually deleted, or if this is the first time
                # get_changed_bills_in_session is running
                loaded_datetime_last_scraped = None
        else:
            try:
                with open("datetime_last_scraped.p", "rb") as f:
                    loaded_datetime_last_scraped = pickle.load(f)
            except (FileNotFoundError) as e:
                # this is the case if the pickle file has been manually deleted, or if this is the first time
                # get_changed_bills_in_session is running
                loaded_datetime_last_scraped = None

        for i in range(len(titles_stripped)):
            if loaded_datetime_last_scraped != None and check_last_updated:
                delta_from_last_update_call = loaded_datetime_last_scraped - updated_dates[i]
                if self.debug:
                    print("bill title: {}".format(titles_stripped[i]))
                    print("bill updated date: {} type {}".format(updated_dates[i], type(updated_dates[i])))
                    print("last updated: {}".format(loaded_datetime_last_scraped))
                # if bill found that was last updated since we last checked, return, we have added all the newest ones
                if delta_from_last_update_call.total_seconds() > 0:
                    if self.debug:
                        print("found newest bill NOT updated recently (first to be discarded)")
                        print("delta in seconds {}".format(delta_from_last_update_call.total_seconds()))
                        print(titles_stripped[i])
                        print(updated_dates[i])

                    self.put_bill_info_in_list_into_bills_overview_data(bill_tuple_list)

                    got_all_updated_bills = True
                    return got_all_updated_bills

                else:
                    if self.debug:
                        print("found bill updated recently {}".format(titles_stripped[i]))

            bill_tuple_list.append(
                (titles_stripped[i],
                 postfixes[i],
                 updated_dates[i],
                 bill_details_paths[i],
                 bill_sessions[i])
            )

            self.listed_bills_counter += 1

        self.put_bill_info_in_list_into_bills_overview_data(bill_tuple_list)

        # last item was updated since we last called, so proceed to next page
        return False

    # adds bill overview information to self.bills_overview_data
    def __fetch_all_overview_info_on_page(self, session, sort_order, page):
        page_query_string = urllib.parse.urlencode(
            OrderedDict(
                Session=session,
                BillSortOrder=sort_order,
                page=str(page),
            )
        )

        url = urllib.parse.urlunparse((
            self.__bills_overview_scheme, self.__bills_overview_netloc, "", "", page_query_string, ""
        ))

        html_data = urlopen(url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')

        card_tags = data_bs.find_all(class_="card-clickable")

        (titles_stripped, postfixes) = self.__get_title_stripped_and_postfix_list_from_card_tags(card_tags)
        updated_dates = self.__get_updated_dates_list_from_card_tags(card_tags)
        bill_data_paths = self.__get_bill_data_path_list_from_card_tags(card_tags)
        sessions = self.__get_bill_sessions_list_from_card_tags(card_tags)

        # list of titles, list of updated_dates, list of bill_data_paths, list of list of sessions
        return (titles_stripped, postfixes, updated_dates, bill_data_paths, sessions)


    def __update_bills_overview_up_to_page(self, session_code, max_page, fetch_delay, smart_update=True):
        # get in order of updated, because update_bills_overview_up_to_page is planned to only crawl pages with
        # bills updated since the method was last called
        sort_order_code = self.__bills_overview_sort_order["Updated (newest first)"]

        for i in range(1, max_page+1):
            time.sleep(fetch_delay)

            (titles_stripped, postfixes, updated_dates, bill_data_paths, bill_sessions) \
                = self.__fetch_all_overview_info_on_page(session_code, sort_order_code, i)

            self.__add_page_data_to_bills_overview_data(titles_stripped, postfixes, updated_dates, bill_data_paths,
                                                        bill_sessions, check_last_updated=False)


    def update_all_bills_in_session(
            self,
            session_name="2019-21",
            fetch_delay=0,
    ):
        """
        Put all bills in session into self.bills_overview_data

        :param session_name: str to determine session, eg "2004-05"... or "All"
        :param fetch_delay: int how many miliseconds to delay between scrapes
        """
        # reset df
        self.bills_overview_data = pd.DataFrame([], columns=["bill_title_stripped", "postfix", "last_updated", "bill_detail_path", "session"])

        # get the integer string corresponding to session string
        session_code = self.__bills_overview_session[session_name]

        max_page = self.__determine_number_pages_for_session(session_code)

        self.__update_bills_overview_up_to_page(session_code, max_page, fetch_delay)

    def __update_bills_overview_with_updated_bills_only_up_to_page(self, session_code, max_page, fetch_delay, debug=False):
        sort_order_code = self.__bills_overview_sort_order["Updated (newest first)"]

        for i in range(1, max_page + 1):
            time.sleep(fetch_delay)
            (titles_stripped, postfixes, updated_dates, bill_data_paths, bill_sessions) \
                = self.__fetch_all_overview_info_on_page(session_code, sort_order_code, i)

            if debug:
                print(f"(titles_stripped, postfixes, updated_dates, bill_data_paths, bill_sessions) for page {i}: {(titles_stripped, postfixes, updated_dates, bill_data_paths, bill_sessions)}")

            got_all_updated_bills = self.__add_page_data_to_bills_overview_data(titles_stripped, postfixes,
                                                                                updated_dates, bill_data_paths,
                                                                                bill_sessions, check_last_updated=True)
            # if we have all the bills which were updated since we last checked, no need to check any more pages
            if got_all_updated_bills:
                break

        # store the current datetime for future use, so we know we have just scraped
        to_store_datetime_last_scraped = datetime.datetime.now()
        if self.debug:
            print("saving to_store_datetime_last_scraped {}".format(to_store_datetime_last_scraped))
        if self.run_on_app_engine:
            fs = gcsfs.GCSFileSystem(project=self.project_name)
            with fs.open(f"{self.project_name}.appspot.com" + "/" + "datetime_last_scraped.p", "wb") as handle:
                pickle.dump(to_store_datetime_last_scraped, handle)
        else:
            with open("datetime_last_scraped.p", "wb") as f:
                pickle.dump(to_store_datetime_last_scraped, f)

    # this method uses a pickled variable (so that ths package can be run periodically)
    # puts into self.bills_overview_data, bills which have been updated since the method was last called
    # these can then be compared to values in a database for example
    def get_changed_bills_in_session(self, session_name="2019-21", fetch_delay=0, debug=False):
        """
        Method to update self.bills_overview_data, but only those updated since the time in datetime_last_scraped.p

        Method behaves like update_all_bills_in_session on its first run or after reset_datetime_last_scraped called,
        after loading data into self.bills_overview_data it updates the pickle file so that the next time it runs it
        only gets new bills
        :param session_name:
        :param fetch_delay:
        """
        # reset df ready for new data
        self.bills_overview_data = pd.DataFrame([], columns=["bill_title_stripped", "postfix", "last_updated", "bill_detail_path", "session"])

        session_code = self.__bills_overview_session[session_name]

        max_page = self.__determine_number_pages_for_session(session_code)

        if debug:
            print("session code ", session_code)
            print("max page ", max_page)

        self.__update_bills_overview_with_updated_bills_only_up_to_page(session_code, max_page, fetch_delay, debug=debug)


    def reset_datetime_last_scraped(self):
        """
        Delete datetime_last_scraped.p if it exists
        """
        if self.run_on_app_engine:
            fs = gcsfs.GCSFileSystem(project=self.project_name)
            if fs.exists(f"{self.project_name}.appspot.com" + "/" + "datetime_last_scraped.p"):
                fs.rm(f"{self.project_name}.appspot.com" + "/" + "datetime_last_scraped.p")
        else:
            if os.path.exists("datetime_last_scraped.p"):
                os.remove("datetime_last_scraped.p")
            else:
                print("datetime last scraped not recorded")


    def mock_datetime_last_scraped(self, mock_datetime: datetime.datetime):
        """
        Save a given datetime as last scraped

        :param mock_datetime: datetime to save
        """
        if self.run_on_app_engine:
            fs = gcsfs.GCSFileSystem(project=self.project_name)
            with fs.open(f"{self.project_name}.appspot.com" + "/" + "datetime_last_scraped.p", "wb") as handle:
                pickle.dump(mock_datetime, handle)
        else:
            with open("datetime_last_scraped.p", "wb") as f:
                pickle.dump(mock_datetime, f)