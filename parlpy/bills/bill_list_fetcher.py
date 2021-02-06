from urllib.request import urlopen
import urllib.parse
from collections import OrderedDict
import re
import time

from bs4 import BeautifulSoup

# class that will have a method to fetch all bill titles, with its associated data:
# * associated link to further details
# * last updated date
# and will update the list by fetching each https://bills.parliament.uk page in series until the oldest updated date
# is older than the bills_df_last_updated, amending the bills_df as it does so
class BillFetcher():
    def __init__(self):
        # todo:
        #   member var ?:bills_df_last_updated
        #   member var dataframe:bill_data
        #   one for each session and one containing intersection?

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

        pass

    # get the total number of pages of bills for the selected session
    # there are many other possible methods of doing this - uncertain which is most robust
    def determine_number_pages_for_session(self, session):
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

    def fetch_all_titles_on_page(self, session, sort_order, page):
        # todo: put scheme, netloc, query mappings in member vars (or utils? - bc these macros will likely need to be
        #   used externally by api users...)
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

        titles = data_bs.find_all(class_="primary-info")

        # prints titles data todo: put in dataframe
        print(titles)
        for t in titles:
            print(t.text)

    # method to fetch overview information about all bills
    # currently fetches all bill titles in current session
    def fetch_all_bills(self):
        session = self.__bills_overview_session["2019 - 19"]

        max_page = self.determine_number_pages_for_session(session)

        sort_order = self.__bills_overview_sort_order["Updated (newest first)"]

        for i in range(1, max_page+1):
            time.sleep(1)
            self.fetch_all_titles_on_page(session, sort_order, i)
