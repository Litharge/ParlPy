from urllib.request import urlopen
import urllib.parse
from collections import OrderedDict
import re
import time

import pandas as pd

from bs4 import BeautifulSoup

# class that will have a method to fetch all bill titles, with its associated data:
# * associated link to further details
# * last updated date
# and will update the list by fetching each https://bills.parliament.uk page in series until the oldest updated date
# is older than the bills_df_last_updated, amending the bills_df as it does so
class BillsOverview():
    def __init__(self):
        # todo:
        #   member var ?:bills_df_last_updated
        #   member var/s - one dataframe for each session and one containing intersection?
        self.bills_overview_data = pd.DataFrame([], columns=["bill_title", "last_updated", "bill_detail_path"])

        self.listed_bills_counter = 0 # debugging var

        self.__bills_overview_scheme = "https"
        self.__bills_overview_netloc = "bills.parliament.uk"

        self.__bills_overview_session = {
            "2019 - 21": "35",
            "2019 - 19": "34",
            "2017 - 19": "33"
        }
        self.__bills_overview_sort_order = {
            "Title (A-Z)": "0",
            "Updated (newest first)": "1",
            "Updated (oldest first)": "2",
            "Title (Z-A)": "3"
        }

        # a reasonable duration in seconds to delay between requesting pages
        self.__bills_overview_fetch_delay = 0.1

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
        print("url: {}".format(url))

        html_data = urlopen(url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')
        page_selection_elements = data_bs.find_all("a", href=re.compile("page=*"))

        max_page = 1 # there is always at least one page for a valid session
        for pt in page_selection_elements:
            page = int(pt["href"].split('page=')[1])

            if page > max_page:
                max_page = page

        return max_page

    def __get_title_list_from_card_tags(self, card_tags):
        titles = []
        for o in card_tags:
            title = o.find(class_="primary-info")
            titles.append(title.text)

        print(titles)

        return titles

    def __get_updated_dates_list_from_card_tags(self, card_tags):
        updated_dates = []
        for o in card_tags:
            updated_date = o.find(class_="indicators-left")
            updated_date = updated_date.text.split("updated: ")[1]
            updated_date = updated_date.splitlines()[0]
            updated_date = updated_date.rsplit(" ", 1)[0]

            print("updated date: {}".format(updated_date.encode('unicode_escape')))

            updated_dates.append(updated_date)

        print(updated_dates)

        return updated_dates

    def __get_bill_data_path_list_from_card_tags(self, card_tags):
        bill_details_paths = []
        for o in card_tags:
            bill_detail_path_tag = o.find(class_="overlay-link")
            bill_data_path = bill_detail_path_tag["href"]

            bill_details_paths.append(bill_data_path)

        print(bill_details_paths)

        return bill_details_paths

    # puts the titles, their last updated dates and bill details paths into dataframe
    def __add_page_data_to_bills_overview_data(self, titles, updated_dates, bill_details_paths):
        bill_tuple_list = []
        print(titles)
        for t in range(len(titles)):
            bill_tuple_list.append((titles[t], updated_dates[t], bill_details_paths[t]))

            self.listed_bills_counter += 1

        page_df = pd.DataFrame(bill_tuple_list, columns=["bill_title", "last_updated", "bill_detail_path"])

        new_indices = [x for x in
                       range(len(self.bills_overview_data.index), len(self.bills_overview_data.index) + len(page_df))]
        page_df.index = new_indices

        self.bills_overview_data = pd.concat([self.bills_overview_data, page_df])

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

        titles = self.__get_title_list_from_card_tags(card_tags)
        updated_dates = self.__get_updated_dates_list_from_card_tags(card_tags)
        bill_data_paths = self.__get_bill_data_path_list_from_card_tags(card_tags)
        self.__add_page_data_to_bills_overview_data(titles, updated_dates, bill_data_paths)

    # method to update self.bills_overview_data dataframe with overview information about bills from current session
    # currently gets titles only
    def update_all_bills_in_session(self):
        session = self.__bills_overview_session["2019 - 21"]

        max_page = self.__determine_number_pages_for_session(session)

        sort_order = self.__bills_overview_sort_order["Updated (newest first)"]

        for i in range(1, max_page+1):
            time.sleep(self.__bills_overview_fetch_delay)
            self.__fetch_all_overview_info_on_page(session, sort_order, i)

        print(self.bills_overview_data)
