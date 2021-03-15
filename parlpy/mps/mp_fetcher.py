import datetime
import time
import pandas as pd
import requests
import json


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=2)
    print(text)


class MPOverview:
    def __init__(self):
        self.last_updated = None
        self.api_url = "https://members-api.parliament.uk/api/"
        self.columns = [
            # Display Name
            "name_display",
            # Full Title
            "name_full_title",
            # Name to address member by
            "name_address_as",
            # Name to list member by
            "name_list_as",
            # Member ID (for further information)
            "id",
            # Gender
            "gender",
            # Party that the member belongs to
            "party_id",
            # Time this information was retrieved
            "last_updated"
        ]
        self.mp_overview_data = pd.DataFrame([], columns=self.columns)

    def __add_member_to_data_from_api_response(self, response: requests.Response):
        # jprint(response.json())
        for item in response.json()["items"]:
            value_obj = item["value"]

            values = {
                "name_display": value_obj["nameDisplayAs"],
                "name_full_title": value_obj["nameFullTitle"],
                "name_address_as": value_obj["nameAddressAs"],
                "name_list_as": value_obj["nameListAs"],
                "member_id": value_obj["id"],
                "gender": value_obj["gender"],
                "party_id": value_obj["latestParty"]["id"],
                "last_updated": datetime.datetime.now(),
            }

            self.mp_overview_data = self.mp_overview_data.append(values, ignore_index=True)

    def get_all_members(self, fetch_delay: int = 0, limit: int = None, verbose: bool = False):
        # Probably a better way of doing this? Dynamically?
        def get_n_href(res, n):
            return res.json()["links"][n]["href"]

        def get_self_href(res):
            return get_n_href(res, 0)

        def get_next_href(res):
            return get_n_href(res, 1)

        response = self.get_members()
        take = int(response.json()["take"])
        skip = 0
        while get_self_href(response) != get_next_href(response):
            # Save response to dataframe
            self.__add_member_to_data_from_api_response(response)

            # Calculate next skip
            skip += take

            # Respect limit, if it's set
            if limit is not None and skip >= limit:
                if verbose:
                    jprint(response.json())
                    print(f"Limit {limit} reached.")

                break

            # Delay if set
            if verbose:
                # Print response
                jprint(response.json())
                # Wait fetch_delay seconds
                print(f"Waiting {fetch_delay}s... ")
                time.sleep(fetch_delay)
                print("Getting...")
            else:
                time.sleep(fetch_delay)

            # Get next response
            response = self.get_members(params={"skip": skip})

        now = datetime.datetime.now()
        if verbose:
            print(f"Setting last_updated to {now}")
            print(f"Updating finished.\n")
        self.last_updated = now

    def get_members(self, params: dict = None) -> requests.Response:
        if params is None:
            params = {}

        # todo Actual name for this?
        ext = "Members/Search"

        response = requests.get(self.api_url + ext, params=params)

        return response
