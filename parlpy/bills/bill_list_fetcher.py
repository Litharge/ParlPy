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
        self.bills_overview_scheme = "https"
        self.bills_overview_netloc = "bills.parliament.uk"
        pass

    # get the total number of pages of bills for the selected session
    # there are many other possible methods of doing this - uncertain which is most robust
    def determine_number_pages_for_session(self, session):
        url = urllib.parse.urlunparse((
            self.bills_overview_scheme, self.bills_overview_netloc, "", "", "", ""
        ))

        html_data = urlopen(url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')
        page_selection_elements = data_bs.find_all("a", href=re.compile("/\?page=*"))

        max_page = 1 # there is always at least one page for a valid session
        for pt in page_selection_elements:
            page = int(pt["href"].split('=')[1])

            if page > max_page:
                max_page = page

        return max_page

    def fetch_all_titles_on_page(self, page):
        # todo: put scheme, netloc, query mappings in member vars (or utils? - bc these macros will likely need to be
        #   used externally by api users...)
        page_query_string = urllib.parse.urlencode(OrderedDict(page=str(page)))
        url = urllib.parse.urlunparse((
            self.bills_overview_scheme, self.bills_overview_netloc, "", "", page_query_string, ""
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
        max_page = self.determine_number_pages_for_session(1)

        for i in range(1, max_page+1):
            time.sleep(1)
            self.fetch_all_titles_on_page(i)
