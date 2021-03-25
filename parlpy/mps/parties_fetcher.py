"""
Contains function to get a list of PartyInformation objects describing all parties

Classes (public):
    PartyInformation

Functions (public):
    get_all_parties
"""
import requests
import json


class PartyInformation():
    """
    Class to represent information on a party

    Attributes (public):
    ---------
    party_name: str
        party name corresponing to id
    party_id: str
    """
    def __init__(self, party_name: str, party_id: int):
        self.party_name = party_name
        self.party_id = party_id


def get_all_parties():
    """
    Function that returns a list of PartyInformation objects containing information on all parties with active MPs
    :return: list of PartyInformation objects for all parties with MPs
    """
    commons_parties_endpoint = "https://members-api.parliament.uk/api/Parties/GetActive/Commons"

    r = requests.get(commons_parties_endpoint)
    parties_object = json.loads(r.text)

    parties_items_object = parties_object["items"]

    # list holding PartiesInformation objects
    parties_list = []
    for p in parties_items_object:
        party_id = p["value"]["id"]
        party_name = p["value"]["name"]

        party_obj = PartyInformation(party_name, party_id)
        parties_list.append(party_obj)

    return parties_list
