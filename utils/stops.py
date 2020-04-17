import json
from os import path

import requests

import config


def main():
    MBTA_KEY = config.api_key
    URL = "https://api-v3.mbta.com/stops?api_key=" + MBTA_KEY
    stops = requests.get(URL).json()['data']
    stops_optimized = dict()
    for stop in stops:
        stops_optimized[stop['id']] = stop['attributes']['name']
    with open("stops.json", "w") as outfile:
        json.dump(stops_optimized, outfile)

def get_stop_name(id):
    if not path.exists("stops.json"):
        main()
    with open("stops.json", "r") as stops_json:
        stops = json.load(stops_json)
        return stops[id]

if __name__ == '__main__':
    main()
