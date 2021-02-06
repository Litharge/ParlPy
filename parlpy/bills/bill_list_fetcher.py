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
        #  member var bills_df_last_updated
        #  member var dataframe:bill_data
        self.bills_url = "https://bills.parliament.uk"
        pass

    def fetch_all_titles_on_page(self, page):
        html_data = urlopen(self.bills_url+"/?page="+str(page))

        data_bs = BeautifulSoup(html_data.read(), 'html.parser')

        titles = data_bs.find_all(class_="primary-info")

        print(titles)
        for t in titles:
            print(t.text)

    # method to fetch overview information about all bills
    # currently fetches all bill titles in current session
    def fetch_all_bills(self):
        html_data = urlopen(self.bills_url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')
        page_selection_elements = data_bs.find_all("a", href=re.compile("/\?page=*"))

        max = 1
        for pt in page_selection_elements:
            page = int(pt["href"].split('=')[1])

            if page > max:
                max_page = page

        for i in range(1, max_page+1):
            time.sleep(1)
            self.fetch_all_titles_on_page(i)


