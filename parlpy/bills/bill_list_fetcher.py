from urllib.request import urlopen
from bs4 import BeautifulSoup

class BillFetcher():
    def __init__(self):
        # todo:
        #  member var time_last_updated
        #  member var dataframe:bill_data
        pass

    # method to fetch overview information about all bills
    def fetch_all_bills(self):
        html_data = urlopen("https://bills.parliament.uk/")
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')
        titles = data_bs.find_all(class_="primary-info")
        print(titles)
        for t in titles:
            print(t.text)
