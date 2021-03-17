"""
Robert Chambers 2021
"""

import requests
import datetime

def fetch_votes(bill_title: str, start_datetime: datetime.date, end_datetime: datetime.date = None) -> requests.Request:
    votes_endpoint = 'https://commonsvotes-api.parliament.uk/data/divisions.json/search'

    votes_parameters = {'queryParameters.searchTerm': bill_title,
                        'queryParameters.startDate': start_datetime.isoformat(),
                        }

    # add end time to narrow results, unless end_datetime None, which is the case for the current session only
    if end_datetime is not None:
        votes_parameters['queryParameters.endDate': end_datetime.isoformat()]

    r = requests.get(votes_endpoint, params=votes_parameters)

    return r