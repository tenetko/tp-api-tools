import hashlib
import json
import os
from time import sleep

import requests
from dotenv import load_dotenv


class TPAviaSearchClient:
    HEADERS = {
        "Content-type": "application/json",
    }
    RESULTS_URL = (
        "http://api.travelpayouts.com/v1/flight_search_results?uuid={search_id}"
    )
    SEARCH_URL = "http://api.travelpayouts.com/v1/flight_search"

    def __init__(self, search_params: dict) -> None:
        load_dotenv()
        self.params = search_params
        self.params["tp_api_token"] = os.getenv("TP_API_TOKEN")
        self.params["tp_affiliate_marker"] = os.getenv("TP_AFFILIATE_MARKER")
        self.params["host"] = os.getenv("TP_HOST")

    def run(self) -> None:
        signature_string = self._make_signature_string(is_round_trip=True)
        signature_md5 = self._make_signature_md5(signature_string)

        response = self._make_request(signature_md5)
        search_id = self._get_search_id(response)

        print(f"Signature string:\t{signature_string}")
        print(f"Signature MD5:\t\t{signature_md5}")
        print(f"search_id:\t\t{search_id}")

        print("Waiting for 15 seconds...")
        sleep(15)

        results = self._get_search_results(search_id)

        self._save_results_to_file(results)

    def _make_signature_string(self, is_round_trip: bool) -> str:
        # PutYourTokenHere:beta.aviasales.ru:ru:PutYourMarkerHere:1:0:0:2015-05-25:LED:MOW:2015-06-18:MOW:LED:Y:127.0.0.1
        values = [
            self.params["tp_api_token"],
            self.params["currency"],
            self.params["host"],
            self.params["locale"],
            self.params["tp_affiliate_marker"],
            str(self.params["adults"]),
            str(self.params["children"]),
            str(self.params["infants"]),
            self.params["depart_date"],
            self.params["destination"],
            self.params["origin"],
        ]

        if is_round_trip:
            round_trip_values = [
                self.params["return_date"],
                self.params["origin"],
                self.params["destination"],
            ]
            values += round_trip_values

        values.append(self.params["trip_class"])
        values.append(self.params["ip"])

        signature = ":".join(values)

        return signature

    @staticmethod
    def _make_signature_md5(signature):
        return hashlib.md5(signature.encode()).hexdigest()

    def _make_request_data(self, signature_md5) -> dict:
        return {
            "signature": signature_md5,
            "marker": self.params["tp_affiliate_marker"],
            "host": self.params["host"],
            "user_ip": self.params["ip"],
            "locale": self.params["locale"],
            "trip_class": self.params["trip_class"],
            "passengers": {
                "adults": self.params["adults"],
                "children": self.params["children"],
                "infants": self.params["infants"],
            },
            "currency": self.params["currency"],
            "segments": [
                {
                    "origin": self.params["origin"],
                    "destination": self.params["destination"],
                    "date": self.params["depart_date"],
                },
                {
                    "origin": self.params["destination"],
                    "destination": self.params["origin"],
                    "date": self.params["return_date"],
                },
            ],
        }

    def _make_request(self, signature_md5: str) -> dict:
        data = self._make_request_data(signature_md5)
        response = requests.post(url=self.SEARCH_URL, headers=self.HEADERS, json=data)

        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")

        return response.json()

    def _get_search_id(self, response: dict) -> str:
        return response["search_id"]

    def _get_search_results(self, search_id: str) -> dict:
        response = requests.get(self.RESULTS_URL.format(search_id=search_id))

        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")

        return response.json()

    @staticmethod
    def _save_results_to_file(results: dict) -> None:
        with open("results.json", "w", encoding="utf-8") as output_file:
            output_file.write(json.dumps(results, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    search_params = {
        "ip": requests.get("https://4.ident.me").text,
        "locale": "en",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "origin": "MOW",
        "destination": "AER",
        "depart_date": "2025-06-05",
        "return_date": "2025-06-12",
        "trip_class": "Y",
        "currency": "RUB",
    }

    search = TPAviaSearchClient(search_params)
    search.run()
