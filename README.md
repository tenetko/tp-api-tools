# tp-api-tools

## Avia search
* install dependecies:
```
pip install requests dotenv
```
* rename `.env-template` into `.env` and fill in the required values;
* run:
```
python ./tp-avia-search/tp-avia-search.py
```
* as a result, you will have the `proposals.json` file with the API response.

## Avia deeplink:
* copy a proposal from avia search results into the `proposal.json` file;
* specify the search_id from the search results in the `./tp-avia-search/tp-avia-click.py` file;
* run:
```
python ./tp-avia-search/tp-avia-click.py
```
* as a result, you will have the `ticket_link.html` file with the tracking pixel URL and deeplink URL.