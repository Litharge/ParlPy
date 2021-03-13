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
        self.bills_overview_data = pd.DataFrame([], columns=["bill_title", "last_updated", "bill_detail_path"])

    def get_all_members(self, fetch_delay: int = 0, limit: int = None, verbose: bool = False):
        # Probably a better way of doing this? Dynamically?
        def get_n_href(res, n):
            return res.json()["links"][n]["href"]

        def get_self_href(res):
            return get_n_href(res, 0)

        def get_next_href(res):
            return get_n_href(res, 1)

        responses = []
        response = self.get_members()
        take = int(response.json()["take"])
        skip = 0
        while get_self_href(response) != get_next_href(response):

            # Calculate next skip
            skip += take

            # Save response to array
            responses.append(response.json())

            # Respect limit, if it's set
            if limit is not None and skip > limit:
                if verbose:
                    jprint(response.json())
                    print(f"Limit {limit} reached.")

                break

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

        self.last_updated = datetime.datetime.now()
        print(responses)

    def get_members(self, params: dict = None) -> requests.Response:
        if params is None:
            params = {}

        # todo Actual name for this?
        ext = "Members/Search"

        response = requests.get(self.api_url + ext, params=params)

        return response
