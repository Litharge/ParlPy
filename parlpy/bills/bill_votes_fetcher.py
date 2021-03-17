"""
Robert Chambers 2021
"""

import requests
import datetime
import json

# get Response object from API, queried about divisions on a stripped title (title without the act/bill postfix)
def fetch_votes(
        bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None) -> requests.models.Response:
    votes_endpoint = 'https://commonsvotes-api.parliament.uk/data/divisions.json/search'

    votes_parameters = {'queryParameters.searchTerm': bill_title_stripped,
                        'queryParameters.startDate': start_datetime.isoformat(),
                        }

    # add end time in order to narrow results, unless end_datetime None, which is the case for the current session only
    print(f"end_datetime {end_datetime}")
    if end_datetime is not None:
        votes_parameters['queryParameters.endDate'] = end_datetime.isoformat()

    r = requests.get(votes_endpoint, params=votes_parameters)

    return r

# get a list of divisionIDs
# note that the earliest *bill* division provided by the system is 2016-03-09
# the earliest session with bill divisions recorded by the system is 2015-16
def get_division_ids(bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None,
                     ) -> list:
    division_response = fetch_votes(bill_title_stripped, start_datetime, end_datetime)
    division_obj = json.loads(division_response.text)

    division_ids = []

    for d in division_obj:
        division_ids.append(d["DivisionId"])

    return division_ids

def get_division_title
