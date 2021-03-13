import urllib.parse
from collections import OrderedDict
from urllib.request import urlopen
from bs4 import BeautifulSoup

import pandas as pd


class MPOverview:
    def __init__(self):
        self.__mp_overview_scheme = "https"
        self.__mp_overview_netloc = "members.parliament.uk"
        self.__gender = {
            "Any": "Any",
            "Male": "Male",
            "Female": "Female",
            "Non-binary": "Nonbinary",
        }
        # New random number generator idea: Use the government's party id
        # todo: scrape this from website? Might change
        self.__party_id = {
            "All": "",
            "Alliance": "1",
            "Conservative": "4",
            "Democratic Unionist Party": "7",
            "Green Party": "44",
            "Independent": "8",
            "Labour": "15",
            "Liberal Democrat": "17",
            "Plaid Cymru": "22",
            "Scottish National Party": "29",
            "Sinn Fein": "30", "Sinn Féin": "30",
            "Social Democratic & Labour Party": "31",
            "Speaker": "47",
        }
        self.__for_parliament = {
            "Current MPs": "0",
            "All MPs": "1", "All MPs - current and former": "1",
            "MPs At dissolution - November 2019": "2",
            "MPs during 2017-2019 Parliament": "3",
            "MPs during 2015-2017 Parliament": "4",
        }
        # todo Is this list extensive?
        self.__titles = {
            "Mr",
            "Dr",
            "Dame",
            "Sir",
            "Mrs",
            "Ms",
            "Miss",
        }
        self.mp_data = pd.DataFrame([], columns=["first_name", "last_name", "mp_detail_path"])

        self.last_updated = None

    def __fetch_all_overview_info_on_page(self, party_id, gender, for_parliament, page):
        page_query_string = urllib.parse.urlencode(
            OrderedDict(
                PartyId=party_id,
                Gender=gender,
                ForParliament=for_parliament,
                page=str(page),
            )
        )

        url = urllib.parse.urlunparse((
            self.__mp_overview_scheme, self.__mp_overview_netloc, "", "", page_query_string, ""
        ))

        html_data = urlopen(url)
        data_bs = BeautifulSoup(html_data.read(), 'html.parser')

        card_tags = data_bs.find_all(class_="card-member")

        names = self.__get_names_list_from_card_tags(card_tags)

        area = self.__get_area_list_from_card_tags(card_tags)

        party = self.__get_party_list_from_card_tags(card_tags)

        mp_data_paths = self.__get_mp_data_path_list_from_card_tags(card_tags)

        return names, party, area, mp_data_paths

    def __get_names_list_from_card_tags(self, card_tags):
        names = []
        for card in card_tags:
            name = card.find(class_="primary-info")
            names.append(self.__format_name(name.text))
        return names

    def __format_name(self, name: str):
        name = name.split(" ")
        name_dict = {
            "title": ""
        }
        if name[0] in self.__titles:
            name_dict["title"] = name[0]
            del name[0]

        name_dict["first_name"] = name[0]
        name_dict["last_name"] = " ".join(name[1:])
        return name_dict

    @staticmethod
    def __get_area_list_from_card_tags(card_tags):
        areas = []
        for card in card_tags:
            area = card.find(class_="indicator-label")
            areas.append(area.text)
        return areas

    @staticmethod
    def __get_party_list_from_card_tags(card_tags):
        parties = []
        for card in card_tags:
            party = card.find(class_="secondary-info")
            parties.append(party.text)
        return parties

    @staticmethod
    def __get_mp_data_path_list_from_card_tags(card_tags):
        mp_details_paths = []
        for card in card_tags:
            mp_data_path = card["href"]

            mp_details_paths.append(mp_data_path)

        return mp_details_paths
