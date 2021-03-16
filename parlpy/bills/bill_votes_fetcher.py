"""
Robert Chambers 2021
"""

import requests
import datetime

def fetch_votes(bill_title: str, start_datetime: datetime.date, end_datetime: datetime.date) -> requests.Request:
    votes_endpoint = 'https://commonsvotes-api.parliament.uk/data/divisions.json/search'

    votes_parameters = {'queryParameters.searchTerm': bill_title}

    r = requests.get(votes_endpoint, params=votes_parameters)

    return r