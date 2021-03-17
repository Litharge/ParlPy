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
        skip_old_bills = True
                     ) -> list:



    division_response = fetch_votes(bill_title_stripped, start_datetime, end_datetime)
    division_obj = json.loads(division_response.text)

    division_ids = []

    for d in division_obj:
        division_ids.append(d["DivisionId"])

    return division_ids

# return response for specific division by ID
def fetch_division_values(division_id):
    specific_division_endpoint = f"https://commonsvotes-api.parliament.uk/data/division/{division_id}.json"

    response = requests.get(specific_division_endpoint)

    return response

def get_division_values(division_id):
    response = fetch_division_values(division_id)
    specific_division_obj = json.loads(response.text)

    division_title = specific_division_obj["Title"]
    print(f"division_title {division_title}")

    ayes_data = specific_division_obj["Ayes"]
    print(f"ayes_data {ayes_data}")
    ayes_ids = [a["MemberId"] for a in ayes_data]

    noes_data = specific_division_obj["Noes"]
    noes_ids = [n["MemberId"] for n in noes_data]

    # todo: better checking of title to determine what stage the division is for
    if "second reading" in division_title.lower():
        division_stage = "Second Reading"
    elif "third reading" in division_title.lower():
        division_stage = "Third Reading"
    else:
        division_stage = "Amendments"

    division_values = DivisionInformation(division_title, division_stage, ayes_ids, noes_ids)

    return division_values

class DivisionInformation():
    def __init__(self, division_name="", division_stage="", ayes=[], noes=[]):
        self.division_name = division_name
        # maybe be "Second Reading", "Third Reading", "Amendments"
        self.division_stage = division_stage
        # list of MP ids for the ayes
        self.ayes = ayes
        # list of MP ids for the noes
        self.noes = noes

# return a list of DivisionInformation objects
def get_divisions_information(bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None,
        skip_old_bills = True):
    division_ids = get_division_ids(bill_title_stripped, start_datetime, end_datetime)

    division_information_list = []

    for id in division_ids:
        division_information = get_division_values(id)
        division_information_list.append(division_information)

    return division_information_list