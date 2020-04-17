import json
from os import path

import requests

import config


def main():
    MBTA_KEY = config.api_key
    URL = "https://api-v3.mbta.com/stops?api_key=" + MBTA_KEY
    stops = requests.get(URL).json()['data']
    with open("stops.json", "w") as outfile:
        json.dump(stops, outfile)


def get_stop_name(id):
    if not path.exists("stops.json"):
        main()
    with open("stops.json", "r") as stops_json:
        stops = json.load(stops_json)
        for stop in stops:
            if stop['id'] == id:
                return stop['attributes']['name']


def get_line(line):
    if not path.exists("stops.json"):
        main()
    with open("stops.json", "r") as stops_json:
        stops = json.load(stops_json)
        for stop in stops:
            if stop['id'] == id:
                return stop['attributes']['name']


if __name__ == '__main__':
    main()
