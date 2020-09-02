#!/usr/bin/python

import os
import sys
import json
import collections
import requests
from hashlib import md5
from time import sleep


class HotelsSearcher:
    def __init__(self) -> None:
        self.config = self.get_config()
        self.config["customer_ip"] = self.get_ip_address()
        self.request_file = "request.txt"
        self.response_file = "response.json"
        self.search_params = {}
        self.search_id = ""
        self.response = ""

    def get_config(self) -> None:
        config = {}
        try:
            with open("config.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        except OSError as e:
            print("Failed to open file {}.".format(e.filename))
        if "iata" in config:
            config["location"] = "iata"
        elif "city_id" in config:
            config["location"] = "city_id"
        elif "hotel_id" in config:
            config["location"] = "hotel_id"
        else:
            print("You should specify the location type: iata, city_id, or hotel_id.")
            sys.exit()

        return config

    def get_ip_address(self) -> str:
        try:
            ip_address = requests.get("https://ident.me").content.decode("utf8")
        except:
            ip_address = "192.168.1.1"

        return ip_address

    def get_init_signature(self) -> str:
        signature_params_values = self.get_init_signature_params()
        init_signature_string = "{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}:{8}:{9}:{10}:{11}".format(
            self.config["token"], self.config["marker"], *signature_params_values
        )
        init_signature_string_md5 = md5(init_signature_string.encode()).hexdigest()
        self.search_params["init_signature_string"] = init_signature_string
        self.search_params["init_signature_md5"] = init_signature_string_md5

        return init_signature_string_md5

    def get_init_signature_params(self) -> list:
        signature_params_values = []
        signature_params = [
            "lang",
            "currency",
            "wait_for_results",
            "check_in",
            "check_out",
            "adults_count",
            "children_count",
            "child_age",
            "customer_ip",
            self.config["location"],
        ]
        for param in sorted(signature_params):
            signature_params_values.append(self.config[param])

        return signature_params_values

    def get_init_url(self) -> None:
        signature = self.get_init_signature()
        location_types_map = {
            "iata": "iata",
            "city_id": "cityId",
            "hotel_id": "hotelId",
        }
        init_url = "http://engine.hotellook.com/api/v2/search/start.json?{0}={1}&checkIn={check_in}&checkOut={check_out}&adultsCount={adults_count}&customerIP={customer_ip}&lang={lang}&currency={currency}&waitForResult={wait_for_results}&marker={marker}&signature={2}&childrenCount={children_count}&childAge1={child_age}".format(
            location_types_map[self.config["location"]],
            self.config[self.config["location"]],
            signature,
            **self.config
        )
        self.search_params["init_url"] = init_url

        return init_url

    def initialize_search(self) -> None:
        url = self.get_init_url()
        response = requests.get(url).json()
        self.search_params["init_response"] = response
        if response["status"] != "ok":
            print("Error message:\t\t{0}\n".format(response["message"]))
            self.dump_request()
            sys.exit()

        self.search_id = response["searchId"]

    def get_results_signature(self) -> dict:
        results_signature_params = self.get_results_signature_params()
        results_signature_string = "{0}:{1}:{limit}:{offset}:{rooms_count}:{search_id}:{sort_asc}:{sort_by}".format(
            self.config["token"], self.config["marker"], **results_signature_params
        )
        results_signature_md5 = md5(results_signature_string.encode()).hexdigest()

        self.search_params["results_signature_string"] = results_signature_string
        self.search_params["results_signature_md5"] = results_signature_md5

        return results_signature_md5

    def get_results_signature_params(self) -> dict:
        results_params = {}
        search_id = self.search_id
        results_params["limit"] = "0"
        results_params["offset"] = "0"
        results_params["rooms_count"] = "0"
        results_params["search_id"] = search_id
        results_params["sort_asc"] = "1"
        results_params["sort_by"] = "price"

        return results_params

    def get_results_url(self) -> str:
        signature = self.get_results_signature()
        results_params = self.get_results_signature_params()
        results_url = "http://engine.hotellook.com/api/v2/search/getResult.json?searchId={search_id}&limit={limit}&sortBy={sort_by}&sortAsc={sort_asc}&roomsCount={rooms_count}&offset={offset}&marker={0}&signature={1}".format(
            self.config["marker"], signature, **results_params
        )
        self.search_params["results_url"] = results_url

        return results_url

    def get_results(self) -> None:
        url = self.get_results_url()
        self.response = requests.get(url).json()
        self.search_params["results_response_status"] = self.response["status"]
        if self.response["status"] != "ok":
            print("Error message:\t\t{0}\n".format(self.response["message"]))
            self.dump_request()
            sys.exit()

    def dump_response(self) -> None:
        try:
            with open(self.response_file, "w", encoding="utf-8") as response_file:
                json.dump(self.response["result"], response_file, indent=4)
        except OSError as e:
            print("Failed to open file {}.".format(e.filename))

    def dump_request(self) -> None:
        try:
            with open(self.request_file, "w", encoding="utf-8") as request_file:
                request_file.write(
                    "Initialization signature string:\n{}\n\n".format(
                        self.search_params["init_signature_string"]
                    )
                )
                request_file.write(
                    "Initialization signature MD5:\n{}\n\n".format(
                        self.search_params["init_signature_md5"]
                    )
                )
                request_file.write(
                    "Initialization request:\n{}\n\n".format(
                        self.search_params["init_url"]
                    )
                )
                request_file.write(
                    "Initialization response:\n{}\n\n".format(
                        self.search_params["init_response"]
                    )
                )
                request_file.write("======================\n\n")
                request_file.write(
                    "Results signature string:\n{}\n\n".format(
                        self.search_params["results_signature_string"]
                    )
                )
                request_file.write(
                    "Results signature MD5:\n{}\n\n".format(
                        self.search_params["results_signature_md5"]
                    )
                )
                request_file.write(
                    "Results request:\n{}\n\n".format(self.search_params["results_url"])
                )
                request_file.write(
                    "Results response status:\n{}\n\n".format(
                        self.search_params["results_response_status"]
                    )
                )

        except OSError as e:
            print("Failed to open file {}.".format(e.filename))
            sys.exit()

    def display_progress(self) -> None:
        for _ in range(int(self.config["sleep"])):
            sleep(1)
            print(".", end="")
            sys.stdout.flush()

    def __call__(self) -> None:
        self.initialize_search()
        self.display_progress()
        self.get_results()
        self.dump_request()
        self.dump_response()


if __name__ == "__main__":
    search = HotelsSearcher()
    search()
