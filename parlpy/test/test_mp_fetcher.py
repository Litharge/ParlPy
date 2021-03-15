from parlpy.mps.mp_fetcher import MPOverview
import json


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=2)
    print(text)


mp = MPOverview()
mp.get_all_members(verbose=True, limit=20)
print(mp.mp_overview_data)