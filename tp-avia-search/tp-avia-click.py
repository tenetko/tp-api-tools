import json

import requests


class TPAviaClickClient:
    CLICK_URL = "http://api.travelpayouts.com/v1/flight_searches/{search_id}/clicks/{url_id}.json"
    PIXEL_URL = "http://yasen.aviasales.ru/adaptors/pixel_click.png?click_id={click_id}&gate_id={gate_id}"

    def __init__(self):
        pass

    def _get_deeplink(self, proposal: dict, search_id: str) -> str:
        gate_id = list(proposal["terms"].keys())[0]
        url_id = proposal["terms"][gate_id]["url"]
        ticket_link = self.CLICK_URL.format(search_id=search_id, url_id=url_id)
        print(f"Ticket link:\t{ticket_link}")

        response = requests.get(ticket_link)
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")

        click_id = response.json()["click_id"]
        deeplink_url = str(response.json()["url"])

        print(f"Deeplink:\t{deeplink_url}")
        print(f"click_id:\t{click_id}")

        pixel_url = self.PIXEL_URL.format(click_id=click_id, gate_id=gate_id)
        with open("ticket_link.html", "w", encoding="utf-8") as wfile:
            wfile.write(
                f"""
<!doctype html>
<html lang=en>
    <head>
        <meta charset=utf-8>
        <title>Ticket</title>
    </head>
    <body>
        <img width="0" height="0" id="pixel" src="{pixel_url}"><a href={deeplink_url}>Ticket Link</a>
    </body>
</html>
"""
            )


if __name__ == "__main__":
    client = TPAviaClickClient()
    search_id = "c73e5180-c4a4-4936-a216-65ccf4146800"

    proposal = {}
    with open("proposal.json", "r", encoding="utf-8") as input_file:
        proposal = json.load(input_file)

    click = client._get_deeplink(proposal, search_id)
